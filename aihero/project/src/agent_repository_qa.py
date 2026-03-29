import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from minsearch import Index
from pydantic_ai import Agent

from logs import log_interaction_to_file


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


SYSTEM_PROMPT = """
You are a helpful repository assistant.

Always use the search_repo tool before answering questions about the repository.
Base your answer on the returned search results.
If the search results are not sufficient, say that clearly and give the best partial answer you can.

Be concise, practical, and specific.
""".strip()


def build_agent(index: Index) -> Agent:
    """Create the repository QA agent with a search tool."""
    agent = Agent(
        name="repo_agent",
        model="openai:gpt-5.4-nano",
        instructions=SYSTEM_PROMPT,
    )

    @agent.tool_plain
    def search_repo(query: str) -> list[dict[str, Any]]:
        """Search the repository documentation for relevant information.

        Args:
            query: Search query to look up in the repository documentation.

        Returns:
            A list of up to 5 relevant search results.
        """
        return search_text(index, query=query, num_results=5)

    return agent


async def run_agent(input_path: str, question: str, source: str = "user") -> tuple[str, Path]:
    """Run the repository QA agent for a single user question and save a log."""
    records = load_json(input_path)
    index = build_text_index(records)
    agent = build_agent(index)

    result = await agent.run(user_prompt=question)
    log_file = log_interaction_to_file(agent, result.new_messages(), source=source)

    return result.output, log_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask questions about a repository using a search-backed agent.")
    parser.add_argument("--input", required=True, help="Input chunk JSON path")
    parser.add_argument("--question", required=True, help="User question")
    args = parser.parse_args()

    answer, log_file = asyncio.run(run_agent(input_path=args.input, question=args.question))
    print(answer)
    print(f"\nLog saved to: {log_file}")


if __name__ == "__main__":
    main()

