---
name: flexfox-charcoal-layout
description: Use when the user asks to typeset a finished FlexFox WeChat article in the account's charcoal business style, ready for direct draft-box delivery without Flowcast.
---

# 炭黑商务排版

This is a self-contained renderer. It turns the final Markdown into WeChat-compatible inline HTML using the fixed charcoal layout contract; it never opens Flowcast or relies on the system clipboard.

## Preconditions

1. Read the active Profile, `article.md`, `evidence.md`, and `images/manifest.md` if present.
2. Confirm the title and article text are final. This Skill must not rewrite them.
3. Read `../../references/charcoal-layout-contract.md` and `../../references/asset-and-source-policy.md`.
4. Work in the existing `articles/YYYY-MM-DD-明确主题/` directory.

## Prepare the body

The WeChat platform owns the title field, so do not duplicate `# 标题` in the rich-text body. Use the helper to make `wechat-body.md`; it keeps `article.md` unchanged, removes the H1, and places the account GIF and greeting first:

```bash
python3 scripts/prepare_wechat_body.py \
  --article articles/YYYY-MM-DD-明确主题/article.md \
  --output articles/YYYY-MM-DD-明确主题/wechat-body.md
```

The active local account config must already contain the opening GIF URL. It is created once with `uv run --with requests python3 scripts/sync_intro_gif.py` and remains private to that account.

For the body that follows the opening:

- Preserve prose, lower-level headings, emphasis, quotes, lists and code exactly; never use Flowcast AI “顺稿微调”.
- Use `##` for primary sections and `###` only for genuine nested scenes.
- Retain only evidence-bearing body images from the manifest. Each image must use a complete `https://` URL and meaningful alt text, be alone on its own line, and have blank lines before and after it.
- Remove local paths, base64/data URIs, placeholder brackets, advertising images and the cover image.
- If an image has no approved remote URL, leave a plain `[待补远程图：用途]` marker and report it. Do not invent an URL or silently embed a local file.

## Render and deliver

`flexfox-wechat-draft` renders `wechat-body.md` directly using `scripts/render_charcoal.py`, uploads its remote body images to WeChat, and creates the draft. There is no exported HTML file and no clipboard step.

Before the first real delivery, inspect the rendered preview or the saved WeChat draft: fixed GIF opening, greeting, normal paragraph, one H2, one H3, one bold phrase, one quote and one image. If WeChat sanitizes a property, fix only that property in the local renderer contract.

## Deliver

Write `layout-checklist.md` with:

- renderer `flexfox-charcoal-layout` / style `炭黑商务`;
- whether direct render succeeded;
- every body image URL and its source/rights state;
- any image deliberately omitted or marked pending;
- the one-time WeChat editor visual check still required.

If `flexfox-wechat-draft` ran, include its receipt path and verification state. It owns the draft action; do not create a second draft yourself.

Report the exact paths. Never claim a cross-device pixel-perfect WeChat result before that real-editor check succeeds.
