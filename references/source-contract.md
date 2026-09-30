# 多源证据合同

## 目录与抓取

所有链接都放在文章目录下的 `sources/`，不再混用 `source/`、`source_1/` 或“过程/来源”。

```text
articles/YYYY-MM-DD-主题/
├── sources/
│   ├── index.json
│   ├── index.md
│   ├── source_01/
│   │   ├── source.md
│   │   └── images/
│   └── source_02/
└── evidence.md
```

执行：

```bash
python3 scripts/fetch_source.py <URL1> <URL2> ... \
  -o articles/YYYY-MM-DD-主题/sources
```

`index.json` 是来源账本。每个输入链接都必须有 `S01`、`S02` 等编号和 `success` 或 `failed` 状态。任何失败都不能被静默忽略：补充素材、换可访问链接，或在 `brief.md` 记录明确排除原因。

## 证据提纯与覆盖

- `evidence.md` 的每条可核验事实都使用稳定编号并标注来源，如 `- [E01][S01] Pro 套餐……`。
- `brief.md` 的「素材关系与关键证据」只标出本篇真正必须写入的事实，例如 `- [必写] E01：会前缩水通知是开场冲突`。标签不是固定叙事模板：教程、实测、争议、趋势稿分别按自身材料决定。
- `outline.md` 必须列出每节承接的 E 编号。门禁检查的是所有 `[必写]` 事实是否进入大纲，而不是“某个来源是否被随便提过一次”。
- `flexfox-ai-check` 必须在 `review.md` 中逐项记录每个 `[必写] E##` 的正文位置和核验结论；只在大纲里出现、最终正文漏写，判定为失败。
- 多源任务中，每个成功来源至少贡献一条进入 `evidence.md` 的增量事实，并在 `outline.md` 的某个章节被分配；这只是来源完整性的底线，不代替编辑取舍。
- 正文只读取 `evidence.md` 和 `outline.md`，不逐段参照原文，以避免沿用原文语序。
- 来源编号只保留在过程文件，最终 `article.md` 不展示研究标签或工作流痕迹。
- 未在来源中出现的日期、人数、收购、亲历、报错或对话，标为待核验或删除，不能用“像是真的”补上。
