#!/usr/bin/env python3
"""Regression checks for fresh-review enforcement in the FlexFox pipeline."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("pipeline.py")
SPEC = importlib.util.spec_from_file_location("pipeline", SCRIPT)
assert SPEC and SPEC.loader
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        article = root / "article.md"
        article.write_text("# 标题\n\n正文", encoding="utf-8")
        (root / "brief.md").write_text("## 素材关系与关键证据\n- [必写] E01：事实\n", encoding="utf-8")
        review = {
            "schema_version": 1,
            "article_sha256": digest(article),
            "review_round": 1,
            "reviewer": "independent-editor",
            "status": "pass",
            "fact_checks": [{"fact_id": "E01", "status": "pass", "location": "首段"}],
            "findings": [],
            "summary": "通过",
        }
        (root / "review.json").write_text(json.dumps(review, ensure_ascii=False), encoding="utf-8")
        assert not pipeline.review_errors(root, require_pass=True)
        article.write_text("# 标题\n\n正文已修改", encoding="utf-8")
        assert pipeline.review_errors(root, require_pass=True)
        review["article_sha256"] = digest(article)
        review["findings"] = [{"severity": "major", "location": "首段", "repair": "补证据"}]
        (root / "review.json").write_text(json.dumps(review, ensure_ascii=False), encoding="utf-8")
        assert pipeline.review_errors(root, require_pass=True)

        compact = root / "compact"
        process = compact / "过程"
        process.mkdir(parents=True)
        compact_article = compact / "article.md"
        compact_article.write_text("# 标题\n\n紧凑目录正文", encoding="utf-8")
        (process / "brief.md").write_text("## 素材关系与关键证据\n- [必写] E01：事实\n", encoding="utf-8")
        compact_review = dict(review)
        compact_review.update(
            article_sha256=digest(compact_article),
            findings=[],
            status="pass",
        )
        (process / "review.json").write_text(json.dumps(compact_review, ensure_ascii=False), encoding="utf-8")
        assert not pipeline.review_errors(compact, require_pass=True)
    print("Pipeline tests passed.")


if __name__ == "__main__":
    main()
