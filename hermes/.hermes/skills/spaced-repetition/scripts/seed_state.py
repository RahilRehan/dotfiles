#!/usr/bin/env python3
"""Seed the durable learning ledger from the normalized curriculum files."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Any


def extract_array(path: pathlib.Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    start = text.find("[")
    end = text.rfind("]")
    if start < 0 or end < start:
        raise SystemExit(f"no JSON array found in {path}")
    try:
        value = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid curriculum JSON in {path}: {exc}")
    if not isinstance(value, list):
        raise SystemExit(f"curriculum must be a JSON array: {path}")
    return value


def slug(value: str) -> str:
    value = value.lower().replace("&", "and")
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", value))


def estimate_minutes(domain: str, kind: str, entry: dict[str, Any] | None = None) -> int:
    if domain == "dsa":
        difficulty = (entry or {}).get("metadata", {}).get("difficulty")
        return {"Easy": 20, "Medium": 35, "Hard": 60}.get(difficulty, 35)
    return {"topic": 20, "design-question": 45, "case-study": 35}.get(kind, 20)


def dsa_metadata(index: int, entry: dict[str, Any]) -> dict[str, Any]:
    """Build conservative DSA metadata, preserving source-backed fields.

    The curriculum may provide topic, difficulty, and source-list membership.
    Missing fields remain empty rather than being guessed from a slug.
    """
    provided = entry.get("metadata", {})
    if not isinstance(provided, dict):
        provided = {}
    metadata = {
        "status": provided.get(
            "status",
            "historical-unverified"
            if entry.get("platform") == "obsidian"
            else "unclassified",
        ),
        "curriculum_order": index,
        "topic": provided.get("topic"),
        "patterns": provided.get("patterns", []),
        "difficulty": provided.get("difficulty"),
        "importance": provided.get("importance"),
        "prerequisites": provided.get("prerequisites", []),
        "source_sets": provided.get("source_sets", []),
    }
    return metadata


def system_design_metadata(index: int) -> dict[str, Any]:
    """Metadata that is safe to derive from the normalized source order."""
    return {
        "status": "source-derived",
        "curriculum_order": index,
    }


def merge_defaults(default: Any, existing: Any) -> Any:
    """Preserve user-tuned configuration while adding new default keys."""
    if isinstance(default, dict) and isinstance(existing, dict):
        merged = {key: value for key, value in default.items()}
        for key, value in existing.items():
            merged[key] = merge_defaults(merged[key], value) if key in merged else value
        return merged
    return existing


def seed(dsa_path: pathlib.Path, system_design_path: pathlib.Path) -> dict[str, Any]:
    dsa = extract_array(dsa_path)
    system_design = extract_array(system_design_path)
    items: list[dict[str, Any]] = []

    for index, entry in enumerate(dsa):
        platform = entry["platform"]
        question = entry["question"]
        items.append(
            {
                "id": f"dsa:{platform}:{slug(question)}",
                "domain": "dsa",
                "kind": "problem",
                "source": platform,
                "label": question,
                "metadata": dsa_metadata(index, entry),
                "estimated_minutes": estimate_minutes("dsa", "problem", entry),
                "progress": {
                    "attempts": 0,
                    "solved_count": 0,
                    "understood_count": 0,
                    "recalled_count": 0,
                    "mastered": False,
                    "first_passed_on": None,
                },
                "review": {},
            }
        )

    for index, entry in enumerate(system_design):
        source = entry["source"]
        label = entry["topic"]
        if source == "hello-interview":
            section = entry["section"]
            items.append(
                {
                    "id": f"system-design:hello-interview:{slug(section)}:{slug(label)}",
                    "domain": "system-design",
                    "kind": entry["type"],
                    "source": source,
                    "section": section,
                    "label": label,
                    "metadata": system_design_metadata(index),
                    "estimated_minutes": estimate_minutes("system-design", entry["type"]),
                    "progress": {
                        "attempts": 0,
                        "solved_count": 0,
                        "understood_count": 0,
                        "recalled_count": 0,
                        "mastered": False,
                        "first_passed_on": None,
                    },
                    "review": {},
                }
            )
        else:
            part = entry["part"]
            module = entry["module"]
            items.append(
                {
                    "id": f"system-design:fanout:{slug(part)}:{slug(module)}:{slug(label)}",
                    "domain": "system-design",
                    "kind": entry["type"],
                    "source": source,
                    "part": part,
                    "module": module,
                    "label": label,
                    "metadata": system_design_metadata(index),
                    "estimated_minutes": estimate_minutes("system-design", entry["type"]),
                    "progress": {
                        "attempts": 0,
                        "solved_count": 0,
                        "understood_count": 0,
                        "recalled_count": 0,
                        "mastered": False,
                        "first_passed_on": None,
                    },
                    "review": {},
                }
            )

    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate stable IDs generated")

    return {
        "schema_version": 2,
        "timezone": "Asia/Kolkata",
        "algorithm": {
            "name": "adaptive-intervals-v1",
            "ratings": {"again": 1, "hard": 1.2, "good": 2.0, "easy": 3.0},
            "minimum_days": {"again": 1, "hard": 1, "good": 3, "easy": 7},
            "maximum_interval_days": 180,
        },
        "planning": {
            "exploration_level": 0.7,
            "minimum_review_share": 0.25,
            "learning_block_minutes": 160,
            "minimum_review_minutes": 30,
            "communication_block_minutes": 25,
            "dsa": {
                "first_pass": {
                    "start_date": "2026-09-14",
                    "target_date": "2027-02-14",
                    "weekly_target_items": 19,
                    "study_days_per_week": 6,
                    "daily_cap_minutes": 75,
                    "mode": "deep-recall",
                    "freeze_curriculum": True,
                },
                "difficulty_minutes": {
                    "Easy": 20,
                    "Medium": 35,
                    "Hard": 60,
                    "unknown": 35,
                },
            },
            "daily_schedule": {
                "total_minutes": 240,
                "news_minutes": 20,
                "learning_minutes": 160,
                "dsa_minutes": 75,
                "system_design_minutes": 60,
                "building_minutes": 60,
            },
            "item_minutes": {
                "problem": 35,
                "topic": 20,
                "design-question": 45,
                "case-study": 35,
                "communication": 20,
            },
        },
        "domains": ["dsa", "system-design", "communication"],
        "items": items,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dsa", type=pathlib.Path, required=True)
    parser.add_argument("--system-design", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    state = seed(args.dsa, args.system_design)
    if args.output.exists():
        try:
            previous = json.loads(args.output.read_text(encoding="utf-8"))
            previous_reviews = {
                item["id"]: item.get("review", {})
                for item in previous.get("items", [])
            }
            for item in state["items"]:
                item["review"] = previous_reviews.get(item["id"], {})
                previous_item = next(
                    (candidate for candidate in previous.get("items", []) if candidate.get("id") == item["id"]),
                    {},
                )
                if isinstance(previous_item.get("progress"), dict):
                    item["progress"] = merge_defaults(item["progress"], previous_item["progress"])
            for key in ("timezone", "algorithm", "planning", "domains"):
                if key in previous:
                    state[key] = merge_defaults(state[key], previous[key])
        except (OSError, json.JSONDecodeError, AttributeError, TypeError, KeyError):
            raise SystemExit(f"cannot safely merge existing state: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({"output": str(args.output), "items": len(state["items"])}))


if __name__ == "__main__":
    main()
