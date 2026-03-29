import argparse
import asyncio
import json
import random
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent


class QuestionsList(BaseModel):
    """Structured output for generated evaluation questions."""

    questions: list[str]


QUESTION_GENERATION_PROMPT = """
You are helping create evaluation questions for an AI agent that answers questions about a GitHub repository.

Based on the provided repository documentation chunks, generate realistic user questions.

The questions should:
- be natural and varied
- range from simple to moderately detailed
- focus on installation, setup, usage, workflow, capabilities, and concepts
- stay grounded in what a user could reasonably ask after reading or skimming the docs

Generate one question per provided record.
""".strip()


def load_json(input_path: str) -> list[dict[str, Any]]:
    """Load repository chunk data from a JSON file."""
    path = Path(input_path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict[str, Any], output_path: str) -> None:
    """Save generated questions to a JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def sample_chunk_records(
    records: list[dict[str, Any]],
    sample_size: int,
    seed: int,
) -> list[dict[str, Any]]:
    """Sample a stable subset of chunk records for question generation."""
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")

    rng = random.Random(seed)
    actual_size = min(sample_size, len(records))
    return rng.sample(records, actual_size)


def build_generation_payload(records: list[dict[str, Any]], content_chars: int = 500) -> str:
    """Prepare a compact JSON payload for the question generator."""
    payload = []

    for record in records:
        payload.append(
            {
                "filename": record.get("filename"),
                "title": record.get("title"),
                "section_header": record.get("section_header"),
                "chunk_text_preview": (record.get("chunk_text") or "")[:content_chars],
            }
        )

    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_question_generator(model_name: str) -> Agent:
    """Create the question generation agent."""
    return Agent(
        name="question_generator",
        model=model_name,
        instructions=QUESTION_GENERATION_PROMPT,
        output_type=QuestionsList,
    )


async def generate_questions(
    input_path: str,
    model_name: str,
    sample_size: int,
    seed: int,
) -> dict[str, Any]:
    """Generate evaluation questions from sampled repository chunks."""
    records = load_json(input_path)
    sample = sample_chunk_records(records, sample_size=sample_size, seed=seed)
    prompt = build_generation_payload(sample)

    agent = build_question_generator(model_name)
    result = await agent.run(user_prompt=prompt)

    return {
        "input_path": input_path,
        "sample_size": len(sample),
        "seed": seed,
        "questions": result.output.questions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate evaluation questions from repository chunks.")
    parser.add_argument("--input", required=True, help="Input chunk JSON path")
    parser.add_argument("--output", required=True, help="Output JSON path for generated questions")
    parser.add_argument(
        "--model",
        default="openai:gpt-5.4-mini",
        help="Model name for question generation",
    )
    parser.add_argument("--sample-size", type=int, default=10, help="Number of chunks to sample")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible sampling")
    args = parser.parse_args()

    result = asyncio.run(
        generate_questions(
            input_path=args.input,
            model_name=args.model,
            sample_size=args.sample_size,
            seed=args.seed,
        )
    )

    save_json(result, args.output)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

