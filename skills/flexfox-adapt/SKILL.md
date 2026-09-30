---
name: flexfox-adapt
description: Use when the user provides a WeChat article, X/Twitter post, or other source link and wants an original FlexFox WeChat article derived from it, rather than a summary or repost.
---

# FlexFox 二创

This is a source-import mode for the ordinary FlexFox writing chain, not a second writer persona. Its output must give AI飞升录 readers a new angle, new structure and account-specific judgment; it must not translate, paraphrase paragraph by paragraph, or imitate the source structure.

## Import the source

1. Save the source URL and author/account in `evidence.md` before drafting.
2. For a public `mp.weixin.qq.com` link, use `wechat-article-to-markdown` when available; it downloads the article and its images into the current article project's `source/` folder. If it is unavailable or blocked, read the page with another real extractor and record the failure.
3. For an X/Twitter link or thread, read the complete post/thread and record the original URL, author, timestamps and claims. Download media only when it is necessary evidence and rights permit reuse.
4. Treat source images as evidence, not free stock. Use them in the new article only with clear reuse permission, attribution where needed, and a remote delivery URL. Otherwise describe the fact or find an approved replacement.

## Rebuild, do not wash

Before writing, create `adaptation.md` with:

- source facts that have been independently checked;
- the reader problem this source reveals;
- the new AI飞升录 angle, scene or test;
- facts/images that cannot be reused;
- the one-line credit or attribution plan if the source is named.

Then continue through `flexfox-research` → Brief confirmation → `flexfox-writer` → `flexfox-ai-check` → title, digest, cover and delivery. Keep direct quotation short and attributed. If the source is too thin to support a distinct article, stop at an annotated idea instead of padding it into a rewrite.
