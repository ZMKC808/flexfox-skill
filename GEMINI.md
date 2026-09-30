# Gemini → Codex 交接

当本项目中的 Gemini 负责写稿、Codex 负责后半段生产时，Gemini 在写作完成后把同一篇文章放入 `articles/YYYY-MM-DD-明确主题/`，并创建 `handoff.json`。这是给 Codex 的唯一接力信号；正文尚在修改中时不得提前创建。

`handoff.json` 等同于本篇的自动化确认：Gemini 已锁定选题、主线和标题方向，Codex 不再等待用户逐篇确认。Codex 可以在已有 `evidence.md` 的事实边界内修复结构、标题、摘要、正文遗漏、AI 味、封面和排版；证据不足时只能停止并写回执，不能编造。

写入信号前必须已有：`brief.md`、`evidence.md`、`outline.md`、`title-options.md`、`article.md`，以及正文实际使用的 `images/` 文件。二创任务还必须有 `sources/index.json`。

`handoff.json` 固定为：

```json
{
  "schema_version": 1,
  "status": "ready_for_codex",
  "article_dir": "articles/YYYY-MM-DD-明确主题",
  "requested_steps": [
    "structure_gate",
    "ai_check",
    "title_and_digest",
    "cover",
    "share_copy",
    "charcoal_layout"
  ],
  "draft_delivery": true
}
```

不写账号密钥，不发布或群发公众号文章，不伪造 `review.md`、封面或交付回执。`draft_delivery: true` 只表示在排版成功后创建一篇草稿；它还要求本机私密配置同时启用 `FLEXFOX_WECHAT_AUTO_DRAFT=1`。任何一侧未启用都停止在本地排版稿。
