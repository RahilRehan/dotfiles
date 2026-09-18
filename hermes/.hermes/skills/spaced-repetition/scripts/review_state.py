#!/usr/bin/env python3
"""Small, dependency-free helper for the learning review ledger."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
from typing import Any


DEFAULT_STATE = pathlib.Path.home() / ".hermes" / "state" / "learning.json"
RATINGS = {"again", "hard", "good", "easy"}
OUTCOMES = {"attempted", "solved", "understood", "recalled", "mastered"}
FIRST_PASS_OUTCOMES = {"solved", "understood", "recalled", "mastered"}


def load(path: pathlib.Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"state file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid state JSON: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise SystemExit("state must be an object containing an items array")
    return data


def save(path: pathlib.Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def today(value: str | None) -> dt.date:
    if value is None:
        return dt.date.today()
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        raise SystemExit("date must use YYYY-MM-DD")


def due_items(data: dict[str, Any], on: dt.date, limit: int | None) -> list[dict[str, Any]]:
    due: list[dict[str, Any]] = []
    for item in data["items"]:
        due_on = item["review"].get("due_on")
        if due_on and dt.date.fromisoformat(due_on) <= on:
            due.append(item)
    due.sort(key=lambda item: (
        -item["review"].get("lapses", 0),
        item["review"].get("due_on", ""),
        item["id"],
    ))
    return due if limit is None else due[:limit]


def item_minutes(data: dict[str, Any], item: dict[str, Any]) -> int:
    defaults = data.get("planning", {}).get("item_minutes", {})
    return int(item.get("estimated_minutes", defaults.get(item.get("kind"), defaults.get(item.get("domain"), 20))))


def first_pass_summary(data: dict[str, Any], on: dt.date) -> dict[str, Any]:
    """Return pacing information for the bounded DSA first-pass plan."""
    config = data.get("planning", {}).get("dsa", {}).get("first_pass", {})
    dsa_items = [item for item in data["items"] if item.get("domain") == "dsa"]
    completed = sum(1 for item in dsa_items if item.get("progress", {}).get("first_passed_on"))
    remaining = max(0, len(dsa_items) - completed)
    week_start = on - dt.timedelta(days=on.weekday())
    completed_this_week = sum(
        1
        for item in dsa_items
        if item.get("progress", {}).get("first_passed_on")
        and week_start <= dt.date.fromisoformat(item["progress"]["first_passed_on"]) <= on
    )
    start = dt.date.fromisoformat(config.get("start_date", on.isoformat()))
    target = dt.date.fromisoformat(config.get("target_date", on.isoformat()))
    days_left = max(0, (target - on).days + 1)
    weeks_left = max(1, (days_left + 6) // 7)
    weekly_target = max(1, (remaining + weeks_left - 1) // weeks_left) if remaining else 0
    return {
        "mode": config.get("mode", "deep-recall"),
        "start_date": start.isoformat(),
        "target_date": target.isoformat(),
        "curriculum_items": len(dsa_items),
        "first_passed_items": completed,
        "remaining_items": remaining,
        "week_start": week_start.isoformat(),
        "completed_this_week": completed_this_week,
        "configured_weekly_target": int(config.get("weekly_target_items", weekly_target)),
        "weekly_remaining": max(0, int(config.get("weekly_target_items", weekly_target)) - completed_this_week),
        "days_left": days_left,
        "weeks_left": weeks_left,
        "current_weekly_target": weekly_target,
        "study_days_per_week": int(config.get("study_days_per_week", 6)),
        "daily_cap_minutes": int(config.get("daily_cap_minutes", 75)),
        "freeze_curriculum": bool(config.get("freeze_curriculum", True)),
    }


def select_with_budget(
    data: dict[str, Any], items: list[dict[str, Any]], budget: int, ensure_one: bool = False
) -> tuple[list[dict[str, Any]], int]:
    selected: list[dict[str, Any]] = []
    used = 0
    for item in items:
        duration = item_minutes(data, item)
        if used + duration <= budget or (ensure_one and not selected):
            selected.append(item)
            used += duration
    return selected, used


def new_item_sort_key(item: dict[str, Any]) -> tuple[int, int, str]:
    """Prefer explicit priority metadata, then preserve curriculum order.

    Unknown metadata deliberately falls back to source order. This prevents
    the planner from making up difficulty or interview importance from a
    question title.
    """
    metadata = item.get("metadata", {})
    importance = {"core": 0, "high": 1, "standard": 2, "low": 3}.get(
        metadata.get("importance"), 4
    )
    order = metadata.get("curriculum_order", 10**9)
    try:
        order = int(order)
    except (TypeError, ValueError):
        order = 10**9
    return importance, order, item["id"]


def planned_items(
    data: dict[str, Any], on: dt.date, minutes: int, exploration: float,
    allowed_domains: set[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int, int]:
    if minutes <= 0:
        raise SystemExit("minutes must be greater than 0")
    if not 0 <= exploration <= 1:
        raise SystemExit("exploration must be between 0 and 1")
    due: list[dict[str, Any]] = []
    new_by_domain: dict[str, list[dict[str, Any]]] = {}
    for item in data["items"]:
        if allowed_domains is not None and item["domain"] not in allowed_domains:
            continue
        due_on = item["review"].get("due_on")
        if due_on and dt.date.fromisoformat(due_on) <= on:
            due.append(item)
        elif not due_on:
            new_by_domain.setdefault(item["domain"], []).append(item)
    due.sort(key=lambda item: (
        -item["review"].get("lapses", 0),
        item["review"].get("due_on", ""),
        item["id"],
    ))

    domain_order = data.get("domains", list(new_by_domain))
    if allowed_domains is not None:
        domain_order = [domain for domain in domain_order if domain in allowed_domains]
    for queue in new_by_domain.values():
        queue.sort(key=new_item_sort_key)

    interleaved_new: list[dict[str, Any]] = []
    while any(new_by_domain.values()):
        made_progress = False
        for domain in domain_order:
            queue = new_by_domain.get(domain, [])
            if queue:
                interleaved_new.append(queue.pop(0))
                made_progress = True
        if not made_progress:
            break

    planning = data.get("planning", {})
    minimum_review_share = float(planning.get("minimum_review_share", 0.25))
    review_share = max(minimum_review_share, 1 - exploration)
    if exploration == 0:
        review_budget = minutes
    elif due:
        minimum_review_minutes = int(planning.get("minimum_review_minutes", 30))
        review_budget = min(minutes, max(minimum_review_minutes, round(minutes * review_share)))
    else:
        review_budget = 0

    selected_due, review_used = select_with_budget(data, due, review_budget, ensure_one=bool(due))
    new_budget = 0 if exploration == 0 else max(0, minutes - review_used)
    selected_new, new_used = select_with_budget(data, interleaved_new, new_budget)
    return selected_due, selected_new, review_used, new_used


def next_interval(previous: int, rating: str, algorithm: dict[str, Any] | None = None) -> int:
    algorithm = algorithm or {}
    multipliers = algorithm.get("ratings", {})
    minimum_days = algorithm.get("minimum_days", {})
    maximum = int(algorithm.get("maximum_interval_days", 180))
    if rating == "again":
        return int(minimum_days.get("again", 1))
    if rating == "hard":
        return max(int(minimum_days.get("hard", 1)), min(maximum, round((previous or 1) * float(multipliers.get("hard", 1.2)))))
    if rating == "good":
        return max(int(minimum_days.get("good", 3)), min(maximum, round((previous or 1) * float(multipliers.get("good", 2.0)))))
    return max(int(minimum_days.get("easy", 7)), min(maximum, round((previous or 1) * float(multipliers.get("easy", 3.0)))))


def cmd_due(args: argparse.Namespace) -> None:
    data = load(args.state)
    selected = due_items(data, today(args.date), args.limit)
    print(json.dumps(selected, indent=2, ensure_ascii=False))


def cmd_plan(args: argparse.Namespace) -> None:
    data = load(args.state)
    on = today(args.date)
    configured = float(data.get("planning", {}).get("exploration_level", 0.7))
    exploration = configured if args.exploration is None else args.exploration
    configured_minutes = int(data.get("planning", {}).get("learning_block_minutes", 180))
    minutes = configured_minutes if args.minutes is None else args.minutes
    allowed_domains = set(args.domains.split(",")) if args.domains else None
    selected_due, selected_new, review_used, new_used = planned_items(
        data, on, minutes, exploration, allowed_domains
    )
    if args.limit is not None:
        selected_due = selected_due[: args.limit]
        selected_new = selected_new[: max(0, args.limit - len(selected_due))]
        review_used = sum(item_minutes(data, item) for item in selected_due)
        new_used = sum(item_minutes(data, item) for item in selected_new)
    annotated = []
    for item in selected_due:
        annotated.append({"reason": "due", "estimated_minutes": item_minutes(data, item), **item})
    for item in selected_new:
        due_on = item["review"].get("due_on")
        reason = "due" if due_on and dt.date.fromisoformat(due_on) <= on else "new"
        annotated.append({"reason": reason, "estimated_minutes": item_minutes(data, item), **item})
    planning = data.get("planning", {})
    review_share = max(float(planning.get("minimum_review_share", 0.25)), 1 - exploration)
    result = {
        "date": on.isoformat(),
        "learning_budget_minutes": minutes,
        "exploration_level": exploration,
        "review_share": round(review_share, 2),
        "review_used_minutes": review_used,
        "new_used_minutes": new_used,
        "unused_minutes": max(0, minutes - review_used - new_used),
        "items": annotated,
    }
    if args.domains is None or "dsa" in allowed_domains:
        result["dsa_first_pass"] = first_pass_summary(data, on)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_rate(args: argparse.Namespace) -> None:
    if args.rating not in RATINGS:
        raise SystemExit(f"rating must be one of: {', '.join(sorted(RATINGS))}")
    data = load(args.state)
    item = next((item for item in data["items"] if item["id"] == args.item_id), None)
    if item is None:
        raise SystemExit(f"unknown item id: {args.item_id}")
    review = item["review"]
    review_date = today(args.date)
    previous = int(review.get("interval_days", 0))
    interval = next_interval(previous, args.rating, data.get("algorithm"))
    review["last_reviewed_on"] = review_date.isoformat()
    review["last_rating"] = args.rating
    review["interval_days"] = interval
    review["due_on"] = (review_date + dt.timedelta(days=interval)).isoformat()
    review["repetitions"] = int(review.get("repetitions", 0)) + 1
    if args.rating == "again":
        review["lapses"] = int(review.get("lapses", 0)) + 1
        review["status"] = "learning"
    else:
        review["status"] = "review"
    if args.outcome:
        progress = item.setdefault("progress", {
            "attempts": 0,
            "solved_count": 0,
            "understood_count": 0,
            "recalled_count": 0,
            "mastered": False,
            "first_passed_on": None,
        })
        progress["attempts"] = int(progress.get("attempts", 0)) + 1
        if args.outcome == "solved":
            progress["solved_count"] = int(progress.get("solved_count", 0)) + 1
        elif args.outcome == "understood":
            progress["understood_count"] = int(progress.get("understood_count", 0)) + 1
        elif args.outcome == "recalled":
            progress["recalled_count"] = int(progress.get("recalled_count", 0)) + 1
        elif args.outcome == "mastered":
            progress["mastered"] = True
        progress["last_outcome"] = args.outcome
        if args.outcome in FIRST_PASS_OUTCOMES and not progress.get("first_passed_on"):
            progress["first_passed_on"] = review_date.isoformat()
    history = review.setdefault("history", [])
    if not isinstance(history, list):
        history = []
        review["history"] = history
    history.append({
        "reviewed_on": review_date.isoformat(),
        "rating": args.rating,
        "outcome": args.outcome,
        "note": args.note,
    })
    # Keep the ledger useful and bounded if a problem is reviewed many times.
    review["history"] = history[-50:]
    if args.note:
        review["last_note"] = args.note
    save(args.state, data)
    result = {"item_id": args.item_id, "rating": args.rating, "due_on": review["due_on"], "interval_days": interval}
    if args.outcome:
        result["outcome"] = args.outcome
        result["first_passed_on"] = item.get("progress", {}).get("first_passed_on")
    if args.note:
        result["note"] = args.note
    print(json.dumps(result, indent=2))


def cmd_summary(args: argparse.Namespace) -> None:
    data = load(args.state)
    counts: dict[str, int] = {}
    progress_counts = {
        "first_passed": 0,
        "solved": 0,
        "understood": 0,
        "recalled": 0,
        "mastered": 0,
    }
    for item in data["items"]:
        status = item["review"].get("status", "new")
        counts[status] = counts.get(status, 0) + 1
        progress = item.get("progress", {})
        if progress.get("first_passed_on"):
            progress_counts["first_passed"] += 1
        if int(progress.get("solved_count", 0)) > 0:
            progress_counts["solved"] += 1
        if int(progress.get("understood_count", 0)) > 0:
            progress_counts["understood"] += 1
        if int(progress.get("recalled_count", 0)) > 0:
            progress_counts["recalled"] += 1
        if progress.get("mastered"):
            progress_counts["mastered"] += 1
    print(json.dumps({"total": len(data["items"]), "statuses": counts, "progress": progress_counts}, indent=2))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    root.add_argument("--state", type=pathlib.Path, default=DEFAULT_STATE)
    sub = root.add_subparsers(dest="command", required=True)
    due = sub.add_parser("due")
    due.add_argument("--date")
    due.add_argument("--limit", type=int, default=10)
    due.set_defaults(func=cmd_due)
    plan = sub.add_parser("plan")
    plan.add_argument("--date")
    plan.add_argument("--minutes", type=int)
    plan.add_argument("--limit", type=int)
    plan.add_argument("--exploration", type=float)
    plan.add_argument("--domains", help="comma-separated domain filter")
    plan.set_defaults(func=cmd_plan)
    rate = sub.add_parser("rate")
    rate.add_argument("item_id")
    rate.add_argument("rating", choices=sorted(RATINGS))
    rate.add_argument("--date")
    rate.add_argument("--outcome", choices=sorted(OUTCOMES), help="record the result separately from recall rating")
    rate.add_argument("--note", help="optional short coaching note")
    rate.set_defaults(func=cmd_rate)
    summary = sub.add_parser("summary")
    summary.set_defaults(func=cmd_summary)
    return root


if __name__ == "__main__":
    parsed = parser().parse_args()
    parsed.func(parsed)
