---
name: flexfox-cover
description: Use when creating a 900×383 WeChat Official Account cover or a cover prompt for a completed FlexFox article.
---

# FlexFox 公众号封面

Use the locked title and active Profile. Do not design from a draft title. The cover is an article asset, not an inline body image.

## Default visual system

- 900×383 horizontal image;
- pure black background, white hand-drawn lines and restrained white blocks;
- one visual metaphor drawn from the title's conflict, emotion, or change;
- abundant negative space and a readable phone-thumbnail silhouette;
- no text, letters, numbers, gradients, glow, particles, cyberpunk decoration, 3D render, or generic corporate illustration.

Write the final prompt to `images/cover-prompt.md`. If an image-generation tool is available and the user requests generation, create `images/cover-900x383.png`, inspect it, and retry once only for the most obvious failure. Crop then scale proportionally; never stretch.

Record in `images/manifest.md` that the cover is not inserted into `article.md`.
