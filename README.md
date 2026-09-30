# FlexFox 公众号写作系统

FlexFox 是一套可安装的公众号写作系统：从来源核验、二创、标题与摘要，到灵动狐正文、AI 味检查、封面、固定转发词、本地炭黑商务排版，以及可选的公众号草稿箱投递，产出可交付的文章资产。

它默认使用 AI飞升录 Profile，也允许其他账号替换自己的 Profile。

## 不做什么

本版本只做一种公众号排版：FlexFox 的“炭黑商务”。不做其他主题、图床、真实发布、群发和数据复盘。它在本机生成稳定的内联富文本并自动存入草稿箱，但永远不会替你发布。

## 安装

发布到 GitHub 后，优先通过 Codex 的插件安装界面安装整个项目。开发期请克隆并加载**整个仓库**；`profiles/`、`references/` 与各 Skill 同属一个可移动的软件包，不能只复制某一个 Skill 文件夹。

```bash
git clone https://github.com/<owner>/flexfox-wechat-writing-system.git
```

不要只复制 `flexfox-writer`：完整写作链还需要 Profile、标题与摘要、核验、二创、AI 检查、封面、固定转发词和排版模块。

## 快速使用

- “写一篇公众号，主题是……”：走完整生产链。
- “研究这个选题”：只产出证据与 Brief。
- “把这个公众号 / X 链接二创成文章”：导入来源、明确复用边界，再重新写成 AI飞升录文章。
- “给这篇文章起标题”：只运行标题模块。
- “检查这篇文章有没有 AI 味”：只运行 `flexfox-ai-check`。
- “给这篇做封面”：只运行封面模块。

完整文章默认输出到当前项目的：

```text
articles/YYYY-MM-DD-主题/
├── brief.md
├── evidence.md
├── title-options.md
├── digest.md
├── article.md
├── review.md
├── 转发词.md
├── wechat-body.md
├── layout-checklist.md
├── wechat-draft.json              # 只在已获授权投递后生成
└── images/
    ├── cover-900x383.png
    ├── cover-prompt.md
    └── manifest.md
```

`article.md` 是唯一正文源。后续排版和发布扩展只能读取它，不能偷偷覆盖它。

`转发词.md` 不是独立创作模块：默认 AI飞升录 Profile 固定句式和篇幅，只替换与本篇有关的场景、工具、步骤与结果。`digest.md` 是 1–2 句的公众号摘要钩子，会自动传给草稿箱接口。

## 炭黑商务排版

当用户要求“排版”或“炭黑商务”时，运行 `flexfox-charcoal-layout`。它把已核对的炭黑商务参数固化为本地的内联 HTML 渲染器：不打开网页、不依赖剪贴板、不保存原始 HTML；草稿箱投递时直接从 `wechat-body.md` 渲染。

正文配图必须是有版权依据的远程 `https://` URL；不要使用本地路径、base64 或把封面塞进正文。单张正文图居中、16px 圆角并保留 28px 下间距。完整数值与验收点在模块的参考文件中。

AI飞升录账号的正文首屏则由私密配置自动插入固定 GIF 和「👋哈喽大家好，我是ai领航员小陆，」。它不是公开 Skill 资产；账号主人先运行 `uv run --with requests python3 scripts/sync_intro_gif.py` 上传一次 GIF，之后每篇 `wechat-body.md` 会自动引用该 URL。

## 自动存草稿箱

草稿箱是一个可选交付适配器，不是公开仓库里的账号配置。账号主人将 `assets/wechat-account.example.env` 复制为被 Git 忽略的 `config/wechat.local.env`，在本机填写凭据并配置微信后台 IP 白名单。随后本地炭黑排版器在内存生成富文本：正文图片上传到微信、封面上传为永久素材、文章新建为一条草稿并被回读核验。项目只保留不含正文或凭据的 `wechat-draft.json` 回执。

默认示例关闭自动投递。只有账号 Profile 与本机私密配置都明确启用时，排版完成后才会自动进入草稿箱。此链路不包含发布或群发。

## Profile

默认读取本插件的 `profiles/ai-feishenglu.md`。如果当前项目根目录存在 `flexfox-profile.md`，则优先读取该文件；可从 `assets/profile-template.md` 复制后修改。

Profile 负责账号身份、读者、口吻、CTA、固定开场、转发句式、标题与封面偏好。FlexFox Skill 负责生产流程、事实边界和写作质量。

## 版权与素材

只提交你拥有版权或明确获得再分发许可的规则、示例、图片和文本。用户提供或第三方来源只能用于当前写作任务，不应提交进本仓库。
