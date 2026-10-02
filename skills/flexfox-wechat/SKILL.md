---
name: flexfox-wechat
description: Use when the user asks to create, continue, or fully produce a WeChat Official Account article with FlexFox, including research, title, writing, AI check, cover, fixed forward copy, or charcoal layout.
---

# FlexFox 公众号主入口

Use the system as a production chain, not a file checklist. The goal is a credible, readable article package; do not create an artifact that the task does not need.

## Resolve context

1. Apply explicit user requirements first.
2. Look for `flexfox-profile.md` in the current project. If absent, use `../../profiles/ai-feishenglu.md` relative to this Skill. When a custom `flexfox-profile.md` is active and a sibling `flexfox-profile-private/style-guide.md` exists, read it and 2–3 samples relevant to the article type. Private samples guide rhythm and judgment only; never copy wording.
3. Read `../../references/output-contract.md`, `../../references/evidence-policy.md`, `../../references/article-contract.md`, and `../../references/pipeline-contract.md` before a full article task. For linked-source work, also read `../../references/source-contract.md`.
4. Create or reuse `articles/YYYY-MM-DD-明确主题/` in the current project, with `过程/` for all working files. Never overwrite another article project.

For a new project, initialize the production record before research:

```bash
python3 scripts/pipeline.py init --article-dir articles/YYYY-MM-DD-明确主题 --mode guided
```

Use `--mode auto` only when the user explicitly asked to skip Brief confirmation. A Pipeline is an artifact contract, not an excuse to invent a rigid story formula.

## Route the request

| User intent | Run |
|---|---|
| “写一篇公众号”“完整做一篇” | Research → source/evidence (if applicable) → Brief confirmation → outline → writer → structure gate → AI check → title lock + digest → cover → fixed forward copy → active Profile's default layout |
| “二创这篇”“把这个公众号/X 链接写成文章” | `flexfox-adapt` |
| “查资料”“核验选题” | `flexfox-research` |
| “起标题” | `flexfox-title` |
| “写/续写/改正文” | `flexfox-writer` |
| “检查 AI 味” | `flexfox-ai-check` |
| “做封面” | `flexfox-cover` |
| “排版”“炭黑商务” | `flexfox-charcoal-layout` |
| “推草稿箱”“上传公众号草稿” | `flexfox-wechat-draft` |

For a new article, create or complete `过程/brief.md` before drafting. It must contain: one-line main thread, material relationship and key evidence, reader takeaway, image plan, and confirmation basis. “Material relationship” is free-form editorial judgment, not a fixed event template: it identifies what opens the article, what is essential context, what evidence carries each turn, and what stays background. If the user already confirmed a direction, reuse that confirmation without asking again.

## Execution discipline

Do not ask one model pass to plan, draft, praise itself and deliver. Keep the same controller if necessary, but use separate calls or clean contexts for these roles:

1. **writer** creates or repairs `article.md` from the approved Brief and outline;
2. **reviewer** reads the finished draft afresh and only writes `过程/review.md` + `过程/review.json`;
3. **writer** makes targeted repairs from findings; a changed draft requires a fresh second review.

Do not create a swarm of subagents merely to claim a pipeline exists. Source downloading and image inventory may be parallel when independent; editorial direction remains with one accountable controller.

## Full-task completion

- Keep `article.md` as the only prose source. Downstream Skills may create assets and reports but must not overwrite it without an explicit revision step.
- For a linked-source article, require `过程/来源/index.json`, source-tagged `过程/evidence.md`, `过程/brief.md`, and `过程/outline.md` before drafting. Mark every essential fact in the Brief as `[必写] E##`; the same E IDs must appear in the outline. A failed source must be resolved or explicitly excluded in `过程/brief.md`; never silently discard it.
- After every full draft, run `python3 scripts/pipeline.py status --article-dir articles/YYYY-MM-DD-明确主题`. A `needs_revision` result blocks layout and draft delivery. Do not describe a failed draft as reviewed or publish-ready.
- `flexfox-ai-check` judges facts, voice and misleading phrasing only after the structure gate passes. It must trace every `[必写] E##` to its actual paragraph in `article.md`; a fact present only in evidence or outline is a failed draft. It must produce a fresh, hash-bound `过程/review.json`, not a prose self-certification. Send only affected passages back to `flexfox-writer` for repair, then recheck the full draft once.
- Generate `过程/digest.md` after the title is locked; it is the one- or two-sentence hook used by the WeChat draft, never a long abstract.
- Generate the final cover with `flexfox-cover` only after the title is locked. It must save `images/cover-900x383.png` using native image generation; prompt-only or external-AI relay is not a complete cover. Generate `转发词.md` only after article and title are final, using the active Profile's fixed transfer template. Do not invent alternate “群聊/朋友圈/私发” versions unless the user asks.
- Run `python3 scripts/pipeline.py preflight --article-dir articles/YYYY-MM-DD-明确主题` before `flexfox-charcoal-layout` or `flexfox-wechat-draft`. It is the single mechanical stop before external delivery.
- Run `flexfox-charcoal-layout` only after article and title are final. It prepares `过程/wechat-body.md` then locally renders the fixed charcoal inline HTML; skip it for a draft-only request.
- After local layout succeeds, run `flexfox-wechat-draft` only for an explicit draft request, or when both the active Profile and ignored local account config explicitly enable automatic draft delivery. It may create one new draft but must never publish or mass-send.
- Do not save rendered HTML or use raw base64 data URIs in the body. Local relative image paths (e.g. `images/01.png`) are standard and will be automatically uploaded to WeChat CDN during draft creation.
- Report the final title and exact paths of all delivered assets, plus any skipped deliverable and why.
