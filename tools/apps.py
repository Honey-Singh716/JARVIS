# tools/apps.py
# Application and website launcher for Windows.
# Opens common apps and websites using subprocess and webbrowser.

import subprocess
import webbrowser

# ── Website shortcuts ──────────────────────────────────────────────────────────
WEBSITES = {
    "youtube":   "https://www.youtube.com",
    "google":    "https://www.google.com",
    "github":    "https://www.github.com",
    "gmail":     "https://mail.google.com",
    "maps":      "https://maps.google.com",
    "netflix":   "https://www.netflix.com",
    "reddit":    "https://www.reddit.com",
    "twitter":   "https://www.twitter.com",
    "x":         "https://www.x.com",
    "linkedin":  "https://www.linkedin.com",
    "wikipedia": "https://www.wikipedia.org",
    "chatgpt":   "https://chat.openai.com",
}

# ── Desktop application commands (Windows) ────────────────────────────────────
APPS = {
    "notepad":       "notepad.exe",
    "calculator":    "calc.exe",
    "paint":         "mspaint.exe",
    "explorer":      "explorer.exe",
    "cmd":           "cmd.exe",
    "powershell":    "powershell.exe",
    "task manager":  "taskmgr.exe",
    "vscode":        "code",
    "vs code":       "code",
    "spotify":       "spotify.exe",
    "chrome":        "chrome.exe",
    "firefox":       "firefox.exe",
    "edge":          "msedge.exe",
    "browser":       "msedge.exe",   # Default browser fallback
}


def open_app(name: str) -> str:
    """
    Open a website or desktop application by name.
    Tries websites first, then desktop apps, then a Google search fallback.
    """
    name_lower = name.strip().lower()

    # ── Check websites ─────────────────────────────────────────────────────────
    for key, url in WEBSITES.items():
        if key in name_lower:
            webbrowser.open(url)
            return f"Opening {key.capitalize()} now, Sir."

    # ── Check desktop apps ─────────────────────────────────────────────────────
    for key, cmd in APPS.items():
        if key in name_lower:
            try:
                subprocess.Popen(cmd, shell=True)
                return f"Launching {key.title()}, Sir."
            except FileNotFoundError:
                return f"Application '{key}' was not found on this system, Sir."

    # ── Fallback: open as URL if it looks like a URL ──────────────────────────
    if "." in name_lower and " " not in name_lower:
        url = name_lower if name_lower.startswith("http") else f"https://{name_lower}"
        webbrowser.open(url)
        return f"Opening {name}, Sir."

    # ── Fallback: Google search ───────────────────────────────────────────────
    search_url = f"https://www.google.com/search?q={name.replace(' ', '+')}"
    webbrowser.open(search_url)
    return f"I couldn't find '{name}' directly, Sir. Searching Google instead."


def search_web(query: str) -> str:
    """Open a Google search for the given query."""
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching the web for '{query}', Sir."
