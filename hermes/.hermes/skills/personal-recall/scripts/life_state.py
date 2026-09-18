#!/usr/bin/env python3
"""Deterministic state helper for personal memories and growth insights."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import unicodedata
from typing import Any, Callable


SKILLS_DIR = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILLS_DIR / "spaced-repetition" / "scripts"))
from review_state import next_interval  # noqa: E402


HERMES_HOME = pathlib.Path(os.environ.get("HERMES_HOME", pathlib.Path.home() / ".hermes"))
DEFAULT_LIFE_DIR = HERMES_HOME / "state" / "life"
DEFAULT_MEMORIES = DEFAULT_LIFE_DIR / "memories.json"
DEFAULT_INSIGHTS = DEFAULT_LIFE_DIR / "insights.json"
TIMEZONE = "Asia/Kolkata"

MEMORY_KINDS = {
    "article", "book", "conversation", "decision", "event", "experience",
    "idea", "movie", "person", "place", "show", "trip", "other",
}
IMPORTANCE = {"low", "normal", "high"}
RECALL_RATINGS = {
    "forgot": "again",
    "partial": "hard",
    "remembered": "good",
    "effortless": "easy",
}
APPLICATION_STATUSES = {"not-started", "planned", "tried", "applied", "rejected"}
ALGORITHM = {
    "ratings": {"hard": 1.2, "good": 2.0, "easy": 3.0},
    "minimum_days": {"again": 1, "hard": 1, "good": 3, "easy": 7},
    "maximum_interval_days": 180,
}


def utc_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def date_value(value: str | None) -> dt.date:
    if value is None:
        return dt.date.today()
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        raise SystemExit("date must use YYYY-MM-DD")


def comma_values(value: str | None) -> list[str]:
    return [part.strip() for part in (value or "").split(",") if part.strip()]


def normalized(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "item"


def stable_id(prefix: str, *parts: str) -> str:
    canonical = "|".join(part.strip().lower() for part in parts)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:10]
    label = normalized(parts[1] if len(parts) > 1 else parts[0])[:48]
    return f"{prefix}:{label}:{digest}"


def empty_memories() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "timezone": TIMEZONE,
        "algorithm": ALGORITHM,
        "items": [],
    }


def empty_insights() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "timezone": TIMEZONE,
        "algorithm": ALGORITHM,
        "items": [],
    }


def load(path: pathlib.Path, factory: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return factory()
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid state JSON in {path}: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise SystemExit(f"{path} must contain an object with an items array")
    data.setdefault("schema_version", 1)
    data.setdefault("timezone", TIMEZONE)
    data.setdefault("algorithm", ALGORITHM)
    return data


def save(path: pathlib.Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def find_item(data: dict[str, Any], item_id: str) -> dict[str, Any]:
    item = next((candidate for candidate in data["items"] if candidate["id"] == item_id), None)
    if item is None:
        raise SystemExit(f"unknown item id: {item_id}")
    return item


def review_state(first_due: dt.date | None) -> dict[str, Any]:
    return {
        "status": "learning" if first_due else "new",
        "due_on": first_due.isoformat() if first_due else None,
        "last_reviewed_on": None,
        "last_rating": None,
        "interval_days": 1 if first_due else 0,
        "repetitions": 0,
        "lapses": 0,
        "history": [],
    }


def append_bounded(history: list[dict[str, Any]], event: dict[str, Any]) -> None:
    history.append(event)
    del history[:-50]


def review_item(
    item: dict[str, Any],
    data: dict[str, Any],
    rating: str,
    on: dt.date,
    note: str | None,
) -> dict[str, Any]:
    review = item["review"]
    interval = next_interval(
        int(review.get("interval_days", 0)),
        RECALL_RATINGS[rating],
        data.get("algorithm"),
    )
    review.update({
        "last_reviewed_on": on.isoformat(),
        "last_rating": rating,
        "interval_days": interval,
        "due_on": (on + dt.timedelta(days=interval)).isoformat(),
        "repetitions": int(review.get("repetitions", 0)) + 1,
        "status": "learning" if rating == "forgot" else "review",
    })
    if rating == "forgot":
        review["lapses"] = int(review.get("lapses", 0)) + 1
    append_bounded(review.setdefault("history", []), {
        "event": "reviewed",
        "reviewed_on": on.isoformat(),
        "rating": rating,
        "note": note,
        "next_due_on": review["due_on"],
    })
    item["updated_at"] = utc_timestamp()
    return {
        "item_id": item["id"],
        "rating": rating,
        "interval_days": interval,
        "due_on": review["due_on"],
    }


def memory_payload(item: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "id", "kind", "title", "occurred_on", "summary", "details", "people",
        "tags", "source_path", "importance", "review",
    )
    return {key: item.get(key) for key in keys}


def insight_payload(item: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "id", "book", "idea", "application", "why_for_rahil", "source",
        "source_type", "source_path", "chapter", "page", "application_status",
        "delivery", "review",
    )
    return {key: item.get(key) for key in keys}


def cmd_init(args: argparse.Namespace) -> None:
    memories_created = not args.memories.exists()
    insights_created = not args.insights.exists()
    if memories_created:
        save(args.memories, empty_memories())
    if insights_created:
        save(args.insights, empty_insights())
    print(json.dumps({
        "memories": str(args.memories),
        "memories_created": memories_created,
        "insights": str(args.insights),
        "insights_created": insights_created,
    }, indent=2))


def cmd_capture_memory(args: argparse.Namespace) -> None:
    on = date_value(args.date)
    occurred_on = date_value(args.occurred_on or args.date)
    data = load(args.memories, empty_memories)
    item_id = stable_id("memory", args.kind, args.title, occurred_on.isoformat())
    item = next((entry for entry in data["items"] if entry["id"] == item_id), None)
    created = item is None
    if created:
        item = {
            "id": item_id,
            "kind": args.kind,
            "title": args.title.strip(),
            "occurred_on": occurred_on.isoformat(),
            "summary": args.summary,
            "details": args.details,
            "people": comma_values(args.people),
            "tags": comma_values(args.tags),
            "source_path": args.source_path,
            "importance": args.importance,
            "created_at": utc_timestamp(),
            "updated_at": utc_timestamp(),
            "review": review_state(on + dt.timedelta(days=1)),
            "capture_history": [],
        }
        data["items"].append(item)
    else:
        for key in ("summary", "details", "source_path"):
            value = getattr(args, key)
            if value:
                item[key] = value
        for key in ("people", "tags"):
            item[key] = sorted(set(item.get(key, [])) | set(comma_values(getattr(args, key))))
        if args.importance != "normal" or not item.get("importance"):
            item["importance"] = args.importance
        item["updated_at"] = utc_timestamp()
    append_bounded(item.setdefault("capture_history", []), {
        "event": "captured" if created else "updated",
        "at": utc_timestamp(),
        "note": args.note,
    })
    save(args.memories, data)
    verified = find_item(load(args.memories, empty_memories), item_id)
    print(json.dumps({
        "action": "created" if created else "updated",
        "memory": memory_payload(verified),
    }, indent=2, ensure_ascii=False))


def cmd_due_memories(args: argparse.Namespace) -> None:
    on = date_value(args.date)
    data = load(args.memories, empty_memories)
    rank = {"high": 0, "normal": 1, "low": 2}
    items = [
        item for item in data["items"]
        if item["review"].get("due_on")
        and dt.date.fromisoformat(item["review"]["due_on"]) <= on
        and item["review"].get("status") != "archived"
    ]
    items.sort(key=lambda item: (
        rank.get(item.get("importance", "normal"), 1),
        -int(item["review"].get("lapses", 0)),
        item["review"]["due_on"],
        item["id"],
    ))
    print(json.dumps({
        "date": on.isoformat(),
        "count": min(len(items), args.limit),
        "items": [memory_payload(item) for item in items[:args.limit]],
    }, indent=2, ensure_ascii=False))


def cmd_review_memory(args: argparse.Namespace) -> None:
    data = load(args.memories, empty_memories)
    item = find_item(data, args.item_id)
    result = review_item(item, data, args.rating, date_value(args.date), args.answer)
    save(args.memories, data)
    result["memory"] = memory_payload(
        find_item(load(args.memories, empty_memories), args.item_id)
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_get_memory(args: argparse.Namespace) -> None:
    data = load(args.memories, empty_memories)
    print(json.dumps(memory_payload(find_item(data, args.item_id)), indent=2, ensure_ascii=False))


def cmd_search_memories(args: argparse.Namespace) -> None:
    data = load(args.memories, empty_memories)
    query = args.query.casefold()
    matches = []
    for item in data["items"]:
        if args.kind and item["kind"] != args.kind:
            continue
        haystack = " ".join([
            item.get("title", ""),
            item.get("summary") or "",
            item.get("details") or "",
            " ".join(item.get("people", [])),
            " ".join(item.get("tags", [])),
        ]).casefold()
        if query in haystack:
            matches.append(item)
    matches.sort(key=lambda item: (item["occurred_on"], item["updated_at"]), reverse=True)
    print(json.dumps({
        "query": args.query,
        "count": min(len(matches), args.limit),
        "items": [memory_payload(item) for item in matches[:args.limit]],
    }, indent=2, ensure_ascii=False))


def cmd_add_insight(args: argparse.Namespace) -> None:
    data = load(args.insights, empty_insights)
    item_id = stable_id("insight", args.book, args.idea)
    item = next((entry for entry in data["items"] if entry["id"] == item_id), None)
    created = item is None
    if created:
        item = {
            "id": item_id,
            "book": args.book.strip(),
            "idea": args.idea.strip(),
            "application": args.application,
            "why_for_rahil": args.why_for_rahil,
            "source": args.source.strip(),
            "source_type": args.source_type,
            "source_path": args.source_path,
            "chapter": args.chapter,
            "page": args.page,
            "application_status": "not-started",
            "created_at": utc_timestamp(),
            "updated_at": utc_timestamp(),
            "delivery": {
                "shown_count": 0,
                "first_shown_on": None,
                "last_shown_on": None,
            },
            "review": review_state(None),
        }
        data["items"].append(item)
    else:
        for key in ("application", "why_for_rahil", "source_path", "chapter", "page"):
            value = getattr(args, key)
            if value:
                item[key] = value
        item["source"] = args.source.strip()
        item["source_type"] = args.source_type
        item["updated_at"] = utc_timestamp()
    save(args.insights, data)
    verified = find_item(load(args.insights, empty_insights), item_id)
    print(json.dumps({
        "action": "created" if created else "updated",
        "insight": insight_payload(verified),
    }, indent=2, ensure_ascii=False))


def cmd_next_insights(args: argparse.Namespace) -> None:
    on = date_value(args.date)
    data = load(args.insights, empty_insights)
    due, new = [], []
    for item in data["items"]:
        if item["review"].get("status") in {"archived", "rejected"}:
            continue
        due_on = item["review"].get("due_on")
        if due_on and dt.date.fromisoformat(due_on) <= on:
            due.append(item)
        elif int(item["delivery"].get("shown_count", 0)) == 0:
            new.append(item)
    due.sort(key=lambda item: (
        -int(item["review"].get("lapses", 0)),
        item["review"]["due_on"],
        item["id"],
    ))
    new.sort(key=lambda item: (item["created_at"], item["id"]))
    selected = [("due", item) for item in due] + [("new", item) for item in new]
    print(json.dumps({
        "date": on.isoformat(),
        "count": min(len(selected), args.limit),
        "items": [
            {"reason": reason, **insight_payload(item)}
            for reason, item in selected[:args.limit]
        ],
    }, indent=2, ensure_ascii=False))


def cmd_show_insight(args: argparse.Namespace) -> None:
    on = date_value(args.date)
    data = load(args.insights, empty_insights)
    item = find_item(data, args.item_id)
    delivery = item["delivery"]
    delivery["shown_count"] = int(delivery.get("shown_count", 0)) + 1
    delivery["first_shown_on"] = delivery.get("first_shown_on") or on.isoformat()
    delivery["last_shown_on"] = on.isoformat()
    review = item["review"]
    if not review.get("due_on") or dt.date.fromisoformat(review["due_on"]) <= on:
        review["status"] = "learning"
        review["interval_days"] = max(3, int(review.get("interval_days", 0)))
        review["due_on"] = (on + dt.timedelta(days=review["interval_days"])).isoformat()
    append_bounded(review.setdefault("history", []), {
        "event": "shown",
        "shown_on": on.isoformat(),
        "next_due_on": review["due_on"],
    })
    item["updated_at"] = utc_timestamp()
    save(args.insights, data)
    print(json.dumps(insight_payload(
        find_item(load(args.insights, empty_insights), args.item_id)
    ), indent=2, ensure_ascii=False))


def cmd_review_insight(args: argparse.Namespace) -> None:
    data = load(args.insights, empty_insights)
    item = find_item(data, args.item_id)
    result = review_item(item, data, args.rating, date_value(args.date), args.note)
    if args.application_status:
        item["application_status"] = args.application_status
        if args.application_status == "rejected":
            item["review"]["status"] = "rejected"
            item["review"]["due_on"] = None
            result["due_on"] = None
    save(args.insights, data)
    result["insight"] = insight_payload(
        find_item(load(args.insights, empty_insights), args.item_id)
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_summary(args: argparse.Namespace) -> None:
    on = date_value(args.date)
    memories = load(args.memories, empty_memories)
    insights = load(args.insights, empty_insights)
    memory_due = sum(
        1 for item in memories["items"]
        if item["review"].get("due_on")
        and dt.date.fromisoformat(item["review"]["due_on"]) <= on
        and item["review"].get("status") != "archived"
    )
    insight_due = sum(
        1 for item in insights["items"]
        if item["review"].get("due_on")
        and dt.date.fromisoformat(item["review"]["due_on"]) <= on
        and item["review"].get("status") not in {"archived", "rejected"}
    )
    insight_new = sum(
        1 for item in insights["items"]
        if int(item["delivery"].get("shown_count", 0)) == 0
        and item["review"].get("status") not in {"archived", "rejected"}
    )
    print(json.dumps({
        "date": on.isoformat(),
        "memories": {"total": len(memories["items"]), "due": memory_due},
        "insights": {"total": len(insights["items"]), "due": insight_due, "new": insight_new},
    }, indent=2))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    root.add_argument("--memories", type=pathlib.Path, default=DEFAULT_MEMORIES)
    root.add_argument("--insights", type=pathlib.Path, default=DEFAULT_INSIGHTS)
    sub = root.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.set_defaults(func=cmd_init)

    capture = sub.add_parser("capture-memory")
    capture.add_argument("--kind", required=True, choices=sorted(MEMORY_KINDS))
    capture.add_argument("--title", required=True)
    capture.add_argument("--occurred-on")
    capture.add_argument("--date")
    capture.add_argument("--summary")
    capture.add_argument("--details")
    capture.add_argument("--people")
    capture.add_argument("--tags")
    capture.add_argument("--source-path")
    capture.add_argument("--importance", choices=sorted(IMPORTANCE), default="normal")
    capture.add_argument("--note")
    capture.set_defaults(func=cmd_capture_memory)

    due = sub.add_parser("due-memories")
    due.add_argument("--date")
    due.add_argument("--limit", type=int, default=3)
    due.set_defaults(func=cmd_due_memories)

    review_memory = sub.add_parser("review-memory")
    review_memory.add_argument("item_id")
    review_memory.add_argument("rating", choices=sorted(RECALL_RATINGS))
    review_memory.add_argument("--date")
    review_memory.add_argument("--answer")
    review_memory.set_defaults(func=cmd_review_memory)

    get_memory = sub.add_parser("get-memory")
    get_memory.add_argument("item_id")
    get_memory.set_defaults(func=cmd_get_memory)

    search = sub.add_parser("search-memories")
    search.add_argument("query")
    search.add_argument("--kind", choices=sorted(MEMORY_KINDS))
    search.add_argument("--limit", type=int, default=10)
    search.set_defaults(func=cmd_search_memories)

    add_insight = sub.add_parser("add-insight")
    add_insight.add_argument("--book", required=True)
    add_insight.add_argument("--idea", required=True)
    add_insight.add_argument("--application")
    add_insight.add_argument("--why-for-rahil")
    add_insight.add_argument("--source", required=True)
    add_insight.add_argument("--source-type", choices=["book", "obsidian", "user", "web"], required=True)
    add_insight.add_argument("--source-path")
    add_insight.add_argument("--chapter")
    add_insight.add_argument("--page")
    add_insight.set_defaults(func=cmd_add_insight)

    next_insight = sub.add_parser("next-insights")
    next_insight.add_argument("--date")
    next_insight.add_argument("--limit", type=int, default=1)
    next_insight.set_defaults(func=cmd_next_insights)

    show = sub.add_parser("show-insight")
    show.add_argument("item_id")
    show.add_argument("--date")
    show.set_defaults(func=cmd_show_insight)

    review_insight = sub.add_parser("review-insight")
    review_insight.add_argument("item_id")
    review_insight.add_argument("rating", choices=sorted(RECALL_RATINGS))
    review_insight.add_argument("--date")
    review_insight.add_argument("--application-status", choices=sorted(APPLICATION_STATUSES))
    review_insight.add_argument("--note")
    review_insight.set_defaults(func=cmd_review_insight)

    summary = sub.add_parser("summary")
    summary.add_argument("--date")
    summary.set_defaults(func=cmd_summary)
    return root


if __name__ == "__main__":
    args = parser().parse_args()
    args.func(args)
