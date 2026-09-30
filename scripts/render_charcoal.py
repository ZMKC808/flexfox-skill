#!/usr/bin/env python3
"""Render FlexFox Markdown as self-contained charcoal rich HTML for WeChat."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


IMAGE = re.compile(r"^!\[([^\]]*)\]\((https://[^)]+)\)$")
LINK = re.compile(r"(?<!!)\[([^\]]+)\]\((https://[^)]+)\)")
BOLD = re.compile(r"\*\*(.+?)\*\*")
ITALIC = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
CODE = re.compile(r"`([^`]+)`")

P_STYLE = "margin:0 0 28px;font-family:sans-serif;font-size:16px;line-height:2.1;color:#27272A"
H1_STYLE = "margin:0 0 40px;font-family:sans-serif;font-size:34px;font-weight:900;line-height:1.45;letter-spacing:-1.5px;color:#09090B"
H2_STYLE = "margin:32px 0 24px;padding:10px 20px;font-family:sans-serif;font-size:24px;font-weight:800;line-height:1.5;color:#FFFFFF;background:#18181B;border-radius:4px"
H3_STYLE = "margin:24px 0;font-family:sans-serif;font-size:20px;font-weight:700;line-height:1.6;color:#3F3F46"
IMAGE_STYLE = "display:block;max-width:100%;height:auto;margin:0 auto 28px;border-radius:16px"
QUOTE_STYLE = "margin:24px 0;padding:20px 24px;font-family:sans-serif;font-size:16px;line-height:2.1;color:#27272A;background:#F4F4F5;border-left:8px solid #18181B;border-radius:0 12px 12px 0"
LIST_STYLE = "margin:0 0 28px;padding-left:1.5em;font-family:sans-serif;font-size:16px;line-height:2.1;color:#27272A"


def inline(markdown: str) -> str:
    value = html.escape(markdown, quote=False)
    value = CODE.sub(lambda match: f'<code style="padding:2px 5px;background:#F4F4F5;border-radius:3px">{match.group(1)}</code>', value)
    value = LINK.sub(lambda match: f'<a href="{match.group(2)}" style="color:#18181B;text-decoration:underline">{match.group(1)}</a>', value)
    value = BOLD.sub(lambda match: f'<strong style="font-weight:900;color:#000000">{match.group(1)}</strong>', value)
    return ITALIC.sub(lambda match: f"<em>{match.group(1)}</em>", value)


def paragraph(lines: list[str]) -> str:
    text = "<br/>".join(inline(line.strip()) for line in lines)
    return f'<p style="{P_STYLE}">{text}</p>'


def render(markdown: str) -> str:
    lines = markdown.splitlines()
    pieces: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith("```"):
            language = html.escape(line[3:].strip())
            index += 1
            code: list[str] = []
            while index < len(lines) and not lines[index].startswith("```"):
                code.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            code_text = html.escape("\n".join(code))
            language_attr = f' data-language="{language}"' if language else ""
            pieces.append(f'<pre style="margin:32px 0;padding:20px 24px;overflow:auto;background:#09090B;border-radius:12px"><code{language_attr} style="font-family:monospace;font-size:14px;line-height:1.7;color:#F4F4F5">{code_text}</code></pre>')
            continue
        if line.startswith("### "):
            pieces.append(f'<h3 style="{H3_STYLE}">{inline(line[4:])}</h3>')
            index += 1
            continue
        if line.startswith("## "):
            pieces.append(f'<h2 style="{H2_STYLE}">{inline(line[3:])}</h2>')
            index += 1
            continue
        if line.startswith("# "):
            pieces.append(f'<h1 style="{H1_STYLE}">{inline(line[2:])}</h1>')
            index += 1
            continue
        image = IMAGE.match(line.strip())
        if image:
            alt, source = image.groups()
            pieces.append(f'<img src="{html.escape(source, quote=True)}" alt="{html.escape(alt, quote=True)}" style="{IMAGE_STYLE}"/>')
            index += 1
            continue
        if line.startswith("> "):
            quote: list[str] = []
            while index < len(lines) and lines[index].startswith("> "):
                quote.append(lines[index][2:])
                index += 1
            pieces.append(f'<blockquote style="{QUOTE_STYLE}">{"<br/>".join(inline(item) for item in quote)}</blockquote>')
            continue
        ordered = re.match(r"^\d+\.\s+(.+)$", line)
        bullet = re.match(r"^[-*]\s+(.+)$", line)
        if ordered or bullet:
            tag = "ol" if ordered else "ul"
            items: list[str] = []
            pattern = r"^\d+\.\s+(.+)$" if ordered else r"^[-*]\s+(.+)$"
            while index < len(lines):
                item = re.match(pattern, lines[index])
                if not item:
                    break
                items.append(f"<li>{inline(item.group(1))}</li>")
                index += 1
            pieces.append(f'<{tag} style="{LIST_STYLE}">{"".join(items)}</{tag}>')
            continue
        if re.fullmatch(r"[-*_]{3,}\s*", line):
            pieces.append('<hr style="margin:48px 0;border:0;border-top:2px solid #18181B"/>')
            index += 1
            continue
        prose: list[str] = [line]
        index += 1
        while index < len(lines) and lines[index].strip():
            next_line = lines[index]
            if (
                next_line.startswith(("# ", "## ", "### ", "> ", "```"))
                or IMAGE.match(next_line.strip())
                or re.match(r"^(?:\d+\.|[-*])\s+", next_line)
                or re.fullmatch(r"[-*_]{3,}\s*", next_line)
            ):
                break
            prose.append(next_line)
            index += 1
        pieces.append(paragraph(prose))
    return '<section data-ff-theme="charcoal" style="box-sizing:border-box;padding:0 8px">' + "".join(pieces) + "</section>"


def render_file(path: Path) -> str:
    return render(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    print(render_file(args.input))


if __name__ == "__main__":
    main()
