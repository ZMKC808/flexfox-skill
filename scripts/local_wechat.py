#!/usr/bin/env python3
"""Local-only preview and readiness checks for the existing Chinese SOP layout."""
from __future__ import annotations
import argparse
import html
import re
from pathlib import Path
from urllib.parse import unquote, urlparse
from prepare_wechat_body import body_without_title, validate_image_sources
from render_charcoal import render_markdown

ROOT = Path(__file__).resolve().parent.parent

def check_ready(directory: Path, body: Path | None = None) -> None:
    from wechat_delivery_check import inspect
    from wechat_draft import parse_env
    errors = inspect(directory, config=parse_env(ROOT/'config/wechat.local.env'), body_path=body)
    if errors:
        raise SystemExit("\n".join(errors))

def check_images(text: str, directory: Path) -> None:
    validate_image_sources(text)
    for source in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text):
        if urlparse(source).scheme in ('https', 'http'):
            continue
        path = Path(unquote(source))
        if not path.is_absolute():
            path = directory / path
        if not path.is_file():
            raise SystemExit(f'本地图片不存在：{path}')

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['preview', 'check'])
    parser.add_argument('--article-dir', type=Path, required=True)
    args = parser.parse_args()
    directory = args.article_dir.resolve()
    if args.command == 'check':
        check_ready(directory, directory / '过程/wechat-body.md')
        print('本地检查通过；质检结论仍须按 WORKFLOW 人工/Agent 核实。未访问微信。')
        return
    article = directory / 'article.md'
    from pipeline import status
    state, errors = status(directory, require_review_pass=True)
    if state != 'ready_for_delivery':
        raise SystemExit('preflight 未通过：'+'; '.join(errors))
    from prepare_wechat_body import prepare_body
    from wechat_draft import parse_env
    content = prepare_body(article.read_text(encoding='utf-8'), parse_env(ROOT/'config/wechat.local.env'))
    check_images(content, directory)
    rendered = render_markdown(content)
    # Preview-only file URLs resolve Chinese paths and spaces from the article root.
    def image_url(match):
        source = html.unescape(match[1])
        if urlparse(source).scheme in ('http', 'https'):
            return match[0]
        path = Path(unquote(source))
        if not path.is_absolute():
            path = directory / path
        return 'src="' + html.escape(path.resolve().as_uri(), quote=True) + '"'
    rendered = re.sub(r'src="([^"]+)"', image_url, rendered)
    process = directory / '过程'
    process.mkdir(exist_ok=True)
    (process / 'wechat-body.md').write_text(content.rstrip()+'\n', encoding='utf-8')
    output = process / '排版预览.html'
    output.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>炭黑排版预览</title><body style="max-width:677px;margin:32px auto">'+rendered+'</body></html>', encoding='utf-8')
    print(output)

if __name__ == '__main__':
    main()
