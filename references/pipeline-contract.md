# 生产流水线合同

目标是让任何支持读写文件的 AI 都能完成同一条生产线；不是要求它拥有 Codex 的 Skill 运行时。

## 阶段与边界

1. **证据**：抓取来源到 `过程/来源/`、建立 `过程/evidence.md`。未读取的来源写失败，不可凭摘要补事实。
2. **Brief**：在 `过程/brief.md` 选择文章原型、主线、必写事实和图片角色。`guided` 模式在此等用户确认；`auto` 模式只有用户明确授权时使用。
3. **大纲**：在 `过程/outline.md` 将每条必写事实放进对应章节，决定信息轻重；不能用固定故事模板替代编辑判断。
4. **初稿**：只由 writer 修改 `article.md`。
5. **独立审稿**：reviewer 不改正文，只写 `过程/review.md` 与 `过程/review.json`。它必须审查事实、开头兑现、叙事轻重、AI 指纹和读者可读性。
6. **定点返工**：writer 仅处理审稿问题。正文一旦修改，旧 `过程/review.json` 因哈希不匹配自动失效，必须二审。
7. **交付**：`pipeline.py preflight` 通过后才可排版或创建微信草稿。

最多两轮“审稿 → 返工”。第二轮仍有 blocker 或 major 问题时，停止自动投递并请人工决定。

## 审稿回执 `过程/review.json`

```json
{
  "schema_version": 1,
  "article_sha256": "article.md 的 SHA-256",
  "review_round": 1,
  "reviewer": "independent-editor",
  "status": "pass",
  "fact_checks": [
    {"fact_id": "E01", "status": "pass", "location": "第 1 节第 2 段", "reason": "与 evidence.md 一致"}
  ],
  "findings": [],
  "summary": "结论"
}
```

`findings` 的每项使用 `blocker`、`major` 或 `minor`，并写 `location`、原文短引和 `repair`。`pass` 不得包含 blocker/major；每一条 `[必写] E##` 必须有 `fact_checks` 的通过项。

## 命令

```bash
python3 scripts/pipeline.py init --article-dir articles/YYYY-MM-DD-明确主题 --mode guided
python3 scripts/pipeline.py status --article-dir articles/YYYY-MM-DD-明确主题
python3 scripts/pipeline.py preflight --article-dir articles/YYYY-MM-DD-明确主题
```

`status` 会重跑结构门禁；初稿合格但尚未审稿时返回 `ready_for_review`。`preflight` 额外要求审稿状态为 `pass`。这两个命令不生成或重写文章正文。
