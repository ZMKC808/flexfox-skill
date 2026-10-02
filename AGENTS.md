# FlexFox Agent Entry

For a complete article task, read in this order:

1. `README.md`
2. `skills/flexfox-wechat/SKILL.md`
3. the active Profile (`flexfox-profile.md` or `profiles/ai-feishenglu.md`)
4. `references/pipeline-contract.md`

Create a named article directory and run `python3 scripts/pipeline.py init --article-dir <目录> --mode guided`. Use `auto` only when the user explicitly skips Brief confirmation.

The non-negotiable order is: evidence → Brief → outline → writer → `pipeline.py status` → independent reviewer → targeted rewrite when needed → second reviewer → `pipeline.py preflight` → layout/draft.

`article.md` is the sole prose source. All working files live under `过程/`; only `article.md`、`转发词.md` and `images/` remain at the article root. A reviewer never edits the prose; a writer never self-certifies its review. Do not create a WeChat draft or publish unless `preflight` passes and the user has authorized draft delivery.
