# FlexFox 公众号写作系统

FlexFox 是一套可安装、可插拔的公众号写作系统：从微信/推特素材抓取、二创与低重复率重构、标题与摘要，到灵动狐正文、22项 AI 味质检、封面提示词接力、固定转发词、本地炭黑商务排版（Flowcast 离线版），以及公众号草稿箱直推，全链路产出可交付的文章资产。

它默认使用 AI飞升录 Profile，也允许其他账号替换自己的 Profile。

## 核心特性

- **半自动化与人机协同**：在关键节点（Brief 论点卡、标题确定、推草稿箱）设有明确的人工确认门禁，AI 绝不自作主张。
- **内置全能抓取**：自带 `scripts/fetch_source.py`，支持抓取微信公众号（含配图）与 Twitter/X 长推（含高清大图与媒体），自动完成原图清洗与事实提纯。
- **超低重复率二创（< 30%）**：通过“裸事实提取（物理隔离）+ 账号立场乘法 + FlexFox 时间推进轴重构”，彻底杜绝洗稿与同义词机械替换。
- **本地图片直推微信 CDN**：写稿全程支持本地相对路径配图（如 `images/01.png`），在调用微信草稿箱接口时，脚本自动将本地图片上传至微信官方 CDN 并完成内联替换，无需配置或依赖外部图床。
- **Flowcast 离线炭黑排版**：本地固化炭黑商务主题样式（`render_charcoal.py`），生成标准微信兼容内联 HTML，未来支持扩展更多颜色主题。
- **提示词接力生图**：标准化生成 900×383 纯黑白手绘线稿视觉隐喻封面提示词（`images/cover-prompt.md`），可一键交由 GPT、Midjourney、Ideogram 或 Codex 接力生图。
- **单套固定转发词**：严格沿用 5 段式槽位替换，保持极简素人感。

## 安装与快速使用

克隆本仓库到本地环境：

```bash
git clone https://github.com/<owner>/flexfox-wechat-writing-system.git
```

### 生产流水线

1. **抓取素材（微信/推特/X）**：
   ```bash
   python3 scripts/fetch_source.py "https://mp.weixin.qq.com/s/..." -o articles/2026-09-30-主题/过程/来源
   ```
2. **清洗与二创**：
   - AI 清洗垃圾图，保留控制台/代码/报错/账单等证据图至 `images/`，产出 `evidence.md`；
   - 结合 Profile 生成 100 字 Brief 与 5 个候选标题，等待人工确认。
3. **正文撰写与质检**：
   - 确认主线后，AI 采用灵动狐短句瀑布、野比喻、真摩擦细节撰写 `article.md`；
   - 运行 22 项 AI 味指纹审查与去洗稿检查，完成局部微调。
4. **排版与草稿箱投递**：
   - 生成固定转发词 `转发词.md` 与封面提示词 `images/cover-prompt.md`；
   - 本地编译排版：
     ```bash
     python3 scripts/prepare_wechat_body.py --article articles/2026-09-30-主题/article.md --output articles/2026-09-30-主题/wechat-body.md
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
├── evidence.md                   # 裸事实清单与核心数据
├── title-options.md              # 标题研究矩阵与最终标题
├── digest.md                     # 15–20字公众号钩子摘要
├── article.md                    # 唯一正文母本 (内嵌本地相对图片)
├── review.md                     # AI味与去洗稿检查记录
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
