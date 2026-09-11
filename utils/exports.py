import csv
import io
import json


def analysis_to_json(data: dict) -> bytes:
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")


def analysis_to_txt(data: dict) -> bytes:
    lines = [
        f"MEETING: {data.get('meeting_title', 'Untitled Meeting')}",
        "",
        "SUMMARY",
        data.get("summary", ""),
        "",
        "PARTICIPANTS",
        *[f"- {x}" for x in data.get("participants", [])],
        "",
        "ACTION ITEMS",
    ]

    for i, item in enumerate(data.get("action_items", []), 1):
        lines += [
            f"{i}. {item.get('task')}",
            f"   Assignee: {item.get('assignee')}",
            f"   Deadline: {item.get('deadline')}",
            f"   Priority: {item.get('priority')}",
        ]

    lines += ["", "DECISIONS"]
    lines += [f"- {x}" for x in data.get("decisions", [])]

    lines += ["", "FOLLOW-UP ITEMS"]
    lines += [f"- {x}" for x in data.get("follow_up_items", [])]

    return "\n".join(lines).encode("utf-8")


def analysis_to_csv(data: dict) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Task", "Assignee", "Deadline", "Priority", "Source"])
    for item in data.get("action_items", []):
        writer.writerow([
            item.get("task", ""),
            item.get("assignee", ""),
            item.get("deadline", ""),
            item.get("priority", ""),
            item.get("source", ""),
        ])
    return output.getvalue().encode("utf-8")
