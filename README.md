# FlexFox 公众号写作系统

FlexFox 是一套可安装、可插拔的公众号写作系统：从微信/推特素材抓取、二创与低重复率重构、标题与摘要，到灵动狐正文、22项 AI 味质检、原生生图封面、固定转发词、本地炭黑商务排版（Flowcast 离线版），以及公众号草稿箱直推，全链路产出可交付的文章资产。

它默认使用 AI飞升录 Profile，也允许其他账号替换自己的 Profile。

任何支持文件读写的 AI 进入项目时，先读 [AGENTS.md](AGENTS.md)；它不依赖特定厂商的 Skill 运行时。

## 生产方式

FlexFox 不把一篇文章交给一次模型调用“从头做到尾”。它用一个最小流水线：证据 → Brief → 大纲 → 初稿 → 独立审稿 → 定点返工 → 排版/草稿箱。`scripts/pipeline.py` 负责检查每一步留下的产物，并让任何改过的正文自动使旧审稿回执失效。

这不是多 Agent 炫技：一个控制者即可，关键是 writer 与 reviewer 不能在同一轮里互相自证。详见 [生产流水线合同](references/pipeline-contract.md)。

## 核心特性

- **单一生产流程**：Brief、标题和草稿箱保留必要的人工确认，避免隐藏的后台接力或轮询。
- **内置全能抓取**：自带 `scripts/fetch_source.py`，支持抓取微信公众号（含配图）与 Twitter/X 长推（含高清大图与媒体），为每个输入链接生成带状态的来源账本。
- **可执行的长文门禁**：二创先做来源提纯、素材关系与大纲，再由脚本校验 2,200–3,000 字、3–5 个小标题、每节段落预算、加粗纪律、必写事实、多源覆盖与图片数量/去重/间隔；未通过不能排版或推送。
- **本地图片直推微信 CDN**：写稿全程支持本地相对路径配图（如 `images/01.png`），在调用微信草稿箱接口时，脚本自动将本地图片上传至微信官方 CDN 并完成内联替换，无需配置或依赖外部图床。
- **Flowcast 离线炭黑排版**：本地固化炭黑商务主题样式（`render_charcoal.py`），生成标准微信兼容内联 HTML，未来支持扩展更多颜色主题。
- **原生封面生图**：标题锁定后直接生成、检查并保存 900×383 纯黑白手绘线稿封面（`images/cover-900x383.png`），不依赖其他 AI。
- **单套固定转发词**：严格沿用 5 段式槽位替换，保持极简素人感。

## 安装与快速使用

克隆本仓库到本地环境：

```bash
git clone https://github.com/<owner>/flexfox-wechat-writing-system.git
```

### 先配置你的账号

不使用默认 AI飞升录风格时，执行：

```bash
cp assets/profile-template.md flexfox-profile.md
```

然后只需填写 `flexfox-profile.md` 的六类信息：读者与定位、口吻与禁语、判断红线、标题/封面/CTA、开场与转发词、默认排版。没有固定 GIF、转发词或自动草稿箱，就明确写“无”或“否”，系统不会假设存在。

想让文章真正像你的账号，再在本机建立一个不上传 GitHub 的风格包：

```text
flexfox-profile-private/
├── style-guide.md       # 你的写法、边界、常见人工修改
└── corpus/              # 5–10 篇自己认可的历史正文
```

每次写作只取同类型的 2–3 篇参考，避免模型整库模仿或照抄。完整字段见 [Profile 模板](assets/profile-template.md)。

从旧工作区升级时，不要把整套旧 SOP、历史过程文件和抓取素材塞进新仓库。按[旧 SOP 迁移说明](references/legacy-migration.md)只迁移账号配置、规则摘要和少量黄金样本。

### 只有要推微信草稿箱时才配置

复制 `assets/wechat-account.example.env` 为 `config/wechat.local.env`，填写：

- `FLEXFOX_WECHAT_APPID`、`FLEXFOX_WECHAT_APPSECRET`：公众号开发配置；
- `FLEXFOX_WECHAT_AUTHOR`：可选署名；
- `FLEXFOX_WECHAT_AUTO_DRAFT=1`：只有希望已完成文章自动进草稿箱时才开启；默认 `0`；
- GIF 相关字段：只有账号固定首屏 GIF 时填写。

该文件已被 Git 忽略。先运行 `uv run --with requests python3 scripts/wechat_draft.py validate`；验证通过后才能创建草稿。系统只创建草稿，绝不发布或群发。

### 交给 AI 的最短指令

```text
工作区：/你的/flexfox-wechat-writing-system
请先读 AGENTS.md，按 FlexFox 流水线完成一篇公众号文章。
模式：guided（或 auto；仅当我已确认 Brief 时）。
素材：
【粘贴链接、图片说明和核心想法】
```

`guided` 会在 Brief 后等你确认；`auto` 仅适合你已经在素材里明确给过主线与执行授权的情况。

### 生产流水线

1. **抓取素材（微信/推特/X）**：
   ```bash
   python3 scripts/fetch_source.py "https://mp.weixin.qq.com/s/..." -o articles/2026-09-30-主题/过程/来源
   ```
2. **清洗与二创**：
   - 检查 `过程/来源/index.json`：每个链接都有 `S01` 编号和成功/失败状态；
   - AI 清洗垃圾图，保留控制台/代码/报错/账单等证据图至 `images/`；以 `[E01][S01]` 标记提纯事实写入 `过程/evidence.md`；
   - 在 `过程/brief.md` 用自由的「素材关系与关键证据」明确本篇必写事实（`[必写] E##`）和图片计划，再让 `过程/outline.md` 分配事实与图片角色；这不是固定事件模板，教程、实测、争议和趋势稿各自组织材料；
   - 深度长文默认 6–8 张正文图、教程/实测 7–10 张；图不能重复或相邻堆放，且要在 `images/manifest.md` 登记来源、用途、文件哈希；立论仍由用户确认。
3. **正文撰写与质检**：
   - 确认主线后，AI 依据大纲采用灵动狐短句瀑布、野比喻、真摩擦细节撰写 `article.md`；
   - 先运行 `python3 scripts/pipeline.py status --article-dir articles/2026-09-30-主题`；返回 `ready_for_review` 后才运行独立的 AI 味与事实审查。审稿、定点返工和二审完成后，运行 `pipeline.py preflight`。
4. **排版与草稿箱投递**：
   - 生成固定转发词 `转发词.md` 与最终封面 `images/cover-900x383.png`；
   - 默认 AI飞升录 Profile 的本机私密配置须先写入开场 GIF URL；缺失时应停止，不得交付少了首屏组件的排版稿；
   - 本地编译排版：
     ```bash
     python3 scripts/prepare_wechat_body.py --article articles/2026-09-30-主题/article.md --output articles/2026-09-30-主题/过程/wechat-body.md --require-intro-gif
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
├── article.md                    # 唯一正文母本 (内嵌本地相对图片)
├── 转发词.md                     # 单套固定槽位替换转发文案
├── images/
    ├── 01-实操证据.png            # 本地证据配图
    ├── cover-900x383.png         # 原生生图生成的最终封面
│   └── manifest.md               # 图片证据清单
└── 过程/                         # 所有工作记录，不影响日常查看
    ├── 来源/index.json            # 输入链接与抓取状态账本（二创）
    ├── brief.md / evidence.md / outline.md
    ├── title-options.md / digest.md
    ├── review.md / review.json
    ├── pipeline.json / structure-check.json
    └── wechat-body.md / wechat-draft.json
```

## Profile 插拔与定制

默认读取 `profiles/ai-feishenglu.md`。其他账号只需在项目根目录下放置 `flexfox-profile.md`（可参考 `assets/profile-template.md`），即可自定义立场卡、口癖指纹库、结尾 CTA 与专属视觉风格。

AI飞升录的历史语料可放在本机 `profiles/ai-feishenglu-private/`。该目录默认被 Git 忽略，不会连同第三方图片、来源归档或账号内容发布到公共仓库；其他账号替换成自己的私有样本即可。
