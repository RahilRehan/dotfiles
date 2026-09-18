#!/usr/bin/env python3
"""Small, dependency-free state store for the Daily Guide.

The learning ledger owns learning progress. This file owns only the daily
execution state: what was planned, completed, skipped, shortened, or deferred.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
from typing import Any


DEFAULT_STATE = pathlib.Path.home() / ".hermes" / "state" / "daily.json"
BLOCKS = {"news", "communication", "dsa", "system-design", "building"}
ENERGY = {"low", "normal", "high"}


def load(path: pathlib.Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"schema_version": 1, "timezone": "Asia/Kolkata", "days": {}}
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid daily state JSON: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("days", {}), dict):
        raise SystemExit("daily state must be an object containing a days map")
    data.setdefault("schema_version", 1)
    data.setdefault("timezone", "Asia/Kolkata")
    return data


def save(path: pathlib.Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def date_value(value: str | None) -> str:
    if value is None:
        return dt.date.today().isoformat()
    try:
        return dt.date.fromisoformat(value).isoformat()
    except ValueError:
        raise SystemExit("date must use YYYY-MM-DD")


def timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def day(data: dict[str, Any], value: str) -> dict[str, Any]:
    days = data.setdefault("days", {})
    return days.setdefault(value, {
        "planned": {},
        "completed": [],
        "skipped": [],
        "shortened": [],
        "energy": None,
        "notes": [],
        "updated_at": None,
    })


def validate_block(value: str) -> None:
    if value not in BLOCKS:
        raise SystemExit(f"block must be one of: {', '.join(sorted(BLOCKS))}")


def mark(data: dict[str, Any], date: str, block: str, field: str, note: str | None) -> None:
    validate_block(block)
    record = day(data, date)
    values = record.setdefault(field, [])
    if block not in values:
        values.append(block)
    if note:
        record.setdefault("notes", []).append({"at": timestamp(), "text": note})
    record["updated_at"] = timestamp()


def cmd_start(args: argparse.Namespace) -> None:
    if args.items and len(args.block) != 1:
        raise SystemExit("--items can be used with exactly one --block")
    data = load(args.state)
    date = date_value(args.date)
    record = day(data, date)
    for block in args.block:
        validate_block(block)
        record.setdefault("planned", {}).setdefault(block, {})
        if args.items:
            record["planned"][block]["items"] = [item for item in args.items.split(",") if item]
    record["updated_at"] = timestamp()
    save(args.state, data)
    print(json.dumps({"date": date, "planned": record["planned"]}, indent=2, ensure_ascii=False))


def cmd_mark(args: argparse.Namespace) -> None:
    data = load(args.state)
    date = date_value(args.date)
    mark(data, date, args.block, args.field, args.note)
    save(args.state, data)
    print(json.dumps({"date": date, "block": args.block, "status": args.field}, indent=2))


def cmd_energy(args: argparse.Namespace) -> None:
    if args.value not in ENERGY:
        raise SystemExit(f"energy must be one of: {', '.join(sorted(ENERGY))}")
    data = load(args.state)
    date = date_value(args.date)
    record = day(data, date)
    record["energy"] = args.value
    record["updated_at"] = timestamp()
    save(args.state, data)
    print(json.dumps({"date": date, "energy": args.value}, indent=2))


def cmd_show(args: argparse.Namespace) -> None:
    data = load(args.state)
    date = date_value(args.date)
    print(json.dumps({"date": date, **day(data, date)}, indent=2, ensure_ascii=False))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    root.add_argument("--state", type=pathlib.Path, default=DEFAULT_STATE)
    sub = root.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="record the blocks/items planned for a day")
    start.add_argument("--date")
    start.add_argument("--block", action="append", required=True)
    start.add_argument("--items", help="comma-separated item ids for the selected block")
    start.set_defaults(func=cmd_start)

    for name, field in (("complete", "completed"), ("skip", "skipped"), ("shorten", "shortened")):
        command = sub.add_parser(name)
        command.add_argument("--date")
        command.add_argument("--block", required=True)
        command.add_argument("--note")
        command.set_defaults(func=cmd_mark, field=field)

    energy = sub.add_parser("energy")
    energy.add_argument("value", choices=sorted(ENERGY))
    energy.add_argument("--date")
    energy.set_defaults(func=cmd_energy)

    show = sub.add_parser("show")
    show.add_argument("--date")
    show.set_defaults(func=cmd_show)
    return root


if __name__ == "__main__":
    parsed = parser().parse_args()
    parsed.func(parsed)
