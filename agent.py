# agent.py
# Intent detection and routing engine for J.A.R.V.I.S.
# Parses user input using keyword matching, then falls back to LLM for
# open-ended questions. Routes to the appropriate tool module.

import re

# ── Tool imports ───────────────────────────────────────────────────────────────
from tools import tasks, notes, calculator, apps, sysinfo, weather, chat


# ── Intent pattern definitions ────────────────────────────────────────────────
# Each entry is a tuple of (list_of_keywords, handler_function).
# Keywords are checked via case-insensitive substring matching.
# More specific patterns must appear BEFORE general ones.

def detect_and_respond(user_input: str) -> tuple[str, str]:
    """
    Parse user_input, detect intent, invoke the right tool, and return
    a tuple of (response_text, response_type).

    response_type is one of: 'success', 'warning', 'error', 'info', 'chat'
    This is used by main.py to colour-code the output.
    """
    raw   = user_input.strip()
    lower = raw.lower()

    # ── Exit / quit ────────────────────────────────────────────────────────────
    if any(k in lower for k in ["exit", "quit", "goodbye", "bye", "shutdown"]):
        return ("Farewell, Sir. J.A.R.V.I.S. going offline. Stay safe.", "warning")

    # ── Help ───────────────────────────────────────────────────────────────────
    if lower in ("help", "?", "commands", "what can you do"):
        return (_help_text(), "info")

    # ── Set API key at runtime ─────────────────────────────────────────────────
    if lower.startswith("set apikey ") or lower.startswith("set api key "):
        key = re.sub(r"^set api ?key\s+", "", lower, flags=re.IGNORECASE).strip()
        return (chat.set_api_key(key), "success")

    # ── System info ────────────────────────────────────────────────────────────
    if any(k in lower for k in ["what time", "current time", "what's the time", "whats the time"]):
        return (sysinfo.get_time(), "info")

    if any(k in lower for k in ["what date", "today's date", "todays date", "what day"]):
        return (sysinfo.get_date(), "info")

    if any(k in lower for k in ["cpu usage", "cpu stats", "processor"]):
        return (sysinfo.get_cpu(), "info")

    if any(k in lower for k in ["ram usage", "memory usage", "ram stats"]):
        return (sysinfo.get_ram(), "info")

    if any(k in lower for k in ["system info", "system status", "system stats", "sysinfo"]):
        return (sysinfo.get_sysinfo(), "info")

    # ── Task management ────────────────────────────────────────────────────────
    if lower.startswith("add task "):
        desc = raw[len("add task "):].strip()
        return (tasks.add_task(desc), "success") if desc else \
               ("Please provide a task description, Sir.", "warning")

    if any(k in lower for k in ["show tasks", "list tasks", "my tasks", "pending tasks", "show my tasks"]):
        return (tasks.show_tasks(), "info")

    m = re.search(r"delete task (\d+)", lower)
    if m:
        return (tasks.delete_task(int(m.group(1))), "success")

    m = re.search(r"(?:complete|done|finish) task (\d+)", lower)
    if m:
        return (tasks.complete_task(int(m.group(1))), "success")

    if any(k in lower for k in ["clear tasks", "clear all tasks", "delete all tasks"]):
        return (tasks.clear_tasks(), "warning")

    # ── Notes / memory ─────────────────────────────────────────────────────────
    # "remember that X is Y" or "note that X is Y" or "save note X: Y"
    m = re.search(r"(?:remember|note|save note)(?:\s+that)?\s+(.+?)\s+is\s+(.+)", raw, re.IGNORECASE)
    if m:
        return (notes.save_note(m.group(1), m.group(2)), "success")

    m = re.search(r"save note\s+(\w[\w\s]*?):\s*(.+)", raw, re.IGNORECASE)
    if m:
        return (notes.save_note(m.group(1), m.group(2)), "success")

    # "what is X" handled first by notes, then by LLM
    m = re.search(r"(?:recall|what do you know about|what is my|remind me of)\s+(.+)", raw, re.IGNORECASE)
    if m:
        return (notes.recall_note(m.group(1)), "info")

    if any(k in lower for k in ["show notes", "list notes", "my notes", "all notes"]):
        return (notes.list_notes(), "info")

    m = re.search(r"delete note\s+(.+)", raw, re.IGNORECASE)
    if m:
        return (notes.delete_note(m.group(1)), "success")

    if lower == "clear history":
        return (chat.clear_history(), "warning")

    # ── Calculator ─────────────────────────────────────────────────────────────
    # Matches: "calculate ...", "compute ...", or a bare math expression
    m = re.match(r"(?:calculate|compute|eval(?:uate)?|what is|solve)\s+(.+)", lower)
    if m:
        expr = m.group(1).strip()
        # Confirm it looks like math (contains digits and operators)
        if re.search(r"[\d\+\-\*\/\^\%\(\)]", expr):
            return (calculator.calculate(expr), "success")

    # Bare math expression: only digits and math symbols, no letters
    if re.fullmatch(r"[\d\s\+\-\*\/\%\(\)\*\*\.]+", lower) and re.search(r"\d", lower):
        return (calculator.calculate(lower), "success")

    # ── Weather ────────────────────────────────────────────────────────────────
    m = re.search(r"weather(?:\s+(?:in|for|at))?\s+(.+)", lower)
    if m:
        return (weather.get_weather(m.group(1).strip()), "info")

    m = re.search(r"(?:what'?s?|how'?s?) the weather (?:in|for|at)\s+(.+)", lower)
    if m:
        return (weather.get_weather(m.group(1).strip()), "info")

    # ── App / website launcher ─────────────────────────────────────────────────
    m = re.match(r"(?:open|launch|start|run|go to)\s+(.+)", lower)
    if m:
        return (apps.open_app(m.group(1).strip()), "success")

    # ── Web search ─────────────────────────────────────────────────────────────
    m = re.match(r"(?:search|google|look up|find)\s+(.+)", lower)
    if m:
        return (apps.search_web(m.group(1).strip()), "success")

    # ── Text summarization ─────────────────────────────────────────────────────
    m = re.match(r"summarize\s+(.+)", raw, re.IGNORECASE | re.DOTALL)
    if m:
        return (chat.summarize(m.group(1).strip()), "chat")

    # ── LLM fallback ───────────────────────────────────────────────────────────
    # Anything not caught above goes to the conversational AI
    return (chat.chat(raw), "chat")


# ── Help text ──────────────────────────────────────────────────────────────────
def _help_text() -> str:
    return """\
J.A.R.V.I.S. COMMAND REFERENCE

  TIME & SYSTEM
    what time is it          → Current time
    what date is it          → Current date
    cpu usage                → CPU utilisation
    ram usage                → RAM statistics
    system info              → Full status report

  TASK MANAGER
    add task <description>   → Add a new task
    show tasks               → List all tasks
    complete task <id>       → Mark task done
    delete task <id>         → Remove a task
    clear tasks              → Wipe all tasks

  NOTES MEMORY
    remember that <key> is <value>  → Save a fact
    recall <key>                    → Retrieve a fact
    show notes                      → List all facts
    delete note <key>               → Erase a fact

  CALCULATOR
    calculate <expression>   → Evaluate math
    2 + 2 * 10               → Direct expressions

  WEATHER
    weather in <city>        → Current conditions

  APPS & WEB
    open <app/site>          → Launch app or browser
    search <query>           → Google in browser

  AI CONVERSATION
    <any question>           → LLM answers (JARVIS tone)
    summarize <long text>    → Text summarization
    set apikey <key>         → Set OpenRouter API key
    clear history            → Reset conversation

  exit / quit                → Shutdown J.A.R.V.I.S."""
