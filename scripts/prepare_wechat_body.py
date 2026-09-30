#!/usr/bin/env python3
"""Create the local charcoal-layout body with AI飞升录's fixed opening."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

try:
    from .wechat_draft import parse_env
except ImportError:  # Script execution, rather than package import.
    from wechat_draft import parse_env


OPENING = "👋哈喽大家好，我是ai领航员小陆，"
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def body_without_title(markdown: str) -> str:
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        if line.startswith("# "):
            return "\n".join(lines[index + 1 :]).lstrip()
        return "\n".join(lines[index:]).lstrip()
    return ""


def validate_image_sources(markdown: str) -> None:
    invalid = [url for url in IMAGE.findall(markdown) if not url.startswith("https://")]
    if invalid:
        raise SystemExit("Error: body images must use approved https URLs, not local paths or base64.")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=root / "config/wechat.local.env")
    args = parser.parse_args()

    config = parse_env(args.config)
    gif_url = config.get("FLEXFOX_WECHAT_INTRO_GIF_URL", "")
    if not gif_url.startswith("https://"):
        raise SystemExit("Error: no opening GIF URL. Run scripts/sync_intro_gif.py first.")
    markdown = args.article.read_text(encoding="utf-8")
    body = body_without_title(markdown)
    if not body:
        raise SystemExit("Error: article has no body after its title.")
    validate_image_sources(body)
    output = f"![AI飞升录开场动图]({gif_url})\n\n{OPENING}\n\n{body.rstrip()}\n"
    args.output.write_text(output, encoding="utf-8")
    print(f"Prepared WeChat body: {args.output}")


if __name__ == "__main__":
    main()
