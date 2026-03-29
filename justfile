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

eval_script := "aihero/project/src/evaluate_agent_logs.py"
eval_model := "openai:gpt-5.4-mini"
eval_log_file := "logs/agent_20260329_173105_0cb000.json"
eval_log_dir := "logs"

eval_questions_script := "aihero/project/src/generate_eval_questions.py"
eval_questions_output := "_data/eval_questions.json"
eval_questions_input := "_data/repository_chunks_sliding.json"
eval_questions_model := "openai:gpt-5.4-mini"
eval_questions_sample_size := "10"
eval_questions_seed := "47"

eval_runs_script := "aihero/project/src/run_eval_questions.py"
eval_runs_output := "_data/eval_runs.json"
eval_results_output := "_data/eval_results_ai_generated.json"

app_script := "aihero/project/src/app_streamlit.py"

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

# Evaluate the default saved agent interaction log.
eval-log:
	uv run --project . python {{eval_script}} \
	  --log-file {{eval_log_file}} \
	  --model {{eval_model}}

# Evaluate a specific saved agent interaction log.
eval-log-file log_file:
	uv run --project . python {{eval_script}} \
	  --log-file {{log_file}} \
	  --model {{eval_model}}

# Evaluate all saved agent interaction logs in the logs directory.
eval-logs:
	uv run --project . python {{eval_script}} \
	  --log-dir {{eval_log_dir}} \
	  --model {{eval_model}}

# Generate evaluation questions from sampled repository chunks.
eval-generate-questions:
	uv run --project . python {{eval_questions_script}} \
	  --input {{eval_questions_input}} \
	  --output {{eval_questions_output}} \
	  --model {{eval_questions_model}} \
	  --sample-size {{eval_questions_sample_size}} \
	  --seed {{eval_questions_seed}}

# Run generated evaluation questions through the agent and save run results.
eval-run-questions:
	uv run --project . python {{eval_runs_script}} \
	  --agent-input {{agent_input}} \
	  --questions-file {{eval_questions_output}} \
	  --output {{eval_runs_output}}

# Evaluate only AI-generated agent interaction logs.
eval-logs-ai:
	uv run --project . python {{eval_script}} \
	  --log-dir {{eval_log_dir}} \
	  --source ai-generated \
	  --model {{eval_model}}

# Evaluate only AI-generated logs and save detailed results.
eval-logs-ai-save:
	uv run --project . python {{eval_script}} \
	  --log-dir {{eval_log_dir}} \
	  --source ai-generated \
	  --model {{eval_model}} \
	  --output {{eval_results_output}}

# Run the local Streamlit app.
app:
	uv run --project . streamlit run {{app_script}}

