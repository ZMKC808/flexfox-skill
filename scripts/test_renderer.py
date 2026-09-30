#!/usr/bin/env python3
"""Small regression checks for the standalone charcoal renderer."""

from __future__ import annotations

from render_charcoal import render_markdown


def main() -> None:
    rendered = render_markdown("## 小标题测试\n\n正文 **重点**。\n\n![证据图](images/01.png)\n")
    assert 'data-ff-theme="charcoal"' in rendered
    assert "<h2" in rendered and "小标题测试" in rendered
    assert "<strong" in rendered and "重点" in rendered
    assert 'src="images/01.png"' in rendered
    try:
        render_markdown("文字里 ![坏图](images/01.png)")
    except ValueError:
        pass
    else:
        raise AssertionError("inline images must be rejected")
    print("Renderer tests passed.")


if __name__ == "__main__":
    main()
