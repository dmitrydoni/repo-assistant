import argparse
import json
from pathlib import Path
from typing import Any
import re


def load_json(input_path: str) -> list[dict[str, Any]]:
    """Load repository data from a JSON file."""
    path = Path(input_path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: list[dict[str, Any]], output_path: str) -> None:
    """Save chunked repository data to a JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def sliding_window(text: str, size: int, step: int) -> list[dict[str, Any]]:
    """Split text into overlapping character-based chunks."""
    if size <= 0 or step <= 0:
        raise ValueError("size and step must be positive")

    chunks: list[dict[str, Any]] = []
    text_length = len(text)

    for start in range(0, text_length, step):
        chunk_text = text[start : start + size]
        chunks.append(
            {
                "chunk_index": len(chunks),
                "start": start,
                "end": min(start + size, text_length),
                "chunk_text": chunk_text,
            }
        )

        if start + size >= text_length:
            break

    return chunks


def chunk_docs_sliding(
    docs: list[dict[str, Any]],
    size: int,
    step: int,
) -> list[dict[str, Any]]:
    """Create sliding-window chunks for all documents."""
    chunked_docs: list[dict[str, Any]] = []

    for doc in docs:
        doc_copy = doc.copy()
        content = doc_copy.pop("content", "") or ""

        if not content.strip():
            continue

        chunks = sliding_window(content, size=size, step=step)

        for chunk in chunks:
            chunk_record = doc_copy.copy()
            chunk_record.update(chunk)
            chunked_docs.append(chunk_record)

    return chunked_docs


def summarize_chunks(chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a small summary of chunked documents."""
    source_files = {chunk.get("filename") for chunk in chunks if chunk.get("filename")}

    return {
        "chunks_total": len(chunks),
        "source_documents": len(source_files),
    }


def preview_chunks(
    chunks: list[dict[str, Any]],
    limit: int = 3,
    content_chars: int = 300,
) -> list[dict[str, Any]]:
    """Return a lightweight preview of chunked records."""
    preview: list[dict[str, Any]] = []

    for chunk in chunks[:limit]:
        preview.append(
            {
                "filename": chunk.get("filename"),
                "chunk_index": chunk.get("chunk_index"),
                "section_index": chunk.get("section_index"),
                "section_header": chunk.get("section_header"),
                "start": chunk.get("start"),
                "end": chunk.get("end"),
                "chunk_text_preview": (chunk.get("chunk_text") or "")[:content_chars],
            }
        )

    return preview


def split_markdown_by_level(text: str, level: int = 2) -> list[dict[str, Any]]:
    """Split markdown text by a specific header level."""
    header_pattern = r"^(#{"+ str(level) + r"} )(.+)$"
    pattern = re.compile(header_pattern, re.MULTILINE)

    parts = pattern.split(text)
    sections: list[dict[str, Any]] = []

    for i in range(1, len(parts), 3):
        header_prefix = parts[i]
        header_text = parts[i + 1]
        header = f"{header_prefix}{header_text}".strip()

        content = ""
        if i + 2 < len(parts):
            content = parts[i + 2].strip()

        section_text = f"{header}\n\n{content}".strip() if content else header

        sections.append(
            {
                "section_index": len(sections),
                "section_header": header,
                "chunk_text": section_text,
            }
        )

    return sections


def chunk_docs_sections(
    docs: list[dict[str, Any]],
    level: int,
) -> list[dict[str, Any]]:
    """Create section-based chunks for all documents."""
    chunked_docs: list[dict[str, Any]] = []

    for doc in docs:
        doc_copy = doc.copy()
        content = doc_copy.pop("content", "") or ""

        if not content.strip():
            continue

        sections = split_markdown_by_level(content, level=level)

        if not sections:
            chunked_docs.append(
                {
                    **doc_copy,
                    "section_index": 0,
                    "section_header": None,
                    "chunk_text": content,
                }
            )
            continue

        for section in sections:
            chunk_record = doc_copy.copy()
            chunk_record.update(section)
            chunked_docs.append(chunk_record)

    return chunked_docs


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunk repository documents into smaller pieces.")
    parser.add_argument("--input", required=True, help="Input JSON path from Day 1")
    parser.add_argument("--output", default=None, help="Optional output JSON path")
    parser.add_argument("--strategy", choices=["sliding", "sections"], default="sliding")
    parser.add_argument("--mode", choices=["counts", "preview", "json"], default="counts")
    parser.add_argument("--level", type=int, default=2, help="Markdown header level for section chunking")
    parser.add_argument("--limit", type=int, default=3, help="Number of preview items")
    parser.add_argument("--size", type=int, default=2000, help="Chunk size in characters")
    parser.add_argument("--step", type=int, default=1000, help="Chunk step in characters")
    args = parser.parse_args()

    docs = load_json(args.input)

    if args.strategy == "sliding":
        chunks = chunk_docs_sliding(docs, size=args.size, step=args.step)
    else:
        chunks = chunk_docs_sections(docs, level=args.level)

    if args.output:
        save_json(chunks, args.output)

    if args.mode == "counts":
        print(json.dumps(summarize_chunks(chunks), indent=2, ensure_ascii=False))
    elif args.mode == "preview":
        print(json.dumps(preview_chunks(chunks, limit=args.limit), indent=2, ensure_ascii=False))
    else:
        print(json.dumps(chunks, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

