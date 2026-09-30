#!/usr/bin/env python3
"""Regression checks for the Gemini-to-Codex handoff gate."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_handoff.py")


def run(root: Path, handoff: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--handoff", str(handoff)],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        article_dir = root / "articles" / "2026-10-01-test"
        article_dir.mkdir(parents=True)
        for name in ("brief.md", "evidence.md", "outline.md", "title-options.md", "article.md"):
            (article_dir / name).write_text("test\n", encoding="utf-8")
        handoff = article_dir / "handoff.json"
        handoff.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "ready_for_codex",
                    "article_dir": "articles/2026-10-01-test",
                    "requested_steps": ["structure_gate", "ai_check", "cover", "charcoal_layout"],
                    "draft_delivery": True,
                }
            ),
            encoding="utf-8",
        )
        valid = run(root, handoff)
        assert valid.returncode == 0, valid.stderr

        data = json.loads(handoff.read_text(encoding="utf-8"))
        data["article_dir"] = "../outside"
        handoff.write_text(json.dumps(data), encoding="utf-8")
        invalid = run(root, handoff)
        assert invalid.returncode == 1
        assert "must stay inside" in invalid.stderr

        data["article_dir"] = "articles/2026-10-01-test"
        data["draft_delivery"] = True
        data["requested_steps"] = ["structure_gate", "cover"]
        handoff.write_text(json.dumps(data), encoding="utf-8")
        missing_layout = run(root, handoff)
        assert missing_layout.returncode == 1
        assert "requires the charcoal_layout" in missing_layout.stderr
    print("Gemini handoff validator tests passed.")


if __name__ == "__main__":
    main()
