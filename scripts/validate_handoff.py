#!/usr/bin/env python3
"""Validate a Gemini-to-Codex article handoff without changing the article."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ALLOWED_STEPS = {
    "structure_gate",
    "ai_check",
    "title_and_digest",
    "cover",
    "share_copy",
    "charcoal_layout",
}
REQUIRED_FILES = ("brief.md", "evidence.md", "outline.md", "title-options.md", "article.md")


def fail(errors: list[str]) -> None:
    for error in errors:
        print(f"Error: {error}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    root = args.root.resolve()
    handoff_path = args.handoff.resolve()
    if not handoff_path.is_file():
        fail([f"handoff file does not exist: {handoff_path}"])
    try:
        data = json.loads(handoff_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail([f"invalid handoff JSON: {exc}"])
    if not isinstance(data, dict):
        fail(["handoff must be a JSON object"])

    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("status") != "ready_for_codex":
        errors.append("status must be ready_for_codex")
    draft_delivery = data.get("draft_delivery", False)
    if not isinstance(draft_delivery, bool):
        errors.append("draft_delivery must be a boolean")

    article_dir_value = data.get("article_dir")
    if not isinstance(article_dir_value, str) or not article_dir_value:
        errors.append("article_dir must be a non-empty repository-relative path")
        article_dir = None
    else:
        candidate = (root / article_dir_value).resolve()
        articles_root = (root / "articles").resolve()
        if candidate == articles_root or articles_root not in candidate.parents:
            errors.append("article_dir must stay inside this repository's articles/ directory")
            article_dir = None
        else:
            article_dir = candidate

    requested_steps = data.get("requested_steps")
    if not isinstance(requested_steps, list) or not requested_steps or not all(isinstance(item, str) for item in requested_steps):
        errors.append("requested_steps must be a non-empty list of strings")
    else:
        invalid_steps = sorted(set(requested_steps) - ALLOWED_STEPS)
        if invalid_steps:
            errors.append("unsupported requested_steps: " + ", ".join(invalid_steps))
        if draft_delivery is True and "charcoal_layout" not in requested_steps:
            errors.append("draft_delivery requires the charcoal_layout step")

    if article_dir:
        missing = [name for name in REQUIRED_FILES if not (article_dir / name).is_file()]
        if missing:
            errors.append("article package is incomplete: " + ", ".join(missing))
        if handoff_path.parent != article_dir:
            errors.append("handoff.json must live in article_dir")

    if errors:
        fail(errors)
    print(f"Gemini handoff validated: {article_dir}")


if __name__ == "__main__":
    main()
