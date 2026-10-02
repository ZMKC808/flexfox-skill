---
name: flexfox-adapt
description: Turn one or more WeChat, X/Twitter, or other supported source links into an original FlexFox WeChat article, rather than a summary or repost.
---

# FlexFox 二创与多源提纯

二创的目标是独立立论，不是同义词改写。先读 [多源证据合同](../../references/source-contract.md)；准备写稿时再读 [长文结构合同](../../references/article-contract.md)。

## 流程

1. 抓取用户给出的所有链接；一个也不能静默跳过。

   ```bash
   python3 scripts/fetch_source.py <URL1> <URL2> ... \
     -o articles/YYYY-MM-DD-主题/过程/来源
   ```

2. 检查 `过程/来源/index.json`。存在失败来源时，先补源、换链接或在 `过程/brief.md` 说明为何排除；不能直接继续。
3. 从所有成功来源提炼裸事实写入 `过程/evidence.md`，每条写 `[E01][S01]` 一类事实与来源编号。未证实的日期、人数、收购、测试细节和对话移入待核验项或删除。
4. 先写 `过程/adaptation.md` 与 `过程/brief.md`。Brief 保留旧工作区的自由「素材关系与关键证据」：说明切入镜头、必要背景、核心证据、转折和读者带走的判断各由什么材料承担；不要把它写成所有文章通用的发布会模板。将必须进入正文的事实标为 `[必写] E##`，同时写明本篇图片数量与用途。需要确认立论时停下；已有用户确认则继续执行。
5. 产出 `过程/outline.md`：3–5 个具体小标题；每节列关键事实 E 编号、展开路径、3–5 个语义块预算与配图角色。语义块按空行计，块内不规定行数。每一个成功来源至少在大纲出现一次；每一个 `[必写]` 事实必须在大纲出现一次。
6. 交给 `flexfox-writer` 成稿，并运行结构门禁。最终正文不保留来源标签。

## 独立性边界

- 正文只能读取已提纯的 `过程/evidence.md` 与 `过程/outline.md`，不能逐段改写原文。
- 改变文章的主线、章节顺序和开头/结尾；保留事实，不复制原文语序、形容词和小标题。
- “重合率低于 30%”是编辑审查目标，不得伪造为未执行的精确测算结果。
