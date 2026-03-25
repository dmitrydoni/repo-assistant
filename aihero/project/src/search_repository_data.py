import argparse
import json
from pathlib import Path
from typing import Any

from minsearch import Index
from sentence_transformers import SentenceTransformer


def load_json(input_path: str) -> list[dict[str, Any]]:
    """Load chunked repository data from a JSON file."""
    path = Path(input_path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_text_index(records: list[dict[str, Any]]) -> Index:
    """Build a lexical search index over chunked repository records."""
    index = Index(
        text_fields=["chunk_text", "title", "description", "filename"],
        keyword_fields=[],
    )
    index.fit(records)
    return index


def search_text(index: Index, query: str, num_results: int = 5) -> list[dict[str, Any]]:
    """Run lexical search against the in-memory index."""
    return index.search(query, num_results=num_results)


def load_embedding_model(model_name: str) -> SentenceTransformer:
    """Load a sentence-transformers embedding model."""
    return SentenceTransformer(model_name)


def build_vector_index(
    records: list[dict[str, Any]],
    model: SentenceTransformer,
) -> list[dict[str, Any]]:
    """Attach document embeddings to records for vector search."""
    indexed_records: list[dict[str, Any]] = []

    for record in records:
        chunk_text = record.get("chunk_text") or ""
        embedding = model.encode_document(chunk_text)

        indexed_record = record.copy()
        indexed_record["_embedding"] = embedding
        indexed_records.append(indexed_record)

    return indexed_records


def search_vector(
    indexed_records: list[dict[str, Any]],
    model: SentenceTransformer,
    query: str,
    num_results: int = 5,
) -> list[dict[str, Any]]:
    """Run vector search using dot-product similarity."""
    query_embedding = model.encode_query(query)

    scored_results: list[dict[str, Any]] = []
    for record in indexed_records:
        score = float(query_embedding.dot(record["_embedding"]))
        scored_record = record.copy()
        scored_record["_score"] = score
        scored_results.append(scored_record)

    scored_results.sort(key=lambda x: x["_score"], reverse=True)
    return scored_results[:num_results]


def preview_results(results: list[dict[str, Any]], content_chars: int = 300) -> list[dict[str, Any]]:
    """Return a compact preview of search results."""
    preview: list[dict[str, Any]] = []

    for result in results:
        preview.append(
            {
                "filename": result.get("filename"),
                "title": result.get("title"),
                "section_header": result.get("section_header"),
                "chunk_index": result.get("chunk_index"),
                "section_index": result.get("section_index"),
                "score": result.get("_score"),
                "chunk_text_preview": (result.get("chunk_text") or "")[:content_chars],
            }
        )

    return preview


def hybrid_search(
    text_results: list[dict[str, Any]],
    vector_results: list[dict[str, Any]],
    num_results: int = 5,
) -> list[dict[str, Any]]:
    """Combine and deduplicate text and vector search results."""
    combined_results: list[dict[str, Any]] = []
    seen_keys: set[tuple[Any, Any, Any]] = set()

    for result in text_results + vector_results:
        key = (
            result.get("filename"),
            result.get("chunk_index"),
            result.get("section_index"),
        )
        if key in seen_keys:
            continue

        seen_keys.add(key)
        combined_results.append(result)

        if len(combined_results) >= num_results:
            break

    return combined_results


def main() -> None:
    parser = argparse.ArgumentParser(description="Search chunked repository data.")
    parser.add_argument("--input", required=True, help="Input chunk JSON path")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--limit", type=int, default=5, help="Number of search results")
    parser.add_argument(
        "--strategy",
        choices=["text", "vector", "hybrid"],
        default="text",
        help="Search strategy",
    )
    parser.add_argument(
        "--model",
        default="multi-qa-distilbert-cos-v1",
        help="Sentence-transformers model name for vector search",
    )
    parser.add_argument(
        "--mode",
        choices=["preview", "json"],
        default="preview",
        help="Output mode",
    )
    args = parser.parse_args()

    records = load_json(args.input)

    if args.strategy == "text":
        index = build_text_index(records)
        results = search_text(index, query=args.query, num_results=args.limit)

    elif args.strategy == "vector":
        model = load_embedding_model(args.model)
        indexed_records = build_vector_index(records, model)
        results = search_vector(indexed_records, model, query=args.query, num_results=args.limit)

    else:
        index = build_text_index(records)
        text_results = search_text(index, query=args.query, num_results=args.limit)

        model = load_embedding_model(args.model)
        indexed_records = build_vector_index(records, model)
        vector_results = search_vector(indexed_records, model, query=args.query, num_results=args.limit)

        results = hybrid_search(text_results, vector_results, num_results=args.limit)

    if args.mode == "preview":
        print(json.dumps(preview_results(results), indent=2, ensure_ascii=False))
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

