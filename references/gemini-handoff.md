# Gemini → Codex 自动交接合同

## 目标与边界

Gemini 写完文章资产后，用 `handoff.json` 通知 Codex 接管后半段。通知从不授权发布或群发。它可在**同时满足** `draft_delivery: true`、包含 `charcoal_layout`、并且本机私密配置启用 `FLEXFOX_WECHAT_AUTO_DRAFT=1` 时，创建一篇草稿；否则只完成本地排版。

## 交接文件

文件必须位于文章目录根部，例如：

```text
articles/2026-10-01-主题/
├── article.md
├── brief.md
├── evidence.md
├── outline.md
├── title-options.md
├── images/
└── handoff.json
```

二创任务另需 `sources/index.json`。`article_dir` 必须是仓库内的 `articles/` 相对路径，禁止绝对路径和 `..` 路径。

## 协议

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

`requested_steps` 只能从以下选择：`structure_gate`、`ai_check`、`title_and_digest`、`cover`、`share_copy`、`charcoal_layout`。`draft_delivery` 是单独布尔开关；为 `true` 时必须同时请求 `charcoal_layout`。

## Codex 接力顺序

1. 运行 `scripts/validate_handoff.py --handoff <文章目录>/handoff.json`；验证失败时停止并写明缺失项，不猜测或补造 Gemini 的内容。
2. 依次执行请求步骤。`structure_gate` 不通过时，停止后续流程；`ai_check` 中任一必写事实未在正文定位时，退回待修。
3. 成功后，在文章目录创建 `codex-handoff-receipt.json`，只记录状态、已完成步骤、失败原因（如有）和时间；不得记录正文、密钥或微信 media ID。
4. 若 `draft_delivery: true` 且本机私密配置 `FLEXFOX_WECHAT_AUTO_DRAFT=1`，先验证微信凭据，再创建并回读一篇草稿，写入 `wechat-draft.json`。任何失败立即停止，不重试、不创建第二篇草稿。
5. 自动交接永远不调用发布或群发接口。
