#!/usr/bin/env python3
"""Offline regression: every draft entry must enforce gates before networking."""
import argparse
import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch
import wechat_draft
import wechat_delivery_check
from prepare_wechat_body import prepare_body

with tempfile.TemporaryDirectory(prefix='公众号 中文 空格 ') as temp:
    directory = Path(temp)
    (directory/'过程').mkdir()
    (directory/'images').mkdir()
    article = directory/'article.md'
    article.write_text('# 测试\n\n正文。\n', encoding='utf-8')
    (directory/'images/cover-900x383.png').write_bytes(b'fixture')
    (directory/'过程/digest.md').write_text('摘要', encoding='utf-8')
    config = {'FLEXFOX_WECHAT_INTRO_GIF_URL':'https://example.com/intro.gif'}
    body = directory/'过程/wechat-body.md'
    args = argparse.Namespace(confirm_draft=True, article_dir=directory, title='测试', body=None, digest=None, cover=None, author=None)
    def blocked(message, *, preflight_ok=True, current_config=None):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), patch.object(wechat_delivery_check.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0 if preflight_ok else 1, '', '审稿未通过')), patch.object(wechat_draft, 'access_token', side_effect=AssertionError('network reached')):
            try:
                wechat_draft.command_draft(args, config if current_config is None else current_config)
            except SystemExit as exc:
                assert message in stderr.getvalue(), stderr.getvalue()
            else:
                raise AssertionError('Invalid draft accepted')
    body.write_text('过期正文', encoding='utf-8')
    blocked('正文不同')
    body.write_text(prepare_body(article.read_text(), config), encoding='utf-8')
    blocked('preflight', preflight_ok=False)
    blocked('opening GIF', current_config={})
    for name in ('wechat-draft.json', 'wechat-draft-attempt.json'):
        receipt=directory/'过程'/name
        receipt.write_text('{}')
        blocked('已有投递记录')
        receipt.unlink()
    with patch.object(wechat_delivery_check.subprocess, 'run', return_value=subprocess.CompletedProcess([],0,'','')):
        assert wechat_delivery_check.inspect(directory, config=config)==[]
    args.cover=directory/'missing.png'
    blocked('指定封面不存在')
    args.cover=None
    args.digest='超'*26
    blocked('指定摘要')
print('Offline delivery guards passed: stale body, preflight, GIF, receipts, cover and digest.')
