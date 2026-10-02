#!/usr/bin/env python3
"""Regression checks for the FlexFox article structure gate."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_article.py")


def run(article: Path, sources: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--article", str(article), "--sources", str(sources)],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        article = root / "article.md"
        sources = root / "sources" / "index.json"
        sources.parent.mkdir()
        sources.write_text(
            json.dumps(
                {"schema_version": 1, "sources": [{"id": "S01", "status": "success"}, {"id": "S02", "status": "success"}]},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (root / "evidence.md").write_text("- [E01][S01] 事实一\n- [E02][S02] 事实二\n", encoding="utf-8")
        (root / "brief.md").write_text("## 素材关系与关键证据\n- [必写] E01：开场事实\n- [必写] E02：转折事实\n", encoding="utf-8")
        (root / "outline.md").write_text("## 现场出问题\n- 证据：[S01] [S02]\n- 关键事实：[E01] [E02]\n", encoding="utf-8")
        paragraphs = ["测" * 250, "验" * 250, "稿" * 250]
        image_dir = root / "images"
        image_dir.mkdir()
        for index in range(1, 7):
            (image_dir / f"{index}.png").write_bytes(f"unique-{index}".encode())
        (image_dir / "manifest.md").write_text(
            "\n".join(f"- images/{index}.png：测试证据图" for index in range(1, 7)) + "\n",
            encoding="utf-8",
        )
        article.write_text(
            "# 测试标题\n\n"
            + "\n\n".join(
                f"## {heading}\n\n{paragraphs[0]}\n\n![图](images/{index * 2 - 1}.png)\n\n{paragraphs[1]}\n\n![图](images/{index * 2}.png)\n\n{paragraphs[2]}"
                for index, heading in enumerate(("现场出问题", "账单有变化", "用户得算账"), 1)
            )
            + "\n**重点** **证据**\n",
            encoding="utf-8",
        )
        passed = run(article, sources)
        assert passed.returncode == 0, passed.stderr
        report = json.loads((root / "structure-check.json").read_text(encoding="utf-8"))
        assert report["status"] == "pass"
        assert report["metrics"]["各节正文语义块数"] == [3, 3, 3]

        article.write_text(article.read_text(encoding="utf-8") + "\n这不是测试，而是扫描样本。\n", encoding="utf-8")
        flagged = run(article, sources)
        assert flagged.returncode == 0, flagged.stderr
        flags = json.loads((root / "structure-check.json").read_text(encoding="utf-8"))["metrics"]["风格红旗"]
        assert {item["name"] for item in flags} == {"否定式翻转"}

        article.write_text("# 太短\n\n只有一点内容。\n", encoding="utf-8")
        failed = run(article, sources)
        assert failed.returncode == 1
        assert json.loads((root / "structure-check.json").read_text(encoding="utf-8"))["status"] == "needs-revision"
    print("Article validator tests passed.")


if __name__ == "__main__":
    main()
