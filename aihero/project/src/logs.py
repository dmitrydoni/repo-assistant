import json
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def serializer(obj: Any) -> str:
    """Serialize datetime values for JSON output."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def log_entry(agent: Agent, messages: list[Any], source: str = "user") -> dict[str, Any]:
    """Build a structured log entry for one agent interaction."""
    dict_messages = ModelMessagesTypeAdapter.dump_python(messages)

    return {
        "agent_name": agent.name,
        "system_prompt": getattr(agent, "_instructions", None),
        "tools": ["search_repo"],
        "messages": dict_messages,
        "source": source,
    }


def log_interaction_to_file(agent: Agent, messages: list[Any], source: str = "user") -> Path:
    """Save one agent interaction to a JSON log file."""
    entry = log_entry(agent, messages, source=source)

    ts = entry["messages"][-1]["timestamp"]
    if isinstance(ts, datetime):
        ts_obj = ts
    else:
        ts_obj = datetime.fromisoformat(ts.replace("Z", "+00:00"))

    ts_str = ts_obj.strftime("%Y%m%d_%H%M%S")
    rand_hex = secrets.token_hex(3)

    filename = f"{agent.name}_{ts_str}_{rand_hex}.json"
    filepath = LOG_DIR / filename

    with filepath.open("w", encoding="utf-8") as f_out:
        json.dump(entry, f_out, indent=2, default=serializer)

    return filepath

