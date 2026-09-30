# FlexFox 公众号写作系统

FlexFox 是一套可安装、可插拔的公众号写作系统：从微信/推特素材抓取、二创与低重复率重构、标题与摘要，到灵动狐正文、22项 AI 味质检、封面提示词接力、固定转发词、本地炭黑商务排版（Flowcast 离线版），以及公众号草稿箱直推，全链路产出可交付的文章资产。

它默认使用 AI飞升录 Profile，也允许其他账号替换自己的 Profile。

## 核心特性

- **两种运行模式**：手动模式在 Brief、标题和草稿箱保留人工门禁；Gemini 自动交接模式以 `handoff.json` 作为本篇确认，自动完成修复、排版与存草稿，永不发布或群发。
- **内置全能抓取**：自带 `scripts/fetch_source.py`，支持抓取微信公众号（含配图）与 Twitter/X 长推（含高清大图与媒体），为每个输入链接生成带状态的来源账本。
- **可执行的长文门禁**：二创先做来源提纯、素材关系与大纲，再由脚本校验 2,200–3,000 字、3–5 个小标题、每节段落预算、加粗纪律、必写事实、多源覆盖与图片数量/去重/间隔；未通过不能排版或推送。
- **本地图片直推微信 CDN**：写稿全程支持本地相对路径配图（如 `images/01.png`），在调用微信草稿箱接口时，脚本自动将本地图片上传至微信官方 CDN 并完成内联替换，无需配置或依赖外部图床。
- **Flowcast 离线炭黑排版**：本地固化炭黑商务主题样式（`render_charcoal.py`），生成标准微信兼容内联 HTML，未来支持扩展更多颜色主题。
- **提示词接力生图**：标准化生成 900×383 纯黑白手绘线稿视觉隐喻封面提示词（`images/cover-prompt.md`），可一键交由 GPT、Midjourney、Ideogram 或 Codex 接力生图。
- **单套固定转发词**：严格沿用 5 段式槽位替换，保持极简素人感。
- **Gemini 无人交接**：Gemini 在同一项目内写完文章后落 `handoff.json`，Codex 自动接手质检、GPT 封面、转发词、炭黑排版，并在本机账号明确开启自动草稿时创建一篇草稿；永不发布或群发。

## 安装与快速使用

克隆本仓库到本地环境：

```bash
git clone https://github.com/<owner>/flexfox-wechat-writing-system.git
```

### 生产流水线

1. **抓取素材（微信/推特/X）**：
   ```bash
   python3 scripts/fetch_source.py "https://mp.weixin.qq.com/s/..." -o articles/2026-09-30-主题/sources
   ```
2. **清洗与二创**：
   - 检查 `sources/index.json`：每个链接都有 `S01` 编号和成功/失败状态；
   - AI 清洗垃圾图，保留控制台/代码/报错/账单等证据图至 `images/`；以 `[E01][S01]` 标记提纯事实写入 `evidence.md`；
   - 在 `brief.md` 用自由的「素材关系与关键证据」明确本篇必写事实（`[必写] E##`）和图片计划，再让 `outline.md` 分配事实与图片角色；这不是固定事件模板，教程、实测、争议和趋势稿各自组织材料；
   - 深度长文默认 6–8 张正文图、教程/实测 7–10 张；图不能重复或相邻堆放，且要在 `images/manifest.md` 登记来源、用途、文件哈希；手动模式等待人工确认，Gemini 自动交接模式由 `handoff.json` 代替确认。
3. **正文撰写与质检**：
   - 确认主线后，AI 依据大纲采用灵动狐短句瀑布、野比喻、真摩擦细节撰写 `article.md`；
   - 先运行 `python3 scripts/validate_article.py --article articles/2026-09-30-主题/article.md --sources articles/2026-09-30-主题/sources/index.json`；通过后才运行 AI 味与事实审查。
4. **排版与草稿箱投递**：
   - 生成固定转发词 `转发词.md` 与封面提示词 `images/cover-prompt.md`；
   - 默认 AI飞升录 Profile 的本机私密配置须先写入开场 GIF URL；缺失时应停止，不得交付少了首屏组件的排版稿；
   - 本地编译排版：
     ```bash
     python3 scripts/prepare_wechat_body.py --article articles/2026-09-30-主题/article.md --output articles/2026-09-30-主题/wechat-body.md --require-intro-gif
     ```
   - 一键推送草稿箱（需本地配置 `config/wechat.local.env`）：
     ```bash
     uv run --with requests python3 scripts/wechat_draft.py draft \
       --article-dir articles/2026-09-30-主题 \
       --title "终审标题" \
       --confirm-draft
     ```

## 交付文件约定

完整文章输出到：

```text
articles/YYYY-MM-DD-主题/
├── brief.md                      # 读者画像、一句话主线、不聊什么
├── sources/index.json             # 输入链接与抓取状态账本（二创）
├── evidence.md                   # 裸事实清单与核心数据
├── outline.md                     # 章节、证据、段落预算（内部过程）
├── title-options.md              # 标题研究矩阵与最终标题
├── digest.md                     # 15–20字公众号钩子摘要
├── article.md                    # 唯一正文母本 (内嵌本地相对图片)
├── review.md                     # AI味与去洗稿检查记录
├── structure-check.json           # 字数、标题、段落、多源覆盖门禁
├── 转发词.md                     # 单套固定槽位替换转发文案
├── wechat-body.md                # 包含开场组件的排版输入稿
├── wechat-draft.json             # 微信草稿箱推送回执
└── images/
    ├── 01-实操证据.png            # 本地证据配图
    ├── cover-900x383.png         # 最终封面 (如有生图)
    ├── cover-prompt.md           # 封面提示词接力
    └── manifest.md               # 图片证据清单
```

## Profile 插拔与定制

默认读取 `profiles/ai-feishenglu.md`。其他账号只需在项目根目录下放置 `flexfox-profile.md`（可参考 `assets/profile-template.md`），即可自定义立场卡、口癖指纹库、结尾 CTA 与专属视觉风格。

## Gemini 自动交接

Gemini 可直接在本机写作时，读取项目根目录的 [GEMINI.md](GEMINI.md)。它完成一篇完整文章包后在文章目录落 `handoff.json`；Codex 先运行：

```bash
python3 scripts/validate_handoff.py \
  --handoff articles/YYYY-MM-DD-主题/handoff.json
```

交接协议和自动化边界见 [Gemini 交接合同](references/gemini-handoff.md)。若 `handoff.json` 设置 `draft_delivery: true`，并且私密配置同步设置 `FLEXFOX_WECHAT_AUTO_DRAFT=1`，Codex 会在本地排版成功后创建一篇草稿；绝不发布或群发。
