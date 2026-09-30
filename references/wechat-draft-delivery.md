# 公众号草稿箱投递

这个模块的终点是**草稿箱**，从不群发、发布或删除已有草稿。

## 本地配置

复制 `assets/wechat-account.example.env` 为 `config/wechat.local.env`，填入公众号后台的 AppID 和 AppSecret。该文件被 Git 忽略；不可提交、分享、写进 Profile 或聊天输出。

在公众号后台的「设置与开发 → 基本配置 → IP 白名单」加入接口实际返回的出网 IPv4；以微信 `40164 invalid ip` 报错中的 IP 为准，不以浏览器查到的 IP 为准。

`FLEXFOX_WECHAT_AUTO_DRAFT=1` 仅适合账号主人明确要求“完成后自动进草稿箱”的账号；默认示例为 `0`。无论开关为何，脚本都要求 `--confirm-draft`，以便调用方在本次任务中明确执行投递。

草稿上传使用 Python 的 `requests`；为避免给用户机器永久安装依赖，统一用 `uv run --with requests python3 scripts/wechat_draft.py …` 调用。

## 投递边界

1. 唯一正文源仍是 `article.md`；本地炭黑排版器由 `wechat-body.md` 在内存生成最终富文本。
2. 脚本不读取剪贴板，也不把原始 HTML 保存到项目。
3. 正文远程图会先上传到微信正文图接口，再替换为微信 URL；封面从 `images/cover-900x383.png` 上传为永久素材。
4. 创建草稿后会立即读取草稿核验，并只写入不含密钥或正文的 `wechat-draft.json` 回执。
5. 草稿摘要默认读取文章目录的 `digest.md`；该文件保持 1–2 句短钩子，不能当长摘要。

失败时停止并报告微信错误；不重复创建草稿，也不转为真实发布。
