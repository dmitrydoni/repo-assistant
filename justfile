set shell := ["bash", "-cu"]

repo_owner := "dlt-hub"
repo_name := "dlt"
branch := "devel"
script := "aihero/project/src/ingest_github_repo.py"
output := "_data/repository_data.json"

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

