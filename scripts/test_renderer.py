#!/usr/bin/env python3
"""Dependency-free regression checks for the charcoal renderer."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import prepare_wechat_body as preparer  # noqa: E402
import render_charcoal as renderer  # noqa: E402
import wechat_draft as draft  # noqa: E402


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_error(markdown: str) -> None:
    try:
        renderer.render_markdown(markdown)
    except ValueError:
        return
    raise AssertionError(f"Expected renderer to reject: {markdown!r}")


def main() -> None:
    article = "---\ntitle: 测试标题\ntype: article\n---\n\n# 测试标题\n\n正文。\n"
    expect(preparer.body_without_title(article) == "正文。", "frontmatter and H1 must be removed")

    html = renderer.render_markdown(
        "## 小标题\n紧接正文\n\n![证据](images/01.png)\n\n```python\nprint(1)\n```\n\n[官网](https://example.test/?a=1&b=2)"
    )
    expect("<h2" in html and "小标题" in html, "H2 must render")
    expect("紧接正文" in html, "text after an H2 must not be dropped")
    expect('<img src="images/01.png"' in html, "local images must render")
    expect("<pre" in html and "print(1)" in html, "fenced code must render")
    expect('href="https://example.test/?a=1&amp;b=2"' in html, "links must be escaped once")
    expect("![证据]" not in html, "image markdown must not leak into output")

    escaped = renderer.render_markdown('![图](images/a"b.png)')
    expect('src="images/a&quot;b.png"' in escaped, "image attributes must be escaped")
    expect_error("图片在这里 ![证据](images/01.png)")
    expect_error("![图](data:image/png;base64,AAAA)")

    seen: list[str] = []
    original_upload = draft.upload_inline_image
    try:
        draft.upload_inline_image = lambda token, source, base_dir=None: (seen.append(source) or "https://cdn.example/image.png")
        rendered, count = draft.replace_images(
            "test-token",
            '<img src="images/a&quot;b.png"/><img src="https://example.test/a.png?x=1&amp;y=2"/>',
        )
    finally:
        draft.upload_inline_image = original_upload
    expect(seen == ['images/a"b.png', 'https://example.test/a.png?x=1&y=2'], "draft uploader must decode HTML image sources")
    expect(count == 2 and "https://cdn.example/image.png" in rendered, "draft uploader must replace each body image")

    print("Charcoal renderer regression checks passed.")


if __name__ == "__main__":
    main()
