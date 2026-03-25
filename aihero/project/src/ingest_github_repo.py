import argparse
import io
import json
import zipfile
from typing import Any

import frontmatter
import requests


def guess_default_branch(repo_owner: str, repo_name: str) -> str:
    """Guess the default branch by trying common branch names."""
    branches_to_try = ["main", "master", "devel", "develop"]

    for branch in branches_to_try:
        url = f"https://codeload.github.com/{repo_owner}/{repo_name}/zip/refs/heads/{branch}"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return branch

    raise RuntimeError(
        f"Could not find a downloadable branch for {repo_owner}/{repo_name}. "
        f"Tried: {', '.join(branches_to_try)}"
    )


def should_keep_file(
    filename: str,
    include_extensions: tuple[str, ...] = (".md", ".mdx"),
    docs_only: bool = False,
) -> bool:
    """Return True if the file should be processed."""
    filename_lower = filename.lower()

    if not filename_lower.endswith(include_extensions):
        return False

    if not docs_only:
        return True

    return (
        "/docs/" in filename_lower
        or filename_lower.endswith("/readme.md")
        or filename_lower.endswith("readme.md")
    )


def parse_frontmatter_content(content: str) -> dict[str, Any]:
    """Parse markdown/mdx content and return metadata + content."""
    post = frontmatter.loads(content)
    return post.to_dict()


def read_repo_data(
    repo_owner: str,
    repo_name: str,
    branch: str | None = None,
    docs_only: bool = False,
) -> list[dict[str, Any]]:
    """Download and parse markdown files from a GitHub repository zip archive."""
    resolved_branch = branch or guess_default_branch(repo_owner, repo_name)
    url = f"https://codeload.github.com/{repo_owner}/{repo_name}/zip/refs/heads/{resolved_branch}"

    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    repository_data: list[dict[str, Any]] = []

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        for file_info in zf.infolist():
            filename = file_info.filename

            if not should_keep_file(filename=filename, docs_only=docs_only):
                continue

            try:
                with zf.open(file_info) as f_in:
                    content = f_in.read().decode("utf-8", errors="ignore")
                    data = parse_frontmatter_content(content)
                    data["filename"] = filename
                    data["repo_owner"] = repo_owner
                    data["repo_name"] = repo_name
                    data["branch"] = resolved_branch
                    repository_data.append(data)
            except Exception as e:
                print(f"Skipping {filename}: {e}")

    return repository_data


def summarize_docs(docs: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a small summary of processed documents."""
    with_content = sum(1 for doc in docs if doc.get("content"))
    with_title = sum(1 for doc in docs if doc.get("title"))

    extensions: dict[str, int] = {}
    for doc in docs:
        filename = doc.get("filename", "")
        ext = "." + filename.lower().split(".")[-1] if "." in filename else "<none>"
        extensions[ext] = extensions.get(ext, 0) + 1

    return {
        "documents_total": len(docs),
        "documents_with_content": with_content,
        "documents_with_title": with_title,
        "extensions": dict(sorted(extensions.items())),
    }


def preview_docs(docs: list[dict[str, Any]], limit: int = 3, content_chars: int = 300) -> list[dict[str, Any]]:
    """Return a lightweight preview of processed documents."""
    preview = []

    for doc in docs[:limit]:
        item = {
            "filename": doc.get("filename"),
            "title": doc.get("title"),
            "keys": sorted(doc.keys()),
            "content_preview": (doc.get("content") or "")[:content_chars],
        }
        preview.append(item)

    return preview


def save_json(data: list[dict[str, Any]], output_path: str) -> None:
    """Save processed repository data to a JSON file."""
    import json
    from pathlib import Path

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and parse markdown docs from a GitHub repo.")
    parser.add_argument("--repo-owner", required=True, help="GitHub org/user name")
    parser.add_argument("--repo-name", required=True, help="GitHub repository name")
    parser.add_argument("--branch", default=None, help="Branch name; if omitted, try common defaults")
    parser.add_argument("--docs-only", action="store_true", help="Keep only docs/ and README markdown files")
    parser.add_argument(
        "--mode",
        choices=["counts", "preview", "json"],
        default="counts",
        help="Output mode",
    )
    parser.add_argument("--limit", type=int, default=3, help="Number of preview items")
    parser.add_argument("--output", default=None, help="Optional output JSON path")
    args = parser.parse_args()

    docs = read_repo_data(
        repo_owner=args.repo_owner,
        repo_name=args.repo_name,
        branch=args.branch,
        docs_only=args.docs_only,
    )

    if args.output:
        save_json(docs, args.output)

    if args.mode == "counts":
        print(json.dumps(summarize_docs(docs), indent=2, ensure_ascii=False))
    elif args.mode == "preview":
        print(json.dumps(preview_docs(docs, limit=args.limit), indent=2, ensure_ascii=False))
    else:
        print(json.dumps(docs, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

