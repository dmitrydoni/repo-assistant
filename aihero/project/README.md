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
- can save processed repository data to disk

### Current example

- repo: `dlt-hub/dlt`
- branch: `devel`

### Day 1 outputs

- raw processed documents: `_data/repository_data.json`

### Day 1 commands

- `j counts`
- `j preview`
- `j preview 2`
- `j save`

## Day 2

Chunk large documents into smaller retrieval-friendly units.

### Implemented chunking strategies

- sliding-window chunking with overlap
- markdown section chunking by header level

### Features

- loads processed repository data from Day 1
- creates chunk records while preserving source document metadata
- supports chunk counts
- supports chunk preview
- supports full JSON output
- saves chunked outputs to disk

### Day 2 outputs

- sliding-window chunks: `_data/repository_chunks_sliding.json`
- section-based chunks: `_data/repository_chunks_sections.json`

### Day 2 commands

- `j chunk-sliding`
- `j chunk-preview`
- `j chunk-preview 2`
- `j chunk-sections`
- `j chunk-sections-preview`
- `j chunk-sections-preview 2`

## Day 3

Add search over the prepared repository chunks.

### Implemented search strategies

- lexical text search
- vector search with embeddings
- hybrid search combining text and vector results

### Features

- loads chunked repository data from Day 2
- supports exact-match and keyword-oriented retrieval
- supports semantic retrieval with embeddings
- supports hybrid retrieval with deduplication
- provides preview and full JSON output modes

### Day 3 input

- sliding-window chunks: `_data/repository_chunks_sliding.json`

### Day 3 commands

- `j search-text`
- `j search-text-q "your query"`
- `j search-vector`
- `j search-vector-q "your query"`
- `j search-hybrid`
- `j search-hybrid-q "your query"`

## Day 4

Build a repository Q&A agent on top of search.

### Features

- uses Pydantic AI for agent orchestration
- exposes repository search as a tool: `search_repo`
- answers questions based on repository search results
- uses the prepared sliding-window chunks as agent input

### Day 4 input

- `_data/repository_chunks_sliding.json`

### Day 4 commands

- `j agent-q`
- `j agent-q-custom "your question"`

## Day 5

Evaluate the repository agent systematically.

### Features

- logs agent interactions to `logs/`
- evaluates saved logs with an LLM judge
- supports single-log and batch evaluation
- generates evaluation questions from repository chunks
- runs generated questions through the agent automatically
- saves detailed evaluation results for later comparison

### Day 5 artefacts

- interaction logs: `logs/*.json`
- question generation: `aihero/project/src/generate_eval_questions.py`
- evaluation: `aihero/project/src/evaluate_agent_logs.py`
- generated questions: `_data/eval_questions.json`
- generated run results: `_data/eval_runs.json`
- saved evaluation baseline: `_data/eval_results_ai_generated.json`

### Day 5 commands

- `j eval-log`
- `j eval-log-file logs/<file>.json`
- `j eval-logs`
- `j eval-logs-ai`
- `j eval-logs-ai-save`
- `j eval-generate-questions`
- `j eval-run-questions`

## Current status

- Day 1 complete
- Day 2 complete
- Day 3 complete
- Day 4 complete
- Day 5 complete

## Next

Day 6: build a UI for the agent and prepare it for deployment.

