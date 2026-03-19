# tools/sysinfo.py
# System information tool — reports CPU usage, RAM stats, and the current
# date/time. Uses the 'psutil' library for hardware metrics.

import psutil
from datetime import datetime


def get_time() -> str:
    """Return the current time in a human-readable JARVIS style."""
    now = datetime.now()
    hour = now.strftime("%H:%M")
    date = now.strftime("%B %dst %Y") if now.day == 1 else \
           now.strftime("%B %dnd %Y") if now.day == 2 else \
           now.strftime("%B %drd %Y") if now.day == 3 else \
           now.strftime("%B %dth %Y")
    return f"It is {hour}, Sir. {date}."


def get_date() -> str:
    """Return the current date."""
    now = datetime.now()
    day = now.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"Today is {now.strftime('%A')}, {now.strftime('%B')} {day}{suffix}, {now.year}, Sir."


def get_cpu() -> str:
    """Return current CPU utilization percentage."""
    cpu = psutil.cpu_percent(interval=0.5)
    cores = psutil.cpu_count(logical=True)
    freq = psutil.cpu_freq()
    freq_str = f" at {freq.current:.0f} MHz" if freq else ""
    level = "nominal" if cpu < 60 else "elevated" if cpu < 85 else "high"
    return (
        f"CPU usage is at {cpu}%{freq_str}, Sir. "
        f"Running {cores} logical core{'s' if cores != 1 else ''}. Load level: {level}."
    )


def get_ram() -> str:
    """Return current RAM usage statistics."""
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024 ** 3)
    used_gb  = mem.used  / (1024 ** 3)
    free_gb  = mem.available / (1024 ** 3)
    percent  = mem.percent
    status = "nominal" if percent < 70 else "moderate" if percent < 85 else "critical"
    return (
        f"RAM: {used_gb:.1f} GB used of {total_gb:.1f} GB total ({percent}% utilised). "
        f"{free_gb:.1f} GB available. Status: {status}, Sir."
    )


def get_sysinfo() -> str:
    """Return a full system report combining CPU, RAM, and time."""
    lines = [
        "── System Status Report ──",
        get_time(),
        get_cpu(),
        get_ram(),
    ]
    # Battery info (optional — not all systems have batteries)
    try:
        battery = psutil.sensors_battery()
        if battery:
            charging = "charging" if battery.power_plugged else "on battery"
            lines.append(f"Battery: {battery.percent:.0f}% ({charging}).")
    except AttributeError:
        pass  # sensors_battery not available on this platform
    return "\n".join(lines)
