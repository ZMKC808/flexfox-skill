#!/usr/bin/env python3
"""Create the local charcoal-layout body with opening greeting and clean markdown."""

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

    # Step 1: Strip YAML frontmatter if present
    start_idx = 0
    for idx, line in enumerate(lines):
        if line.strip():
            start_idx = idx
            break

    if start_idx < len(lines) and lines[start_idx].strip() == "---":
        end_fm_idx = -1
        for idx in range(start_idx + 1, len(lines)):
            if lines[idx].strip() in ("---", "..."):
                end_fm_idx = idx
                break
        if end_fm_idx != -1:
            lines = lines[end_fm_idx + 1 :]

    # Step 2: Strip the first H1 header
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        if line.startswith("# "):
            return "\n".join(lines[index + 1 :]).lstrip()
        return "\n".join(lines[index:]).lstrip()
    return ""


def validate_image_sources(markdown: str) -> None:
    # Only reject raw base64 data URIs that bloat the document; local paths and https URLs are allowed!
    invalid = [url for url in IMAGE.findall(markdown) if url.startswith("data:image/")]
    if invalid:
        raise SystemExit("Error: body images should not be raw base64 data URIs. Use local paths (e.g. images/01.png) or remote URLs.")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=root / "config/wechat.local.env")
    args = parser.parse_args()

    config = {}
    if args.config.is_file():
        try:
            config = parse_env(args.config)
        except Exception:
            pass

    gif_url = config.get("FLEXFOX_WECHAT_INTRO_GIF_URL", "")
    markdown = args.article.read_text(encoding="utf-8")
    body = body_without_title(markdown)
    if not body:
        raise SystemExit("Error: article has no body after its title.")
    validate_image_sources(body)

    header_parts = []
    if gif_url.startswith("https://") or gif_url.startswith("http://"):
        header_parts.append(f"![AI飞升录开场动图]({gif_url})\n")
    header_parts.append(f"{OPENING}\n")

    prefix = "\n".join(header_parts)
    output = f"{prefix}\n{body.rstrip()}\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"Prepared WeChat body: {args.output}")


if __name__ == "__main__":
    main()
