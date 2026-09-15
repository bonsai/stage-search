#!/usr/bin/env python3
"""STAGE-Search event aggregation agent.

Fetch configured public event datasets, normalize them into one Event model,
and write data/events.jsonl plus data/week.json.
"""
from __future__ import annotations

import json
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources.yaml"
OUT = ROOT / "data"


def load_sources() -> list[dict]:
    # Keep the runtime dependency-free: this is intentionally a tiny YAML reader
    # for the flat source definitions used by this project.
    import re
    text = SOURCES.read_text(encoding="utf-8")
    rows = []
    current = None
    for line in text.splitlines():
        m = re.match(r"\s*- id:\s*(.+)", line)
        if m:
            current = {"id": m.group(1).strip()}
            rows.append(current)
            continue
        if current is None:
            continue
        m = re.match(r"\s+(kind|category|url):\s*(.+)", line)
        if m:
            current[m.group(1)] = m.group(2).strip()
    return rows


def fetch(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "stage-search/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def load_records(source: dict) -> list[dict]:
    raw = fetch(source["url"])
    if source["kind"] == "jsonl":
        return [json.loads(x) for x in raw.splitlines() if x.strip()]
    data = json.loads(raw)
    # owarai-live currently stores its event array directly; tolerate a
    # wrapped JSON string as well.
    if isinstance(data, dict) and isinstance(data.get("content"), str):
        try:
            data = json.loads(data["content"])
        except json.JSONDecodeError:
            pass
    return data if isinstance(data, list) else []


def normalize(e: dict, source: dict) -> dict:
    title = e.get("title") or e.get("name") or ""
    url = e.get("source_url") or e.get("url") or ""
    event_id = str(e.get("id") or f"{source['id']}:{title}:{e.get('date', '')}")
    artists = e.get("artists") or e.get("performers") or []
    return {
        "id": event_id,
        "date": e.get("date") or "",
        "start_at": e.get("start_at") or e.get("start") or "",
        "end_at": e.get("end_at") or "",
        "title": title,
        "venue": e.get("venue") or "",
        "area": e.get("area") or e.get("region") or "",
        "address": e.get("address") or "",
        "artists": artists if isinstance(artists, list) else [],
        "category": source["category"],
        "organizer": e.get("organizer") or e.get("source_type") or "",
        "price": e.get("price") or e.get("fee") or "",
        "url": url,
        "source": source["id"],
        "confidence": e.get("confidence") or "unknown",
    }


def main() -> None:
    events: dict[str, dict] = {}
    errors = []
    for source in load_sources():
        try:
            for raw in load_records(source):
                event = normalize(raw, source)
                if event["title"] and event["url"]:
                    events[event["id"]] = event
        except Exception as exc:
            errors.append({"source": source["id"], "error": str(exc)})

    ordered = sorted(events.values(), key=lambda x: (x["date"] or "9999-99-99", x["start_at"], x["title"]))
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "events.jsonl").open("w", encoding="utf-8") as f:
        for event in ordered:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    today = date.today()
    week_end = today + timedelta(days=7)
    week = [e for e in ordered if e["date"] and today.isoformat() <= e["date"] < week_end.isoformat()]
    (OUT / "week.json").write_text(json.dumps({"from": today.isoformat(), "to": week_end.isoformat(), "events": week, "errors": errors}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"STAGE-Search: {len(ordered)} events / {len(week)} this week / {len(errors)} source errors")
    if errors:
        print(json.dumps(errors, ensure_ascii=False))


if __name__ == "__main__":
    main()
