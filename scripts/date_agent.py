#!/usr/bin/env python3
"""STAGE-Search date agent.

Natural-language-ish planner for event-centered dates.
MVP: score normalized events for a date, area, category and budget, then
produce a compact date-plan JSON. The event DB remains the source of truth.
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "data" / "events.jsonl"
OUT = ROOT / "data" / "date-plans.json"


def load_events():
    if not EVENTS.exists():
        return []
    rows = []
    for line in EVENTS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def price_number(value):
    if isinstance(value, (int, float)):
        return int(value)
    if not value:
        return 0
    digits = "".join(c for c in str(value) if c.isdigit())
    return int(digits) if digits else 0


def score(event, target, area="", category="owarai", max_price=5000):
    if event.get("date") != target:
        return -1
    text = " ".join(str(event.get(k, "")) for k in ("title", "type", "category", "venue", "area"))
    s = 0
    if category and category.lower() in text.lower():
        s += 5
    if area and area.lower() in text.lower():
        s += 4
    price = price_number(event.get("price"))
    if price and price <= max_price:
        s += 2
    if price == 0:
        s += 1
    if event.get("start_at"):
        s += 1
    return s


def build(target, area="", category="owarai", max_price=5000, limit=5):
    ranked = sorted(
        ((score(e, target, area, category, max_price), e) for e in load_events()),
        key=lambda x: (-x[0], x[1].get("start_at", "")),
    )
    events = [e for s, e in ranked if s >= 0][:limit]
    return {
        "kind": "date-plan",
        "date": target,
        "theme": f"{category} date",
        "area": area,
        "max_price": max_price,
        "events": events,
        "plan": ["meet", "event", "dinner", "walk_or_cafe"],
    }


def main():
    target = (date.today() + timedelta(days=3)).isoformat()
    area = ""
    if len(sys.argv) > 1:
        target = sys.argv[1]
    if len(sys.argv) > 2:
        area = sys.argv[2]
    plan = build(target, area)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
