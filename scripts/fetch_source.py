#!/usr/bin/env python3
"""Unified source and image scraper for WeChat Official Accounts and Twitter/X.

Supports scraping multiple URLs in a single run.
Downloads article/tweet text into Markdown and saves all associated images locally.
Zero external dependencies (uses standard library urllib, json, re, html).
"""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
WECHAT_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.50 NetType/WIFI Language/zh_CN"
)


def log(msg: str) -> None:
    print(f"[fetch_source] {msg}")


def download_file(url: str, dest_path: Path, ua: str = USER_AGENT) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua, "Referer": url})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_bytes(data)
            return True
    except Exception as e:
        log(f"Failed to download image {url}: {e}")
        return False


def clean_html_text(raw_html: str) -> str:
    text = re.sub(r"<!--.*?-->", "", raw_html, flags=re.DOTALL)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<script.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return text


def fetch_wechat(url: str, out_dir: Path) -> Path:
    log(f"Fetching WeChat article: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": WECHAT_UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw_content = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        log(f"Error fetching WeChat URL ({url}): {e}")
        return out_dir / "error.txt"

    out_dir.mkdir(parents=True, exist_ok=True)
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "raw.html").write_text(raw_content, encoding="utf-8")

    # Check for anti-spider or verification
    if "环境异常" in raw_content or "访问过于频繁" in raw_content:
        log("Warning: Triggered WeChat anti-crawler verification.")
        log("Fallback: Save the page manually in your browser as raw.html in the output directory.")

    # Extract title
    title_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', raw_content) or \
                  re.search(r'<h1[^>]*class="[^"]*rich_media_title[^"]*"[^>]*>(.*?)</h1>', raw_content, re.DOTALL)
    title = html.unescape(title_match.group(1).strip()) if title_match else "未命名微信文章"

    # Extract author
    author_match = re.search(r'<meta\s+property="og:article:author"\s+content="([^"]+)"', raw_content) or \
                   re.search(r'<meta\s+name="author"\s+content="([^"]+)"', raw_content)
    author = html.unescape(author_match.group(1).strip()) if author_match else "微信作者"

    # Extract body content container
    content_match = re.search(r'<div[^>]*id="js_content"[^>]*>(.*?)</div>\s*(?:<!--\s*end js_content\s*-->|<div[^>]*class="rich_media_tool"|<script)', raw_content, re.DOTALL)
    body_html = content_match.group(1) if content_match else raw_content

    # Extract and download images
    img_counter = 1
    image_manifest = []

    def replace_img(m: re.Match) -> str:
        nonlocal img_counter
        tag = m.group(0)
        src_match = re.search(r'data-src=["\']([^"\']+)["\']', tag) or re.search(r'src=["\']([^"\']+)["\']', tag)
        if not src_match:
            return ""
        img_url = src_match.group(1)
        if img_url.startswith("data:") or "res.wx.qq.com" in img_url:
            return ""

        fmt_match = re.search(r'wx_fmt=([a-zA-Z0-9]+)', img_url)
        ext = f".{fmt_match.group(1)}" if fmt_match else ".png"
        filename = f"img_{img_counter:02d}{ext}"
        dest = images_dir / filename
        
        success = download_file(img_url, dest, ua=WECHAT_UA)
        if success:
            image_manifest.append({"index": img_counter, "file": f"images/{filename}", "origin": img_url})
            res = f"\n\n![图片](images/{filename})\n\n"
            img_counter += 1
            return res
        return ""

    body_md = re.sub(r'<img\b[^>]*>', replace_img, body_html, flags=re.IGNORECASE)

    # Clean HTML tags to simple markdown-like text
    body_md = clean_html_text(body_md)
    body_md = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', lambda m: f"\n\n## {m.group(1).strip()}\n\n", body_md, flags=re.DOTALL)
    body_md = re.sub(r'<p[^>]*>(.*?)</p>', lambda m: f"\n\n{m.group(1).strip()}\n\n", body_md, flags=re.DOTALL)
    body_md = re.sub(r'<section[^>]*>(.*?)</section>', lambda m: f"\n\n{m.group(1).strip()}\n\n", body_md, flags=re.DOTALL)
    body_md = re.sub(r'<br\s*/?>', "\n", body_md, flags=re.IGNORECASE)
    body_md = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', body_md, flags=re.DOTALL)
    body_md = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', body_md, flags=re.DOTALL)
    body_md = re.sub(r'<[^>]+>', "", body_md)
    body_md = html.unescape(body_md)
    body_md = re.sub(r'\n{3,}', '\n\n', body_md).strip()

    source_md = f"""# {title}

- 来源平台：微信公众号
- 原文作者：{author}
- 原文链接：{url}
- 下载图片：共 {len(image_manifest)} 张

---

{body_md}
"""
    target_file = out_dir / "source.md"
    target_file.write_text(source_md, encoding="utf-8")
    
    # Save manifest
    manifest_file = out_dir / "image-manifest.json"
    manifest_file.write_text(json.dumps(image_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    log(f"Successfully scraped WeChat article: '{title}' ({len(image_manifest)} images) -> {target_file}")
    return target_file


def fetch_twitter_x(url: str, out_dir: Path) -> Path:
    log(f"Fetching Twitter/X post: {url}")
    m = re.search(r'(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)/status/(\d+)', url)
    if not m:
        log(f"Invalid Twitter/X status URL: {url}")
        return out_dir / "error.txt"
    screen_name, status_id = m.group(1), m.group(2)

    api_url = f"https://api.fxtwitter.com/{screen_name}/status/{status_id}"
    req = urllib.request.Request(api_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        log(f"Failed to query Twitter API mirror ({api_url}): {e}")
        return out_dir / "error.txt"

    tweet = data.get("tweet", {})
    if not tweet:
        log(f"Empty tweet data returned by API mirror for {url}")
        return out_dir / "error.txt"

    author = tweet.get("author", {})
    author_name = author.get("name", screen_name)
    author_screen = author.get("screen_name", screen_name)
    tweet_text = tweet.get("text", "")
    created_at = tweet.get("created_at", "")
    likes = tweet.get("likes", 0)
    retweets = tweet.get("retweets", 0)
    replies = tweet.get("replies", 0)

    out_dir.mkdir(parents=True, exist_ok=True)
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    media = tweet.get("media", {})
    photos = media.get("photos", []) or []
    all_media_urls = [p.get("url") for p in photos if p.get("url")]

    img_counter = 1
    image_manifest = []
    media_markdown_blocks = []

    for img_url in all_media_urls:
        ext = Path(urllib.parse.urlparse(img_url).path).suffix or ".jpg"
        filename = f"tweet_img_{img_counter:02d}{ext}"
        dest = images_dir / filename
        if download_file(img_url, dest):
            image_manifest.append({"index": img_counter, "file": f"images/{filename}", "origin": img_url})
            media_markdown_blocks.append(f"![推特媒体](images/{filename})")
            img_counter += 1

    media_section = "\n\n".join(media_markdown_blocks)
    source_md = f"""# 推特/X 来源：@{author_screen} ({author_name})

- 原文链接：{url}
- 发布时间：{created_at}
- 数据指标：赞 {likes} | 转 {retweets} | 评 {replies}
- 配图数量：{len(image_manifest)} 张

## 推文正文

{tweet_text}

## 附带媒体证据

{media_section}
"""
    target_file = out_dir / "source.md"
    target_file.write_text(source_md, encoding="utf-8")
    
    # Save manifest
    manifest_file = out_dir / "image-manifest.json"
    manifest_file.write_text(json.dumps(image_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    log(f"Successfully scraped Twitter/X tweet: @{author_screen} ({len(image_manifest)} images) -> {target_file}")
    return target_file


def process_single_url(url: str, target_dir: Path) -> Path:
    if "mp.weixin.qq.com" in url:
        return fetch_wechat(url, target_dir)
    elif "x.com" in url or "twitter.com" in url:
        return fetch_twitter_x(url, target_dir)
    else:
        log(f"Unsupported URL: {url}")
        return target_dir / "error.txt"


def source_record(source_id: str, url: str, base_dir: Path, result: Path) -> dict[str, object]:
    """Create a durable source-ledger record for every input URL."""
    record: dict[str, object] = {
        "id": source_id,
        "url": url,
        "status": "failed",
        "path": str(result.relative_to(base_dir)) if result.is_relative_to(base_dir) else str(result),
        "title": None,
        "image_count": 0,
    }
    if not (result.is_file() and result.name == "source.md"):
        return record

    lines = result.read_text(encoding="utf-8", errors="replace").splitlines()
    record["status"] = "success"
    record["title"] = lines[0].removeprefix("# ") if lines else "未命名来源"
    manifest = result.parent / "image-manifest.json"
    if manifest.is_file():
        try:
            images = json.loads(manifest.read_text(encoding="utf-8"))
            record["image_count"] = len(images) if isinstance(images, list) else 0
        except json.JSONDecodeError:
            pass
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch one or more WeChat articles or Twitter/X tweets with images.")
    parser.add_argument("urls", nargs="+", help="One or more target URLs (mp.weixin.qq.com or x.com/twitter.com)")
    parser.add_argument("-o", "--output", default="source", help="Output base directory to save source files and images/")
    args = parser.parse_args()

    base_dir = Path(args.output).resolve()
    urls = [u.strip() for u in args.urls if u.strip()]

    base_dir.mkdir(parents=True, exist_ok=True)
    log(f"Processing {len(urls)} URL(s) into {base_dir}...")
    records: list[dict[str, object]] = []
    for idx, url in enumerate(urls, 1):
        source_id = f"S{idx:02d}"
        sub_dir = base_dir / f"source_{idx:02d}"
        result = process_single_url(url, sub_dir)
        records.append(source_record(source_id, url, base_dir, result))

    index = {"schema_version": 1, "sources": records}
    (base_dir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary_lines = [f"# 来源账本（共 {len(records)} 个输入）\n"]
    for record in records:
        summary_lines.extend(
            [
                f"## [{record['id']}] {record['title'] or '抓取失败'}",
                f"- 状态：{record['status']}",
                f"- 链接：{record['url']}",
                f"- 路径：`{record['path']}`",
                f"- 图片：{record['image_count']} 张\n",
            ]
        )
    (base_dir / "index.md").write_text("\n".join(summary_lines), encoding="utf-8")
    log(f"Source ledger written to {base_dir / 'index.json'}")


if __name__ == "__main__":
    main()
