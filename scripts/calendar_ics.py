#!/usr/bin/env python3
"""Create a minimal RFC 5545 iCalendar event from a normalized STAGE event."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path


def esc(value: str) -> str:
    return str(value or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def dt(value: str, date_value: str) -> str:
    value = value or date_value
    if not value:
        raise ValueError("event has no date/start_at")
    value = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo:
        return parsed.astimezone().strftime("%Y%m%dT%H%M%S")
    return parsed.strftime("%Y%m%dT%H%M%S")


def make_ics(event: dict) -> str:
    start = dt(event.get("start_at"), event.get("date"))
    end = dt(event.get("end_at"), event.get("date")) if event.get("end_at") else ""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//bonsai//STAGE-Search//JP",
        "BEGIN:VEVENT",
        f"UID:{esc(event.get('id') or event.get('url'))}@stage-search",
        f"DTSTART:{start}",
    ]
    if end:
        lines.append(f"DTEND:{end}")
    lines += [
        f"SUMMARY:{esc(event.get('title'))}",
        f"LOCATION:{esc(', '.join(x for x in [event.get('venue'), event.get('address')] if x))}",
        f"DESCRIPTION:{esc(event.get('url'))}",
        f"URL:{esc(event.get('url'))}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(lines) + "\r\n"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: calendar_ics.py EVENT.json")
    event = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(make_ics(event), end="")
