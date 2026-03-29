import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent


class EvaluationCheck(BaseModel):
    """Single evaluation check result."""

    check_name: str
    justification: str
    check_pass: bool


class EvaluationChecklist(BaseModel):
    """Structured evaluation output for one interaction log."""

    checklist: list[EvaluationCheck]
    summary: str


EVALUATION_PROMPT = """
Use this checklist to evaluate the quality of an AI agent's answer (<ANSWER>) to a user question (<QUESTION>).
We also include the interaction log (<LOG>) for analysis.

For each item, check if the condition is met.

Checklist:
- instructions_follow: The agent followed the system instructions in <INSTRUCTIONS>
- answer_relevant: The response directly addresses the user's question
- answer_clear: The answer is clear and practically useful
- answer_grounded: The answer is grounded in the retrieved repository information
- tool_call_search: The search tool was invoked

Output true/false for each check and provide a short explanation for your judgment.
""".strip()

USER_PROMPT_TEMPLATE = """
<INSTRUCTIONS>{instructions}</INSTRUCTIONS>
<QUESTION>{question}</QUESTION>
<ANSWER>{answer}</ANSWER>
<LOG>{log}</LOG>
""".strip()


def load_log_file(log_file: str) -> dict[str, Any]:
    """Load one saved agent log file."""
    path = Path(log_file)
    with path.open("r", encoding="utf-8") as f:
        log_data = json.load(f)
    log_data["log_file"] = path.name
    return log_data


def load_log_records_from_dir(log_dir: str, source: str | None = None) -> list[dict[str, Any]]:
    """Load saved agent log files from a directory, optionally filtering by source."""
    path = Path(log_dir)
    records: list[dict[str, Any]] = []

    for log_file in sorted(path.glob("*.json")):
        record = load_log_file(str(log_file))

        if source is not None and record.get("source") != source:
            continue

        records.append(record)

    return records


def simplify_log_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reduce log verbosity before sending it to the evaluation model."""
    simplified: list[dict[str, Any]] = []

    for message in messages:
        parts = []

        for original_part in message.get("parts", []):
            part = original_part.copy()
            part_kind = part.get("part_kind")

            if part_kind == "user-prompt":
                part.pop("timestamp", None)

            if part_kind == "tool-call":
                part.pop("tool_call_id", None)

            if part_kind == "tool-return":
                part.pop("tool_call_id", None)
                part.pop("metadata", None)
                part.pop("timestamp", None)

                tool_content = part.get("content")

                try:
                    parsed = json.loads(tool_content) if isinstance(tool_content, str) else tool_content
                except Exception:
                    parsed = "RETURN_RESULTS_UNPARSEABLE"

                if isinstance(parsed, list):
                    preview = []
                    for item in parsed[:2]:
                        preview.append(
                            {
                                "filename": item.get("filename"),
                                "title": item.get("title"),
                                "section_header": item.get("section_header"),
                                "chunk_index": item.get("chunk_index"),
                                "section_index": item.get("section_index"),
                                "chunk_text_preview": (item.get("chunk_text") or "")[:200],
                            }
                        )
                    part["content"] = preview
                else:
                    part["content"] = parsed

            if part_kind == "text":
                part.pop("id", None)

            parts.append(part)

        simplified.append(
            {
                "kind": message.get("kind"),
                "parts": parts,
            }
        )

    return simplified


def build_eval_agent(model_name: str) -> Agent:
    """Create the evaluation agent."""
    return Agent(
        name="eval_agent",
        model=model_name,
        instructions=EVALUATION_PROMPT,
        output_type=EvaluationChecklist,
    )


async def evaluate_log_record(eval_agent: Agent, log_record: dict[str, Any]) -> EvaluationChecklist:
    """Evaluate one saved agent interaction log."""
    messages = log_record["messages"]

    instructions = log_record["system_prompt"]
    question = messages[0]["parts"][0]["content"]
    answer = messages[-1]["parts"][0]["content"]

    log_simplified = simplify_log_messages(messages)
    log_json = json.dumps(log_simplified, ensure_ascii=False)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        instructions=instructions,
        question=question,
        answer=answer,
        log=log_json,
    )

    result = await eval_agent.run(user_prompt=user_prompt)
    return result.output


async def evaluate_log_records(
    eval_agent: Agent,
    log_records: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], EvaluationChecklist]]:
    """Evaluate multiple saved agent logs."""
    results: list[tuple[dict[str, Any], EvaluationChecklist]] = []

    for log_record in log_records:
        checklist = await evaluate_log_record(eval_agent, log_record)
        results.append((log_record, checklist))

    return results


def print_evaluation(checklist: EvaluationChecklist) -> None:
    """Print evaluation results in a readable format."""
    print(checklist.summary)
    print()

    for check in checklist.checklist:
        status = "PASS" if check.check_pass else "FAIL"
        print(f"[{status}] {check.check_name}: {check.justification}")


def print_evaluation_summary(results: list[tuple[dict[str, Any], EvaluationChecklist]]) -> None:
    """Print simple aggregate pass rates across all evaluations."""
    if not results:
        print("No evaluation results found.")
        return

    totals: dict[str, int] = {}
    passed: dict[str, int] = {}

    for _, checklist in results:
        for check in checklist.checklist:
            totals[check.check_name] = totals.get(check.check_name, 0) + 1
            if check.check_pass:
                passed[check.check_name] = passed.get(check.check_name, 0) + 1

    print("Evaluation summary:")
    for check_name in sorted(totals):
        total = totals[check_name]
        ok = passed.get(check_name, 0)
        rate = ok / total if total else 0.0
        print(f"- {check_name}: {ok}/{total} ({rate:.0%})")


def save_evaluation_results(
    results: list[tuple[dict[str, Any], EvaluationChecklist]],
    output_path: str,
) -> None:
    """Save detailed evaluation results to a JSON file."""
    output = []

    for log_record, checklist in results:
        row = {
            "log_file": log_record.get("log_file"),
            "source": log_record.get("source"),
            "question": log_record["messages"][0]["parts"][0]["content"],
            "answer": log_record["messages"][-1]["parts"][0]["content"],
            "summary": checklist.summary,
            "checks": [
                {
                    "check_name": check.check_name,
                    "check_pass": check.check_pass,
                    "justification": check.justification,
                }
                for check in checklist.checklist
            ],
        }
        output.append(row)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate one saved agent log with an LLM judge.")
    parser.add_argument("--log-dir", default=None, help="Optional directory of log JSON files")
    parser.add_argument("--log-file", default=None, help="Path to one log JSON file")
    parser.add_argument(
        "--model",
        default="openai:gpt-5.4-mini",
        help="Model name for the evaluation agent",
    )
    parser.add_argument("--source", default=None, help="Optional source filter, e.g. user or ai-generated")
    parser.add_argument("--output", default=None, help="Optional output JSON path for evaluation results")
    args = parser.parse_args()

    eval_agent = build_eval_agent(args.model)

    if args.log_dir:
        log_records = load_log_records_from_dir(args.log_dir, source=args.source)
        results = asyncio.run(evaluate_log_records(eval_agent, log_records))
        if args.output:
            save_evaluation_results(results, args.output)
        print_evaluation_summary(results)
    else:
        log_record = load_log_file(args.log_file)
        checklist = asyncio.run(evaluate_log_record(eval_agent, log_record))
        print_evaluation(checklist)


if __name__ == "__main__":
    main()

