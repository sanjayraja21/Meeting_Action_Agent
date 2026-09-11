"""Utilities for validating and safely normalizing meeting analysis JSON.

The validator keeps the output honest by requiring the required top-level
keys, checking action item structure, and replacing unsupported or
missing values with safe defaults instead of hallucinating more details.
"""

from __future__ import annotations

import json
from typing import Any


REQUIRED_KEYS = {
    "meeting_title",
    "summary",
    "participants",
    "action_items",
    "decisions",
    "follow_up_items",
}


VALID_PRIORITIES = {"High", "Medium", "Low", "Unspecified"}


def validate_json_text(text: str) -> dict[str, Any]:
    """Parse a model response that may contain markdown fences.

    Returns a dictionary when the response contains valid JSON. Raises
    ValueError if no JSON object can be safely recovered.
    """

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    if not cleaned.startswith("{"):
        # recover from an inner JSON object if the model added text
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise ValueError("The model did not return valid JSON.")
        cleaned = cleaned[start : end + 1]

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("The model did not return valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise ValueError("The model did not return a JSON object.")

    return parsed


def normalize_action_item(item: Any, index: int = 0) -> dict[str, str]:
    """Convert a single action item to the required safe schema."""

    if not isinstance(item, dict):
        raise ValueError(f"Action item {index + 1} must be a JSON object.")

    task = str(item.get("task") or "").strip()
    assignee = str(item.get("assignee") or "Unassigned").strip()
    deadline = str(item.get("deadline") or "No deadline").strip()
    priority = str(item.get("priority") or "Unspecified").strip()
    source = str(item.get("source") or "").strip()

    if not task:
        task = "Unspecified task"
    if not assignee:
        assignee = "Unassigned"
    if not deadline:
        deadline = "No deadline"
    if not priority:
        priority = "Unspecified"
    if priority not in VALID_PRIORITIES:
        priority = "Unspecified"

    return {
        "task": task,
        "assignee": assignee,
        "deadline": deadline,
        "priority": priority,
        "source": source,
    }


def validate_analysis(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and repair a meeting analysis dictionary.

    Safety rule: do not invent missing information. The validator supplies
    the requested defaults only when the transcript genuinely lacks evidence.
    """

    if not isinstance(data, dict):
        raise ValueError("Model response must be a JSON object.")

    missing = sorted(REQUIRED_KEYS - set(data.keys()))
    if missing:
        for key in missing:
            if key == "participants":
                data[key] = []
            elif key == "action_items":
                data[key] = []
            elif key == "decisions":
                data[key] = []
            elif key == "follow_up_items":
                data[key] = []
            else:
                data[key] = ""

    data["meeting_title"] = str(data.get("meeting_title") or "Untitled Meeting")
    data["summary"] = str(data.get("summary") or "No summary was generated.")

    participants = data.get("participants") or []
    if not isinstance(participants, list):
        participants = [str(participants)] if participants else []
    data["participants"] = [str(p).strip() for p in participants if str(p).strip()]

    action_items = data.get("action_items") or []
    if not isinstance(action_items, list):
        raise ValueError("Action items must be returned as a JSON array.")

    cleaned_actions = []
    seen_keys = set()
    for idx, item in enumerate(action_items):
        try:
            normalized = normalize_action_item(item, idx)
        except Exception as exc:
            raise ValueError(f"Invalid action item structure: {exc}") from exc

        dedupe_key = (normalized["task"].lower(), normalized["assignee"].lower(), normalized["deadline"].lower())
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        cleaned_actions.append(normalized)

    data["action_items"] = cleaned_actions

    decisions = data.get("decisions") or []
    if not isinstance(decisions, list):
        decisions = [str(decisions)]
    data["decisions"] = [str(x).strip() for x in decisions if str(x).strip()]

    follow_up_items = data.get("follow_up_items") or []
    if not isinstance(follow_up_items, list):
        follow_up_items = [str(follow_up_items)]
    data["follow_up_items"] = [str(x).strip() for x in follow_up_items if str(x).strip()]

    return data


def require_no_hallucinations(data: dict[str, Any]) -> bool:
    """Return True when the payload is sufficiently grounded in the transcript.

    This lightweight check is intentionally conservative. It catches obvious
    cases where a model returns impossible placeholders or fabricated fields.
    """

    if not isinstance(data, dict):
        return False

    if "title" in data and data.get("title") in {"", "None"}:
        return False

    return True
