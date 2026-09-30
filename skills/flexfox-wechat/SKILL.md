---
name: flexfox-wechat
description: Use when the user asks to create, continue, or fully produce a WeChat Official Account article with FlexFox, including research, title, writing, AI check, cover, fixed forward copy, or charcoal layout.
---

# FlexFox 公众号主入口

Use the system as a production chain, not a file checklist. The goal is a credible, readable article package; do not create an artifact that the task does not need.

## Resolve context

1. Apply explicit user requirements first.
2. Look for `flexfox-profile.md` in the current project. If absent, use `../../profiles/ai-feishenglu.md` relative to this Skill.
3. Read `../../references/output-contract.md` and `../../references/evidence-policy.md` before a full article task.
4. Create or reuse `articles/YYYY-MM-DD-明确主题/` in the current project. Never overwrite another article project.

## Route the request

| User intent | Run |
|---|---|
| “写一篇公众号”“完整做一篇” | Research → title → Brief confirmation → writer → AI check → title lock + digest → cover → fixed forward copy → active Profile's default layout |
| “二创这篇”“把这个公众号/X 链接写成文章” | `flexfox-adapt` |
| “查资料”“核验选题” | `flexfox-research` |
| “起标题” | `flexfox-title` |
| “写/续写/改正文” | `flexfox-writer` |
| “检查 AI 味” | `flexfox-ai-check` |
| “做封面” | `flexfox-cover` |
| “排版”“炭黑商务” | `flexfox-charcoal-layout` |
| “推草稿箱”“上传公众号草稿” | `flexfox-wechat-draft` |

For a new article, obtain or record the one-line Brief before drafting: reader, intended feeling, and what not to discuss. If the user already confirmed a direction, reuse that confirmation without asking again.

## Full-task completion

- Keep `article.md` as the only prose source. Downstream Skills may create assets and reports but must not overwrite it without an explicit revision step.
- `flexfox-ai-check` identifies problems; send only the affected passages back to `flexfox-writer` for repair, then recheck those passages.
- Generate `digest.md` after the title is locked; it is the one- or two-sentence hook used by the WeChat draft, never a long abstract.
- Generate the cover only after the title is locked. Generate `转发词.md` only after article and title are final, using the active Profile's fixed transfer template. Do not invent alternate “群聊/朋友圈/私发” versions unless the user asks.
- Run `flexfox-charcoal-layout` only after article and title are final. It prepares `wechat-body.md` then locally renders the fixed charcoal inline HTML; skip it for a draft-only request.
- After local layout succeeds, run `flexfox-wechat-draft` only for an explicit draft request, or when both the active Profile and ignored local account config explicitly enable automatic draft delivery. It may create one new draft but must never publish or mass-send.
- Do not save rendered HTML or use local image paths/base64 in the body.
- Report the final title and exact paths of all delivered assets, plus any skipped deliverable and why.
