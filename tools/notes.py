# tools/notes.py
# Notes memory — stores key-value facts in data/notes.json
# Supports: save note, recall note, list all notes, delete note

import json
import os

# Path to the notes data file
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "notes.json")


def _load() -> dict:
    """Load notes dictionary from JSON file."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(notes: dict) -> None:
    """Persist notes dictionary back to JSON file."""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)


def save_note(key: str, value: str) -> str:
    """Store a new note or overwrite an existing one."""
    notes = _load()
    key = key.strip().lower()
    notes[key] = value.strip()
    _save(notes)
    return f"Noted, Sir. I will remember that {key} is: {value.strip()}"


def recall_note(key: str) -> str:
    """Retrieve a note by its key."""
    notes = _load()
    key = key.strip().lower()
    if key in notes:
        return f"My records show that {key} is: {notes[key]}, Sir."
    return f"I have no notes on '{key}', Sir."


def list_notes() -> str:
    """Return all stored notes as a formatted string."""
    notes = _load()
    if not notes:
        return "My memory banks are empty, Sir. No notes saved."
    lines = ["Here is what I have on record, Sir:"]
    for k, v in notes.items():
        lines.append(f"  • {k}: {v}")
    return "\n".join(lines)


def delete_note(key: str) -> str:
    """Remove a note by key."""
    notes = _load()
    key = key.strip().lower()
    if key in notes:
        del notes[key]
        _save(notes)
        return f"Note '{key}' has been erased from my memory, Sir."
    return f"No record found for '{key}', Sir."
