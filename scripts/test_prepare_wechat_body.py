#!/usr/bin/env python3
"""Regression checks for the WeChat opening-component preparation step."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("prepare_wechat_body.py")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True, check=False)


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        article = root / "article.md"
        output = root / "wechat-body.md"
        config = root / "wechat.local.env"
        article.write_text("# 测试标题\n\n正文。\n", encoding="utf-8")

        missing_gif = run(
            "--article",
            str(article),
            "--output",
            str(output),
            "--config",
            str(config),
            "--require-intro-gif",
        )
        assert missing_gif.returncode == 1
        assert "requires an opening GIF" in missing_gif.stderr

        config.write_text(
            "FLEXFOX_WECHAT_APPID=test-app\n"
            "FLEXFOX_WECHAT_APPSECRET=test-secret\n"
            "FLEXFOX_WECHAT_INTRO_GIF_URL=https://example.com/intro.gif\n",
            encoding="utf-8",
        )
        prepared = run(
            "--article",
            str(article),
            "--output",
            str(output),
            "--config",
            str(config),
            "--require-intro-gif",
        )
        assert prepared.returncode == 0, prepared.stderr
        body = output.read_text(encoding="utf-8")
        assert "https://example.com/intro.gif" in body
        assert "👋哈喽大家好，我是ai领航员小陆，" in body
        assert "# 测试标题" not in body
    print("WeChat body preparation tests passed.")


if __name__ == "__main__":
    main()
