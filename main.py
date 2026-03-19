# main.py
# J.A.R.V.I.S. — Entry point with Rich terminal UI.
# Handles the animated boot sequence, header panel, input loop,
# and colour-coded typed output. All visual styling is here.

import time
import sys
import os

from rich.console import Console
from rich.panel   import Panel
from rich.text    import Text
from rich.table   import Table
from rich.columns import Columns
from rich.live    import Live
from rich.align   import Align
from rich import   box

import psutil
from datetime import datetime

# Import the intent router
from agent import detect_and_respond

# ── Console (no markup auto-escape — we control markup ourselves) ──────────────
console = Console()

# ── Colour palette ─────────────────────────────────────────────────────────────
C_CYAN    = "cyan"
C_BLUE    = "bright_blue"
C_GREEN   = "bright_green"
C_YELLOW  = "yellow"
C_RED     = "bright_red"
C_WHITE   = "bright_white"
C_DIM     = "dim cyan"
C_HEADER  = "bold cyan"

# ── JARVIS ASCII logo ──────────────────────────────────────────────────────────
LOGO = r"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
  Just A Rather Very Intelligent System
"""


# ── Typing animation ───────────────────────────────────────────────────────────
def type_print(text: str, style: str = C_CYAN, delay: float = 0.018) -> None:
    """Print text with a character-by-character typing animation effect."""
    for char in text:
        console.print(char, style=style, end="", highlight=False)
        time.sleep(delay)
    console.print()  # Newline after typing finishes


# ── Boot check line printer ────────────────────────────────────────────────────
def boot_line(label: str, status: str = "OK", delay: float = 0.04) -> None:
    """Print a single boot diagnostic line with colour-coded status."""
    time.sleep(delay)
    if status == "OK":
        status_text = Text("[ OK ]", style=f"bold {C_GREEN}")
    elif status == "WARN":
        status_text = Text("[WARN]", style=f"bold {C_YELLOW}")
    else:
        status_text = Text("[FAIL]", style=f"bold {C_RED}")

    console.print(status_text, end=" ")
    console.print(label, style=C_DIM)


# ── Animated startup sequence ──────────────────────────────────────────────────
def startup_sequence() -> None:
    """Display the animated JARVIS boot sequence."""
    console.clear()

    # ASCII logo in a cyan panel
    logo_text = Text(LOGO, style=f"bold {C_CYAN}")
    panel = Panel(
        Align.center(logo_text),
        border_style=C_CYAN,
        padding=(0, 2),
    )
    console.print(panel)
    time.sleep(0.3)

    # Boot status lines
    console.rule(f"[{C_CYAN}]INITIALIZING J.A.R.V.I.S...[/{C_CYAN}]", style=C_CYAN)
    time.sleep(0.2)

    boot_line("Loading core modules ...............", "OK")
    boot_line("Initialising Rich terminal UI ......", "OK")
    boot_line("Connecting to task database ........", "OK")
    boot_line("Loading notes memory ...............", "OK")
    boot_line("Calibrating AST calculator .........", "OK")
    boot_line("Loading application registry .......", "OK")
    boot_line("Connecting system monitor (psutil) .", "OK")

    # API key check
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if api_key:
        boot_line("OpenRouter API key detected ........", "OK")
    else:
        boot_line("OpenRouter API key NOT SET (set OPENROUTER_API_KEY)", "WARN")

    boot_line("Starting weather module ............", "OK")
    boot_line("All subsystems nominal .............", "OK")

    time.sleep(0.3)
    console.rule(style=C_CYAN)
    time.sleep(0.4)

    # Greeting message with typing animation
    hour = datetime.now().hour
    greeting = "Good morning" if 5 <= hour < 12 else \
               "Good afternoon" if 12 <= hour < 17 else \
               "Good evening"

    console.print()
    type_print(f'  {greeting}, Sir. All systems are online.', style=f"bold {C_CYAN}", delay=0.03)
    type_print('  J.A.R.V.I.S. is fully operational. Type "help" for commands.', style=C_DIM, delay=0.015)
    console.print()


# ── Live header panel ──────────────────────────────────────────────────────────
def _build_header() -> Panel:
    """Build the status header bar showing time, date, CPU, RAM."""
    now    = datetime.now()
    cpu    = psutil.cpu_percent(interval=None)
    mem    = psutil.virtual_memory()
    ram_pc = mem.percent

    # Colour CPU bar: green < 60, yellow < 85, red >= 85
    cpu_color = C_GREEN if cpu < 60 else (C_YELLOW if cpu < 85 else C_RED)
    ram_color = C_GREEN if ram_pc < 70 else (C_YELLOW if ram_pc < 85 else C_RED)

    table = Table.grid(expand=True, padding=(0, 2))
    table.add_column(justify="left",   ratio=3)
    table.add_column(justify="center", ratio=4)
    table.add_column(justify="right",  ratio=3)

    left   = Text.assemble(
        ("⬡ J.A.R.V.I.S.", f"bold {C_CYAN}"),
        ("  ●  ", C_DIM),
        ("[ONLINE]", f"bold {C_GREEN}"),
    )
    center = Text.assemble(
        (now.strftime("%A, %B %d %Y"), C_WHITE),
        ("   ⟩   ", C_DIM),
        (now.strftime("%H:%M:%S"), f"bold {C_CYAN}"),
    )
    right = Text.assemble(
        ("CPU ", C_DIM),
        (f"{cpu:.0f}%", f"bold {cpu_color}"),
        ("  RAM ", C_DIM),
        (f"{ram_pc:.0f}%", f"bold {ram_color}"),
    )

    table.add_row(left, center, right)
    return Panel(table, border_style=C_CYAN, padding=(0, 1))


def print_header() -> None:
    """Print the static (non-live) header. Called once per loop iteration."""
    console.print(_build_header())


# ── Response rendering ─────────────────────────────────────────────────────────
def render_response(text: str, response_type: str) -> None:
    """Render the JARVIS response inside a styled panel with typing animation."""
    # Choose panel border colour and title based on response type
    type_map = {
        "success": (C_GREEN,  "● JARVIS — SUCCESS"),
        "warning": (C_YELLOW, "⚠ JARVIS — WARNING"),
        "error":   (C_RED,    "✖ JARVIS — ERROR"),
        "info":    (C_BLUE,   "◈ JARVIS — SYSTEM"),
        "chat":    (C_CYAN,   "◆ JARVIS"),
    }
    border_color, title = type_map.get(response_type, (C_CYAN, "◆ JARVIS"))

    # Print panel header
    panel_title = Text(f" {title} ", style=f"bold {border_color}")
    console.print()
    console.print(Panel(
        "",
        title=panel_title,
        border_style=border_color,
        padding=(0, 2),
        height=1,
    ), end="")

    # Type the response character by character inside the panel indent
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if i == 0:
            console.print(f"  [dim cyan]▶[/dim cyan] ", end="")
        else:
            console.print("    ", end="")
        type_print(line, style=border_color, delay=0.008)

    console.print()


# ── Separator ──────────────────────────────────────────────────────────────────
def print_separator() -> None:
    console.rule(style=f"dim {C_CYAN}")


# ── Main interaction loop ──────────────────────────────────────────────────────
def main() -> None:
    """Entry point: run startup sequence then enter the interactive JARVIS loop."""
    startup_sequence()
    print_header()
    print_separator()

    while True:
        try:
            # ── Prompt ────────────────────────────────────────────────────────
            console.print(
                Text.assemble(
                    ("\n  ◇ SIR  ", f"bold {C_YELLOW}"),
                    ("›› ", C_DIM),
                ),
                end="",
            )
            user_input = input().strip()

            # Skip empty input silently
            if not user_input:
                continue

            # ── Processing indicator ──────────────────────────────────────────
            console.print(
                f"  [dim cyan][ PROCESSING ][/dim cyan]",
                highlight=False
            )

            # ── Route to agent ────────────────────────────────────────────────
            response, resp_type = detect_and_respond(user_input)

            # ── Render response ───────────────────────────────────────────────
            render_response(response, resp_type)

            # Graceful shutdown on exit intent
            if resp_type == "warning" and any(k in user_input.lower()
               for k in ["exit", "quit", "goodbye", "bye", "shutdown"]):
                time.sleep(0.8)
                break

            # Refresh header after each command
            print_separator()
            print_header()
            print_separator()

        except KeyboardInterrupt:
            # Ctrl+C ── clean shutdown
            console.print()
            console.print(
                Panel(
                    "[bold cyan]  Interrupt received. Powering down, Sir.[/bold cyan]",
                    border_style=C_YELLOW,
                ),
            )
            break
        except EOFError:
            # Non-interactive mode (piped input exhausted)
            break
        except Exception as e:
            # Catch-all — JARVIS never crashes
            console.print(
                Panel(
                    f"[bright_red]  ✖ System fault detected, Sir: {e}[/bright_red]",
                    border_style=C_RED,
                    title="[bold red] ERROR [/bold red]",
                ),
            )

    # ── Shutdown banner ────────────────────────────────────────────────────────
    console.print()
    console.rule(f"[bold {C_CYAN}]J.A.R.V.I.S. OFFLINE[/bold {C_CYAN}]", style=C_CYAN)
    console.print()


# ── Entrypoint guard ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
