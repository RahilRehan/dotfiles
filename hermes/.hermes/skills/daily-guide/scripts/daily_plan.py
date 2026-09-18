#!/usr/bin/env python3
"""Generate the current four-hour Daily Guide plan without side effects."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "spaced-repetition" / "scripts"))
from review_state import first_pass_summary, item_minutes, load, planned_items, today  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--state",
        type=pathlib.Path,
        default=pathlib.Path.home() / ".hermes" / "state" / "learning.json",
    )
    parser.add_argument(
        "--daily-state",
        type=pathlib.Path,
        default=pathlib.Path.home() / ".hermes" / "state" / "daily.json",
    )
    parser.add_argument("--date")
    parser.add_argument("--exploration", type=float)
    args = parser.parse_args()

    data = load(args.state)
    on = today(args.date)
    try:
        daily_data = json.loads(args.daily_state.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        daily_data = {"days": {}}
    execution_state = daily_data.get("days", {}).get(on.isoformat(), {})
    planning = data.get("planning", {})
    schedule = planning.get("daily_schedule", {})
    total = int(schedule.get("total_minutes", 240))
    news_minutes = int(schedule.get("news_minutes", 20))
    learning_minutes = int(schedule.get("learning_minutes", planning.get("learning_block_minutes", 160)))
    building_minutes = int(schedule.get("building_minutes", 60))
    communication_minutes = int(planning.get("communication_block_minutes", 25))
    dsa_config = planning.get("dsa", {})
    first_pass = dsa_config.get("first_pass", {})
    dsa_minutes = min(
        int(schedule.get("dsa_minutes", first_pass.get("daily_cap_minutes", 75))),
        int(first_pass.get("daily_cap_minutes", 75)),
    )
    system_design_minutes = int(
        schedule.get("system_design_minutes", max(0, learning_minutes - communication_minutes - dsa_minutes))
    )
    exploration = float(planning.get("exploration_level", 0.7)) if args.exploration is None else args.exploration

    def plan_domain(domain: str, minutes: int) -> tuple[list[dict[str, Any]], int, int, list[dict[str, Any]]]:
        selected_due, selected_new, review_used, new_used = planned_items(
            data, on, minutes, exploration, {domain}
        )
        selected = []
        for reason, item in [("due", item) for item in selected_due] + [("new", item) for item in selected_new]:
            selected.append({
            "reason": reason,
            "estimated_minutes": item_minutes(data, item),
            "id": item["id"],
            "domain": item["domain"],
            "kind": item["kind"],
            "label": item["label"],
            })
        return selected_due + selected_new, review_used, new_used, selected

    dsa_selected, dsa_review_used, dsa_new_used, dsa_items = plan_domain("dsa", dsa_minutes)
    sd_selected, sd_review_used, sd_new_used, system_design_items = plan_domain(
        "system-design", system_design_minutes
    )

    communication_ready = any(item["domain"] == "communication" for item in data["items"])
    print(json.dumps({
        "date": on.isoformat(),
        "timezone": data.get("timezone", "Asia/Kolkata"),
        "total_minutes": total,
        "execution_state": {
            "completed": execution_state.get("completed", []),
            "skipped": execution_state.get("skipped", []),
            "shortened": execution_state.get("shortened", []),
            "energy": execution_state.get("energy"),
        },
        "blocks": [
            {
                "id": "news",
                "minutes": news_minutes,
                "skill": "x-news-digest",
                "status": "configured",
            },
            {
                "id": "communication",
                "minutes": communication_minutes,
                "skill": "communication-coach",
                "status": "ready" if communication_ready else "planned-at-session-time",
            },
            {
                "id": "dsa",
                "minutes": dsa_minutes,
                "selector": "spaced-repetition",
                "coach": "dsa-coach",
                "exploration_level": exploration,
                "review_used_minutes": dsa_review_used,
                "new_used_minutes": dsa_new_used,
                "unused_minutes": max(0, dsa_minutes - dsa_review_used - dsa_new_used),
                "first_pass": first_pass_summary(data, on),
                "items": dsa_items,
            },
            {
                "id": "system-design",
                "minutes": system_design_minutes,
                "selector": "spaced-repetition",
                "coach": "system-design-coach",
                "exploration_level": exploration,
                "review_used_minutes": sd_review_used,
                "new_used_minutes": sd_new_used,
                "unused_minutes": max(0, system_design_minutes - sd_review_used - sd_new_used),
                "items": system_design_items,
            },
            {
                "id": "building",
                "minutes": building_minutes,
                "status": "requires-connected-backlog",
            },
        ],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
