# Changelog

## 0.7.0

- Remove Gemini/Codex handoff, polling, and external-AI cover relay from the package.
- Make the final 900×383 cover a native FlexFox image-generation deliverable, not a prompt for another tool.

## 0.6.1

- Fix body rendering for YAML frontmatter, adjacent headings, fenced code blocks, local images, and escaped links.
- Reject inline or data-URI body images instead of silently emitting malformed content.
- Add renderer regression checks to local validation and GitHub Actions.

## 0.6.0

- Add unified scraper `scripts/fetch_source.py` supporting both WeChat articles and Twitter/X posts (with automatic image extraction).
- Overhaul `scripts/wechat_draft.py` to seamlessly accept local relative image paths (`images/` or `图片/`), automatically uploading them to WeChat Official CDN via `/media/uploadimg` without requiring third-party image hosting.
- Upgrade `skills/flexfox-adapt` with a strict 4-step deconstruction and stance multiplication pipeline to guarantee under 30% repetition rate and prevent text-spinning.
- Upgrade `profiles/ai-feishenglu.md` with authentic language fingerprints, wild analogies, friction rules, and strict 2-4 spot bolding discipline extracted from historical published articles.
- Update `scripts/prepare_wechat_body.py` to permit local images and gracefully handle missing intro GIF configurations.
- Update `references/output-contract.md` to standardize local image usage throughout the authoring and review lifecycle.

## 0.5.0

- Replace the browser-dependent Flowcast adapter with `flexfox-charcoal-layout`, a self-contained charcoal inline-HTML renderer.
- Remove clipboard transport from draft delivery; `wechat-body.md` is rendered directly in memory for WeChat.
- Tighten WeChat digests to 15–20 Chinese characters, with a hard 25-character limit.

## 0.4.0

- Replace the generic share-copy Skill with the AI飞升录 account's fixed forward-copy template.
- Add `flexfox-adapt` for original, attributed source adaptation from public WeChat and X/Twitter links.
- Add a mandatory short `digest.md`, automated draft digest reading, and account-configured author field.
- Add an account-private opening GIF upload and deterministic Flowcast-input preparation step.

## 0.3.0

- Add `flexfox-wechat-draft` for verified WeChat Official Account draft-box delivery.
- Preserve Flowcast's native clipboard HTML, upload body images and cover through WeChat APIs, and record a safe delivery receipt.
- Keep automatic draft delivery account-local and opt-in; publishing and mass-send remain out of scope.

## 0.2.0

- Add `flexfox-flowcast-charcoal`, the first optional layout adapter.
- Use Flowcast's native charcoal export rather than a second CSS implementation.
- Add a fixed, auditable typography and image-placement contract for this theme.

## 0.1.0

- First public architecture: research, title, FlexFox writing, AI check, cover, and share-copy skills.
- Includes the AI飞升录 default Profile and a replacement template.
- Excludes layout, publishing, and analytics.
