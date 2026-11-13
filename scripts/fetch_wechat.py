#!/usr/bin/env python3
"""
微信公众号文章与图片通用抓取工具（Zero-dependency）
用法：
  python3 fetch_wechat.py "https://mp.weixin.qq.com/s/xxxx" -o "文章/2026-09-15-示例项目"
"""

import sys
import os
import re
import json
import urllib.request
import urllib.parse
from pathlib import Path

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def clean_title(title):
    return re.sub(r'[\/:*?"<>|\s]+', '-', title).strip('-')

def fetch_article(url, output_dir):
    out_path = Path(output_dir)
    img_dir = out_path / "图片"
    proc_dir = out_path / "过程"
    out_path.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)
    proc_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] 正在抓取微信文章: {url}")
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[!] 请求失败: {e}")
        print("[*] 提示: 若遇微信安全验证拦截，请直接在浏览器中打开链接，右键保存网页内容或复制正文到 过程/来源.md")
        return False

    # 提取标题
    title_match = re.search(r'<h1[^>]*class="[^"]*rich_media_title[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
    raw_title = title_match.group(1).strip() if title_match else "未命名文章"
    raw_title = re.sub(r'<[^>]+>', '', raw_title).strip()

    # 提取作者/公众号
    author_match = re.search(r'<meta\s+property="og:article:author"\s+content="([^"]*)"', html)
    account_match = re.search(r'<strong[^>]*class="[^"]*profile_nickname[^"]*"[^>]*>(.*?)</strong>', html, re.DOTALL)
    account = account_match.group(1).strip() if account_match else (author_match.group(1).strip() if author_match else "未知公众号")

    # 提取正文内容 (rich_media_content / js_content)
    content_match = re.search(r'<div[^>]*id="js_content"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
    if not content_match:
        content_match = re.search(r'<div[^>]*class="[^"]*rich_media_content[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)

    body_html = content_match.group(1) if content_match else ""

    # 提取图片 URL (微信使用 data-src 属性)
    img_urls = re.findall(r'<img[^>]+data-src=["\'](https://[^"\']+)["\']', body_html)
    if not img_urls:
        img_urls = re.findall(r'<img[^>]+src=["\'](https://[^"\']+)["\']', body_html)

    # 过滤与下载图片
    valid_images = []
    print(f"[*] 发现 {len(img_urls)} 张原始图片，开始筛选并下载可用原图...")

    count = 1
    for img_url in img_urls:
        if "mmbiz.qpic.cn" not in img_url and "qpic.cn" not in img_url:
            continue
        # 简单过滤格式
        fmt = "png"
        if "wx_fmt=jpeg" in img_url or "wx_fmt=jpg" in img_url:
            fmt = "jpg"
        elif "wx_fmt=gif" in img_url:
            fmt = "gif"

        filename = f"{count:02d}-素材图.{fmt}"
        target_file = img_dir / filename

        img_req = urllib.request.Request(img_url, headers={**HEADERS, "Referer": url})
        try:
            with urllib.request.urlopen(img_req, timeout=15) as r:
                data = r.read()
            # 过滤 1x1 或极小图标 (< 1KB)
            if len(data) < 1024:
                continue
            target_file.write_bytes(data)
            valid_images.append({
                "file": f"图片/{filename}",
                "size_kb": round(len(data) / 1024, 1),
                "url": img_url
            })
            count += 1
        except Exception as err:
            continue

    print(f"[✓] 成功下载 {len(valid_images)} 张有效图片到 {img_dir}")

    # 简单提取纯文本并格式化为初始 Markdown
    text_content = re.sub(r'<p[^>]*>', '\n\n', body_html)
    text_content = re.sub(r'<br\s*/?>', '\n', text_content)
    text_content = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'\n\n## \1\n\n', text_content)
    text_content = re.sub(r'<[^>]+>', '', text_content)
    text_content = re.sub(r'\n{3,}', '\n\n', text_content).strip()

    # 写入来源备份
    source_md = proc_dir / "来源原文.md"
    source_content = f"# {raw_title}\n\n- **来源链接**：{url}\n- **来源公众号**：{account}\n\n---\n\n## 原文内容\n\n{text_content}\n\n---\n\n## 可用图片列表\n\n"
    for img in valid_images:
        source_content += f"- `![]({img['file']})` ({img['size_kb']} KB)\n"

    source_md.write_text(source_content, encoding="utf-8")
    print(f"[✓] 来源文档已保存在: {source_md}")

    # 初始化生成一个标准的 brief.md 草稿
    brief_md = proc_dir / "brief.md"
    if not brief_md.exists():
        brief_draft = f"""# 论点卡：{raw_title} (二创草稿)

- **受众与情绪**：关注 AI 前沿的普通开发者与效率探索者；带着好奇与求真情绪。
- **核心主线与判断**：[在此提炼1句反直觉判断：不同于原文的独特切入点]。
- **明确不聊**：[不聊宏大叙事，聚焦实测细节]。
- **素材与配图关系**：已下载 {len(valid_images)} 张原图，重点挑选展示核心界面的图片。
- **候选标题**：
  1. {raw_title}
  2. ...
  3. ...
"""
        brief_md.write_text(brief_draft, encoding="utf-8")
        print(f"[✓] 已自动初始化论点卡模板: {brief_md}")

    print(f"\n[★] 抓取完成！请在 {proc_dir}/brief.md 确认主线后启动二创写稿。")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 fetch_wechat.py <文章URL> -o <输出文件夹>")
        sys.exit(1)
    target_url = sys.argv[1]
    out_dir = "文章/新建项目"
    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        if idx + 1 < len(sys.argv):
            out_dir = sys.argv[idx + 1]
    fetch_article(target_url, out_dir)
