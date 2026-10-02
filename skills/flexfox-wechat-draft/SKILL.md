---
name: flexfox-wechat-draft
description: Use when the user explicitly asks to put a final FlexFox 炭黑商务 article into a WeChat Official Account draft box; never use it to publish or mass-send.
---

# 微信草稿箱投递

This Skill delivers one final, already typeset article to the current account's draft box. It never publishes, mass-sends, deletes, or edits existing drafts.

## Preconditions

1. Read `../../references/wechat-draft-delivery.md`.
2. Require a final title, final `article.md`, prepared `过程/wechat-body.md`, and `images/cover-900x383.png`.
3. Require either the user's explicit request to push this article to drafts, or an active Profile plus local account config that explicitly enables automatic draft delivery. Do not infer this from a request to merely write or typeset.
4. Confirm `config/wechat.local.env` is local and ignored. Never display, copy, commit, or transmit its values anywhere except the WeChat API request.
5. Run `python3 scripts/pipeline.py preflight --article-dir articles/YYYY-MM-DD-明确主题`. A failed preflight blocks draft creation.

## Deliver

First validate credentials without a write:

```bash
uv run --with requests python3 scripts/wechat_draft.py validate
```

If WeChat reports `40164 invalid ip`, stop. Tell the account owner to add the IP from that error to the official-account IP whitelist, then retry validation once.

Only after validation succeeds, call the script with the final locked title. It reads the mandatory `过程/digest.md` automatically; pass `--digest` only to override it for this one draft:

```bash
uv run --with requests python3 scripts/wechat_draft.py draft \
  --article-dir articles/YYYY-MM-DD-明确主题 \
  --title "最终标题" \
  --digest "可选摘要" \
  --confirm-draft
```

The script renders `过程/wechat-body.md` with the local charcoal renderer, uploads body images and the cover, creates exactly one draft, verifies it, and writes `过程/wechat-draft.json`. Do not call it again after a success. Report the receipt path and whether verification succeeded; do not print the media ID unless the user asks.
