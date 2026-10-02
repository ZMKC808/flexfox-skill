#!/usr/bin/env python3
"""Verify the artifact gates for one FlexFox article production run.

This runner deliberately does not call an LLM. It makes a portable article
workflow observable: the host model creates editorial artifacts, while this
script blocks layout and WeChat delivery unless the latest draft has a fresh,
independently recorded editorial review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


REVIEW_FILE = "review.json"
REQUIRED_REVIEW_KEYS = {
    "schema_version",
    "article_sha256",
    "review_round",
    "reviewer",
    "status",
    "fact_checks",
    "findings",
    "summary",
}


def process_dir(article_dir: Path) -> Path:
    candidate = article_dir / "过程"
    return candidate if candidate.is_dir() else article_dir


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def required_fact_ids(brief: Path) -> list[str]:
    if not brief.is_file():
        return []
    return re.findall(r"\[必写\]\s*(E\d{2,})\b", brief.read_text(encoding="utf-8"))


def load_review(article_dir: Path) -> tuple[dict[str, Any] | None, list[str]]:
    path = process_dir(article_dir) / REVIEW_FILE
    if not path.is_file():
        return None, [f"缺少 {REVIEW_FILE}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"{REVIEW_FILE} 不是合法 JSON：{exc}"]
    if not isinstance(data, dict):
        return None, [f"{REVIEW_FILE} 必须是 JSON 对象"]
    return data, []


def review_errors(article_dir: Path, require_pass: bool) -> list[str]:
    article = article_dir / "article.md"
    review, errors = load_review(article_dir)
    if review is None:
        return errors
    missing = sorted(REQUIRED_REVIEW_KEYS - set(review))
    if missing:
        errors.append(f"{REVIEW_FILE} 缺少字段：{', '.join(missing)}")
        return errors
    if not article.is_file():
        errors.append("缺少 article.md")
        return errors
    if review["article_sha256"] != sha256(article):
        errors.append("审稿对应的正文版本已过期；修改正文后必须重新审稿")
    if review["status"] not in {"pass", "needs_revision"}:
        errors.append("review.status 必须为 pass 或 needs_revision")
    if not isinstance(review["review_round"], int) or review["review_round"] < 1:
        errors.append("review_round 必须是从 1 开始的整数")
    if not isinstance(review["reviewer"], str) or not review["reviewer"].strip():
        errors.append("reviewer 必须记录独立审稿角色或会话")
    if not isinstance(review["fact_checks"], list) or not isinstance(review["findings"], list):
        errors.append("fact_checks 与 findings 必须为数组")
        return errors
    checked_facts = {
        item.get("fact_id")
        for item in review["fact_checks"]
        if isinstance(item, dict) and item.get("status") == "pass"
    }
    missing_facts = [fact for fact in required_fact_ids(process_dir(article_dir) / "brief.md") if fact not in checked_facts]
    if missing_facts:
        errors.append("必写事实未逐项通过审稿：" + ", ".join(missing_facts))
    blocking = [
        item
        for item in review["findings"]
        if isinstance(item, dict) and item.get("severity") in {"blocker", "major"}
    ]
    if review["status"] == "needs_revision":
        errors.append("编辑审稿要求返工")
    if require_pass and review["status"] != "pass":
        errors.append("编辑审稿尚未通过")
    if require_pass and blocking:
        errors.append("审稿仍有 blocker/major 问题，不能进入下游交付")
    return errors


def structure_gate(article_dir: Path) -> tuple[bool, str]:
    article = article_dir / "article.md"
    if not article.is_file():
        return False, "缺少 article.md"
    command = [sys.executable, str(Path(__file__).with_name("validate_article.py")), "--article", str(article)]
    process = process_dir(article_dir)
    source_index = process / "来源" / "index.json"
    if not source_index.is_file():
        source_index = article_dir / "sources" / "index.json"
    if source_index.is_file():
        command.extend(["--sources", str(source_index)])
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    report = process / "structure-check.json"
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "结构门禁失败"
        return False, detail
    if not report.is_file():
        return False, "结构门禁未生成 structure-check.json"
    try:
        passed = json.loads(report.read_text(encoding="utf-8")).get("status") == "pass"
    except json.JSONDecodeError:
        return False, "structure-check.json 无法读取"
    return passed, result.stdout.strip()


def status(article_dir: Path, *, require_review_pass: bool) -> tuple[str, list[str]]:
    process = process_dir(article_dir)
    errors = [f"缺少 过程/{name}" for name in ("brief.md", "evidence.md", "outline.md") if not (process / name).is_file()]
    if not (article_dir / "article.md").is_file():
        errors.append("缺少 article.md")
    if errors:
        return "blocked", errors
    passed, detail = structure_gate(article_dir)
    if not passed:
        return "needs_revision", [detail]
    if not (process / REVIEW_FILE).is_file() and not require_review_pass:
        return "ready_for_review", []
    errors = review_errors(article_dir, require_pass=require_review_pass)
    if errors:
        return "needs_revision", errors
    return "ready_for_delivery", []


def write_state(article_dir: Path, mode: str) -> None:
    process = article_dir / "过程"
    process.mkdir(parents=True, exist_ok=True)
    state = process / "pipeline.json"
    if state.exists():
        raise SystemExit(f"已存在 {state}；不会覆盖现有生产记录")
    payload = {
        "schema_version": 1,
        "mode": mode,
        "purpose": "editorial artifact gates, not model orchestration",
        "stages": ["evidence", "brief", "outline", "draft", "independent_review", "delivery"],
    }
    state.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Initialized pipeline record: {state}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create a non-destructive pipeline record")
    init.add_argument("--article-dir", type=Path, required=True)
    init.add_argument("--mode", choices=("guided", "auto"), default="guided")
    for name in ("status", "preflight"):
        command = sub.add_parser(name, help="Check artifact gates; preflight requires a passing review")
        command.add_argument("--article-dir", type=Path, required=True)
    args = parser.parse_args()
    article_dir = args.article_dir.resolve()
    if args.command == "init":
        article_dir.mkdir(parents=True, exist_ok=True)
        write_state(article_dir, args.mode)
        return
    if not article_dir.is_dir():
        raise SystemExit(f"文章目录不存在：{article_dir}")
    state, errors = status(article_dir, require_review_pass=args.command == "preflight")
    print(json.dumps({"status": state, "errors": errors}, ensure_ascii=False, indent=2))
    successful_states = {"ready_for_delivery"}
    if args.command == "status":
        successful_states.add("ready_for_review")
    if state not in successful_states:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
