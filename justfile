set shell := ["bash", "-cu"]

repo_owner := "AltimateAI"
repo_name := "altimate-code"
branch := "main"

script := "aihero/project/src/ingest_github_repo.py"
output := "_data/repository_data.json"

input_data := "_data/repository_data.json"
chunks_sliding := "_data/repository_chunks_sliding.json"
chunks_sections := "_data/repository_chunks_sections.json"
chunk_script := "aihero/project/src/chunk_repository_data.py"

search_input := "_data/repository_chunks_sliding.json"
search_script := "aihero/project/src/search_repository_data.py"
search_query := "How do I install Altimate?"
search_model := "multi-qa-distilbert-cos-v1"

agent_input := "_data/repository_chunks_sliding.json"
agent_script := "aihero/project/src/agent_repository_qa.py"
agent_question := "How do I install Altimate Code?"

###
### Project info
###

# This menu
help:
	@echo "=========================================="
	@echo "Welcome!"
	@echo "------------------------------------------"
	@just --list
	@echo "=========================================="

# Repo structure
tree:
	@echo "------------------------------------------"
	@echo "Repo structure"
	@echo "------------------------------------------"
	@tree -a -I '.git|.venv|__pycache__|*.pyc|_data|.dlt/secrets.toml|.ruff_cache|__marimo__' -L 4

###
### Operations
###

# Show summary counts for processed markdown docs.
counts:
	uv run --project . python {{script}} \
	  --repo-owner {{repo_owner}} \
	  --repo-name {{repo_name}} \
	  --branch {{branch}} \
	  --docs-only \
	  --mode counts

# Preview a few processed records.
preview limit="5":
	uv run --project . python {{script}} \
	  --repo-owner {{repo_owner}} \
	  --repo-name {{repo_name}} \
	  --branch {{branch}} \
	  --docs-only \
	  --mode preview \
	  --limit {{limit}}

# Full JSON output for debugging.
json:
	uv run --project . python {{script}} \
	  --repo-owner {{repo_owner}} \
	  --repo-name {{repo_name}} \
	  --branch {{branch}} \
	  --docs-only \
	  --mode json

# Save processed repository data to disk and show summary counts.
save:
	uv run --project . python {{script}} \
	  --repo-owner {{repo_owner}} \
	  --repo-name {{repo_name}} \
	  --branch {{branch}} \
	  --docs-only \
	  --mode counts \
	  --output {{output}}

# Preview saved repository data file path.
where:
	@echo {{output}}

# Create sliding-window chunks and save them to disk.
chunk-sliding:
	uv run --project . python {{chunk_script}} \
	  --input {{input_data}} \
	  --output {{chunks_sliding}} \
	  --strategy sliding \
	  --mode counts

# Preview a few sliding-window chunks.
chunk-preview limit="5":
	uv run --project . python {{chunk_script}} \
	  --input {{input_data}} \
	  --strategy sliding \
	  --mode preview \
	  --limit {{limit}}

# Show full JSON sliding chunk output.
chunk-json:
	uv run --project . python {{chunk_script}} \
	  --input {{input_data}} \
	  --strategy sliding \
	  --mode json

# Show saved sliding chunk output path.
chunk-where:
	@echo {{chunks_sliding}}

# Create section-based chunks and save them to disk.
chunk-sections:
	uv run --project . python {{chunk_script}} \
	  --input {{input_data}} \
	  --output {{chunks_sections}} \
	  --strategy sections \
	  --level 2 \
	  --mode counts

# Preview a few section-based chunks.
chunk-sections-preview limit="5":
	uv run --project . python {{chunk_script}} \
	  --input {{input_data}} \
	  --strategy sections \
	  --level 2 \
	  --mode preview \
	  --limit {{limit}}

# Show full JSON section chunk output.
chunk-sections-json:
	uv run --project . python {{chunk_script}} \
	  --input {{input_data}} \
	  --strategy sections \
	  --level 2 \
	  --mode json

# Show saved section chunk output path.
chunk-sections-where:
	@echo {{chunks_sections}}

# Run a default lexical search query against sliding-window chunks.
search-text:
	uv run --project . python {{search_script}} \
	  --input {{search_input}} \
	  --query "{{search_query}}" \
	  --limit 5 \
	  --mode preview

# Run a custom lexical search query against sliding-window chunks.
search-text-q query:
	uv run --project . python {{search_script}} \
	  --input {{search_input}} \
	  --query "{{query}}" \
	  --limit 5 \
	  --mode preview

# Show full JSON results for the default lexical search query.
search-text-json:
	uv run --project . python {{search_script}} \
	  --input {{search_input}} \
	  --query "{{search_query}}" \
	  --limit 5 \
	  --mode json

# Run a default vector search query against sliding-window chunks.
search-vector:
	uv run --project . python {{search_script}} \
	  --input {{search_input}} \
	  --query "{{search_query}}" \
	  --strategy vector \
	  --model {{search_model}} \
	  --limit 5 \
	  --mode preview

# Run a custom vector search query against sliding-window chunks.
search-vector-q query:
	uv run --project . python {{search_script}} \
	  --input {{search_input}} \
	  --query "{{query}}" \
	  --strategy vector \
	  --model {{search_model}} \
	  --limit 5 \
	  --mode preview

# Show full JSON results for the default vector search query.
search-vector-json:
	uv run --project . python {{search_script}} \
	  --input {{search_input}} \
	  --query "{{search_query}}" \
	  --strategy vector \
	  --model {{search_model}} \
	  --limit 5 \
	  --mode json

# Run a default hybrid search query against sliding-window chunks.
search-hybrid:
	uv run --project . python {{search_script}} \
	  --input {{search_input}} \
	  --query "{{search_query}}" \
	  --strategy hybrid \
	  --model {{search_model}} \
	  --limit 5 \
	  --mode preview

# Run a custom hybrid search query against sliding-window chunks.
search-hybrid-q query:
	uv run --project . python {{search_script}} \
	  --input {{search_input}} \
	  --query "{{query}}" \
	  --strategy hybrid \
	  --model {{search_model}} \
	  --limit 5 \
	  --mode preview

# Show full JSON results for the default hybrid search query.
search-hybrid-json:
	uv run --project . python {{search_script}} \
	  --input {{search_input}} \
	  --query "{{search_query}}" \
	  --strategy hybrid \
	  --model {{search_model}} \
	  --limit 5 \
	  --mode json

# Ask the repository agent a default question.
agent-q:
	uv run --project . python {{agent_script}} \
	  --input {{agent_input}} \
	  --question "{{agent_question}}"

# Ask the repository agent a custom question.
agent-q-custom question:
	uv run --project . python {{agent_script}} \
	  --input {{agent_input}} \
	  --question "{{question}}"

