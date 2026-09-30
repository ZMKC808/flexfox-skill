# Changelog

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
