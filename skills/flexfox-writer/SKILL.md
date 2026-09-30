---
name: flexfox-writer
description: Draft or revise a FlexFox WeChat long-form article after its brief, evidence, and outline are ready. Do not use for titles, share copy, or short-form posts.
---

# 灵动狐正文写作

先读当前 Profile、`brief.md`、`evidence.md` 与 `outline.md`。再读 [长文结构合同](../../references/article-contract.md)。正文只写入 `article.md`；不得把大纲、来源编号或质检过程混入成稿。

## 写作原则

- 每个判断落在已核验的事实、场景、物件、动作或数据上。没有亲测证据时，使用观察者口吻，不能假装自己经历过。
- 先写冷事实和现场摩擦，再给判断。比喻只能帮助读者理解具体事实，不能替代事实。
- 文章以章节推进，不以“每段一个时间戳”推进；时间或场景只在真实转折处切换。
- 开场三句内交代事件、冲突或账本。结尾回到读者的现实，并使用 Profile 固定 CTA。
- 配图按 `brief.md` 的图片计划和 `outline.md` 的章节角色执行。默认深度长文 6–8 张，实测/教程可 7–10 张；只用已清洗的证据图、关键 UI、步骤或数据图，独占一行，前后文说明它证明什么。图片不重复，也不相邻。

## 执行

1. 严格按 `outline.md` 的章节、关键事实、段落预算和图片角色写初稿。
2. 自查结构合同、事实边界、2–4 处加粗、图片数量、去重和图片与段落的间隔。
3. 运行结构门禁；失败则依报告重写缺失章节。最多两轮，仍失败时停止并请求人工决定。

```bash
python3 scripts/validate_article.py \
  --article articles/YYYY-MM-DD-主题/article.md \
  --sources articles/YYYY-MM-DD-主题/sources/index.json
```

通过前不能调用排版、草稿箱或把 `review.md` 写成通过。
