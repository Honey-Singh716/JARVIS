# tools/tasks.py
# Task manager — stores tasks in data/tasks.json
# Supports: add task, show tasks, delete task, clear all tasks

import json
import os

# Path to the tasks data file (resolved relative to this file's location)
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tasks.json")


def _load() -> list:
    """Load tasks list from JSON file."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save(tasks: list) -> None:
    """Persist tasks list back to JSON file."""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def add_task(description: str) -> str:
    """Add a new task and return a confirmation message."""
    tasks = _load()
    task = {
        "id": len(tasks) + 1,
        "description": description.strip(),
        "done": False
    }
    tasks.append(task)
    _save(tasks)
    return f"Task logged, Sir. You now have {len(tasks)} pending task{'s' if len(tasks) != 1 else ''}."


def show_tasks() -> str:
    """Return a formatted string listing all tasks."""
    tasks = _load()
    if not tasks:
        return "Your task list is empty, Sir. Nothing pending."
    lines = ["Here are your current tasks, Sir:"]
    for t in tasks:
        status = "✓" if t.get("done") else "○"
        lines.append(f"  [{status}] {t['id']}. {t['description']}")
    return "\n".join(lines)


def delete_task(task_id: int) -> str:
    """Delete a task by its numeric ID."""
    tasks = _load()
    original_len = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) == original_len:
        return f"No task found with ID {task_id}, Sir."
    _save(tasks)
    return f"Task {task_id} removed, Sir. {len(tasks)} task{'s' if len(tasks) != 1 else ''} remaining."


def complete_task(task_id: int) -> str:
    """Mark a task as completed."""
    tasks = _load()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            _save(tasks)
            return f"Task {task_id} marked as complete, Sir. Well done."
    return f"No task found with ID {task_id}, Sir."


def clear_tasks() -> str:
    """Remove all tasks."""
    _save([])
    return "All tasks cleared, Sir. Starting with a clean slate."
