---
name: flexfox-charcoal-layout
description: Use when the user asks to typeset a finished FlexFox WeChat article in the account's charcoal business style, ready for direct draft-box delivery without Flowcast.
---

# 炭黑商务排版

This is a self-contained renderer. It turns the final Markdown into WeChat-compatible inline HTML using the fixed charcoal layout contract; it never opens Flowcast or relies on the system clipboard.

## Preconditions

1. Read the active Profile, `article.md`, `evidence.md`, and `images/manifest.md` if present.
2. Confirm the title and article text are final. This Skill must not rewrite them.
3. Read `../../references/charcoal-layout-contract.md` and `../../references/output-contract.md`.
4. Work in the existing `articles/YYYY-MM-DD-明确主题/` directory.

## Prepare the body

The WeChat platform owns the title field, so do not duplicate `# 标题` in the rich-text body. Use the helper to make `wechat-body.md`; it keeps `article.md` unchanged, strips YAML frontmatter and H1, and places the account GIF and greeting first:

```bash
python3 scripts/prepare_wechat_body.py \
  --article articles/YYYY-MM-DD-明确主题/article.md \
  --output articles/YYYY-MM-DD-明确主题/wechat-body.md \
  --require-intro-gif
```

The default AI飞升录 Profile requires this fixed GIF. Its active local account config must contain the opening GIF URL; otherwise preparation stops instead of silently producing a different first screen. Create it once with `uv run --with requests python3 scripts/sync_intro_gif.py`; the source GIF and generated URL remain private to that account. A different Profile without a fixed opener omits `--require-intro-gif`.

For the body that follows the opening:

- Preserve prose, lower-level headings, emphasis, quotes, lists and code exactly; never use Flowcast AI “顺稿微调”.
- Use `##` for primary sections and `###` only for genuine nested scenes.
- Retain only evidence-bearing body images from the manifest. Images use local relative paths (such as `images/01.png` or `图片/01.png`) or remote `https://` URLs, with meaningful alt text, alone on their own lines, with blank lines before and after.
- Remove raw base64 data URIs, advertising images and the cover image.
- During drafting, local relative paths are standard. When pushing to WeChat draft box, `scripts/wechat_draft.py` automatically uploads local images to WeChat's official CDN and substitutes the resulting URLs.
- The renderer rejects a body image embedded in prose instead of silently publishing Markdown syntax. Fix the source `article.md`, then regenerate `wechat-body.md`.

## Render and deliver

`flexfox-wechat-draft` renders `wechat-body.md` directly using `scripts/render_charcoal.py`, uploads local/remote body images to WeChat CDN, and creates the draft. There is no exported HTML file and no clipboard step.

Before the first real delivery, inspect the rendered preview or the saved WeChat draft: fixed GIF opening, greeting, normal paragraph, one H2, one H3, one bold phrase, one quote and one image. If WeChat sanitizes a property, fix only that property in the local renderer contract.

## Deliver

Write `layout-checklist.md` with:

- renderer `flexfox-charcoal-layout` / style `炭黑商务`;
- whether direct render succeeded;
- every body image path/URL and its evidence purpose;
- any image deliberately omitted or marked pending;
- the one-time WeChat editor visual check still required.

If `flexfox-wechat-draft` ran, include its receipt path and verification state. It owns the draft action; do not create a second draft yourself.

Report the exact paths.
