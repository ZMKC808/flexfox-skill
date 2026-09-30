---
name: flexfox-cover
description: Use when creating the final 900×383 WeChat Official Account cover for a completed FlexFox article.
---

# FlexFox 公众号封面

Use the locked title and active Profile. Do not design from a draft title. The cover is an article asset, not an inline body image.

## Default visual system

- 900×383 horizontal image;
- pure black background, white hand-drawn lines and restrained white blocks;
- one visual metaphor drawn from the title's conflict, emotion, or change;
- abundant negative space and a readable phone-thumbnail silhouette;
- no text, letters, numbers, gradients, glow, particles, cyberpunk decoration, 3D render, or generic corporate illustration.

Use the current environment's native image-generation ability directly. Generate the final asset, inspect it, then save it as `images/cover-900x383.png`. Crop and scale proportionally to 900×383; never stretch. Retry once only for the most obvious visual failure.

Do not create `cover-prompt.md`, and do not relay the prompt or asset to another AI provider. If native image generation is unavailable, report the cover as incomplete and stop the cover step rather than creating a prompt-only substitute.

Record in `images/manifest.md` that the cover is not inserted into `article.md`.
