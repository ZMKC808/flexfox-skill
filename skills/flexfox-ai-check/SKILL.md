---
name: flexfox-ai-check
description: Use when checking or repairing AI-sounding, templated, overly polished, or untrustworthy prose in a FlexFox WeChat Official Account article.
---

# FlexFox AI 检查

This is an editorial quality gate, not a disguise exercise. The aim is clearer thinking, real evidence, and the author's own voice.

Read the Profile, `article.md`, `brief.md`, and `evidence.md`. Write `review.md` in source order. Quote each problem passage, name the problem, and state the smallest safe repair.

## Blockers: fix before delivery

- fabricated experience, person, dialogue, date, number, quote, test result, or source;
- a claim that contradicts `evidence.md`;
- a headline promise not delivered in the opening;
- collaboration traces such as “按你的要求”“我先写一版”.

## AI-pattern check

Inspect context, rather than mechanically banning a phrase:

1. repeated “不是 X 而是 Y” reversals;
2. smooth three-part parallelism or repeated sentence molds;
3. guide voice: “首先/其次/最后/下面说三点”；
4. every paragraph ending in a polished slogan;
5. abstract words explaining another abstract word;
6. false specificity and invented sensory scenes;
7. empty connectors, translationese, or stock emotional reactions;
8. a title-hook-pain-promise opening that sells anxiety before giving information;
9. overuse of em dashes, quotation marks, bolding, or one-sentence fragments;
10. hollow philosophical uplift instead of returning to the reader's real situation.

## Repair protocol

1. Preserve a clean passage; do not invent faults to fill a report.
2. Send only the flagged passages and their intended meaning to `flexfox-writer`.
3. Recheck the repaired passages, source claims, and first 100 words.
4. Mark `pass` only when blockers are resolved. A pass does not certify factual claims that have no source.

Use this structure:

```md
# 编辑与 AI 检查

## 通过项
-

## 待修订
### 1. 位置或小节
> 原文

问题：
修改方向：

## 复检
- 状态：pass / needs-input
- 未解决风险：
```
