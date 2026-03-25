# AI Hero Project

Implementation track for the AI Hero crash course.

## Day 1

GitHub repository document ingestion.

### Features

- downloads a GitHub repository as a zip archive
- processes files fully in memory
- parses `.md` and `.mdx` files
- extracts frontmatter metadata when present
- keeps raw content for later chunking and indexing
- supports configurable repo owner, repo name, and branch
- supports docs-only filtering
- provides CLI modes for:
  - counts
  - preview
  - full JSON

### Current example

- repo: `dlt-hub/dlt`
- branch: `devel`

### Next

Day 2: chunk large documents into smaller sections for retrieval.
