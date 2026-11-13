#!/usr/bin/env python3
"""Read-only local delivery diagnostics; never uploads or edits articles."""
from pathlib import Path
import argparse
import json
import re
import subprocess
import sys
from urllib.parse import unquote, urlparse


def inspect(directory, *, config=None, body_path=None, cover_path=None, digest_override=None):
    errors=[]
    process=directory/'过程'
    source=directory/'article.md'
    if not source.exists():
        errors.append('上游正文 article.md 缺失（现有文章.md 不会自动重命名或覆盖）')
    body=body_path or process/'wechat-body.md'
    if not body.is_file():
        errors.append('缺少 过程/wechat-body.md')
    else:
        if source.is_file():
            from prepare_wechat_body import prepare_body
            try:
                expected = prepare_body(source.read_text(encoding='utf-8'), config or {})
                if body.read_text(encoding='utf-8').strip() != expected.strip():
                    errors.append('wechat-body.md 与终审正文不同，请重新排版')
            except SystemExit as exc:
                errors.append(str(exc))
        from render_charcoal import render_file
        try: render_file(body)
        except ValueError as e: errors.append('排版失败：'+str(e))
        for image in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',body.read_text(encoding='utf-8')):
            if urlparse(image).scheme in ('https','http'): continue
            path=Path(unquote(image))
            if not path.is_absolute(): path=directory/path
            if not path.is_file(): errors.append('缺少正文图片：'+image)
    if cover_path is not None and not cover_path.is_file():
        errors.append('指定封面不存在')
    if cover_path is None and not any((directory/path).is_file() for path in ('images/cover-900x383.png','图片/封面-900x383.png','封面-900x383.png')):
        errors.append('缺少封面：images/cover-900x383.png 或 图片/封面-900x383.png')
    digest=process/'digest.md'
    if not digest.is_file() or not digest.read_text(encoding='utf-8').strip():
        errors.append('缺少摘要：过程/digest.md')
    else:
        from wechat_draft import article_digest, WeChatError
        try: article_digest(directory)
        except WeChatError as e: errors.append(str(e))
    for name in ('wechat-draft.json','wechat-draft-attempt.json'):
        if (process/name).exists(): errors.append('已有投递记录，请先核对草稿箱：'+name)
    if digest_override is not None and (not digest_override.strip() or len(digest_override.strip()) > 25):
        errors.append('指定摘要应为 1–25 字')
    result=subprocess.run([sys.executable,str(Path(__file__).with_name('pipeline.py')),'preflight','--article-dir',str(directory)],capture_output=True,text=True)
    if result.returncode:
        errors.append('上游 preflight 未通过：'+(result.stdout.strip() or result.stderr.strip()))
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--article-dir',type=Path,required=True)
    args=parser.parse_args()
    from wechat_draft import parse_env
    config = parse_env(Path(__file__).resolve().parent.parent/'config/wechat.local.env')
    errors=inspect(args.article_dir.resolve(), config=config)
    print(json.dumps({'status':'blocked' if errors else 'pass','network_requests':0,'errors':errors},ensure_ascii=False,indent=2))
    return 1 if errors else 0

if __name__=='__main__':sys.exit(main())
