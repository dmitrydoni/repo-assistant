import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from agent_repository_qa import run_agent


def load_json(input_path: str) -> dict[str, Any]:
    """Load generated evaluation questions from a JSON file."""
    path = Path(input_path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


async def run_questions(agent_input: str, questions_file: str) -> list[dict[str, Any]]:
    """Run the repository agent on generated questions and log each interaction."""
    payload = load_json(questions_file)
    questions = payload.get("questions", [])

    results: list[dict[str, Any]] = []

    for question in questions:
        answer, log_file = await run_agent(
            input_path=agent_input,
            question=question,
            source="ai-generated",
        )
        results.append(
            {
                "question": question,
                "answer": answer,
                "log_file": str(log_file),
            }
        )

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run generated evaluation questions through the repository agent.")
    parser.add_argument("--agent-input", required=True, help="Input chunk JSON path for the agent")
    parser.add_argument("--questions-file", required=True, help="Generated questions JSON path")
    parser.add_argument("--output", default=None, help="Optional output JSON path for run results")
    args = parser.parse_args()

    results = asyncio.run(
        run_questions(
            agent_input=args.agent_input,
            questions_file=args.questions_file,
        )
    )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

