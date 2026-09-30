#!/usr/bin/env python3
"""Create and verify WeChat Official Account drafts from FlexFox charcoal HTML.

Secrets live only in the ignored local config file. This program never logs an
access token or secret, and it refuses to create a draft without an explicit
command-line confirmation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    from .render_charcoal import render_file
except ImportError:  # Script execution, rather than package import.
    from render_charcoal import render_file


API_ROOT = "https://api.weixin.qq.com/cgi-bin"
MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024
IMG_SRC = re.compile(r'(<img\b[^>]*?\bsrc\s*=\s*["\'])([^"\']+)(["\'])', re.IGNORECASE)


class WeChatError(RuntimeError):
    """A concise, credential-safe error from a WeChat API request."""


def die(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_env(path: Path) -> dict[str, str]:
    if not path.exists():
        die(f"No local account config at {path}. Copy assets/wechat-account.example.env first.")
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    needed = ("FLEXFOX_WECHAT_APPID", "FLEXFOX_WECHAT_APPSECRET")
    missing = [key for key in needed if not values.get(key)]
    if missing:
        die("Missing " + ", ".join(missing) + " in local account config.")
    return values


def request_json(url: str, *, data: bytes | None = None, headers: dict[str, str] | None = None) -> dict:
    request = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raise WeChatError(f"WeChat HTTP {error.code}") from error
    except urllib.error.URLError as error:
        raise WeChatError(f"WeChat network request failed: {error.reason}") from error
    try:
        result = json.loads(payload)
    except json.JSONDecodeError as error:
        raise WeChatError("WeChat returned invalid JSON") from error
    if result.get("errcode", 0) != 0:
        raise WeChatError(f"WeChat API {result.get('errcode')}: {result.get('errmsg', 'unknown error')}")
    return result


def access_token(config: dict[str, str]) -> tuple[str, int]:
    query = urllib.parse.urlencode(
        {
            "grant_type": "client_credential",
            "appid": config["FLEXFOX_WECHAT_APPID"],
            "secret": config["FLEXFOX_WECHAT_APPSECRET"],
        }
    )
    result = request_json(f"{API_ROOT}/token?{query}")
    token = result.get("access_token")
    if not isinstance(token, str) or not token:
        raise WeChatError("WeChat returned no access token")
    return token, int(result.get("expires_in", 0))


def download_image(url: str) -> tuple[bytes, str]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"https", "http"}:
        raise WeChatError(f"Unsupported image source: {parsed.scheme or 'relative path'}")
    request = urllib.request.Request(url, headers={"User-Agent": "FlexFox-WeChat-Draft/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read(MAX_DOWNLOAD_BYTES + 1)
            content_type = response.headers.get_content_type()
    except (urllib.error.HTTPError, urllib.error.URLError) as error:
        raise WeChatError(f"Could not download a body image: {url}") from error
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise WeChatError(f"Body image exceeds {MAX_DOWNLOAD_BYTES // 1024 // 1024} MB: {url}")
    if not content_type.startswith("image/"):
        raise WeChatError(f"Body image is not an image response: {url}")
    extension = mimetypes.guess_extension(content_type) or Path(parsed.path).suffix or ".png"
    return data, extension


def multipart_upload(
    url: str,
    token: str,
    field: str,
    filename: str,
    content: bytes,
    mime: str,
    query: dict[str, str] | None = None,
) -> dict:
    try:
        import requests
    except ImportError as error:
        raise WeChatError("The draft uploader needs requests. Run it with: uv run --with requests python3 scripts/wechat_draft.py …") from error
    params = {"access_token": token}
    if query:
        params.update(query)
    try:
        response = requests.post(
            url,
            params=params,
            files={field: (filename, content, mime)},
            timeout=30,
        )
        result = response.json()
    except requests.RequestException as error:
        raise WeChatError(f"WeChat upload request failed: {error}") from error
    except ValueError as error:
        raise WeChatError("WeChat upload returned invalid JSON") from error
    if result.get("errcode", 0) != 0:
        raise WeChatError(f"WeChat API {result.get('errcode')}: {result.get('errmsg', 'unknown error')}")
    return result


def upload_inline_image(token: str, source: str) -> str:
    data, extension = download_image(source)
    try:
        result = multipart_upload(
            f"{API_ROOT}/media/uploadimg",
            token,
            "media",
            "body" + extension,
            data,
            mimetypes.guess_type("body" + extension)[0] or "image/png",
        )
    except WeChatError as error:
        raise WeChatError(f"Body-image upload failed: {error}") from error
    url = result.get("url")
    if not isinstance(url, str) or not url:
        raise WeChatError("WeChat did not return a usable body-image URL")
    return url


def upload_cover(token: str, cover: Path) -> str:
    if not cover.is_file():
        raise WeChatError(f"Cover file does not exist: {cover}")
    suffix = cover.suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png"}:
        raise WeChatError("Cover must be a PNG or JPEG")
    data = cover.read_bytes()
    if not data:
        raise WeChatError("Cover file is empty")
    try:
        result = multipart_upload(
            f"{API_ROOT}/material/add_material",
            token,
            "media",
            cover.name,
            data,
            mimetypes.guess_type(cover.name)[0] or "image/png",
            {"type": "image"},
        )
    except WeChatError as error:
        raise WeChatError(f"Cover upload failed: {error}") from error
    media_id = result.get("media_id")
    if not isinstance(media_id, str) or not media_id:
        raise WeChatError("WeChat did not return a cover media_id")
    return media_id


def replace_images(token: str, html: str) -> tuple[str, int]:
    if "data:" in html or "file:" in html:
        raise WeChatError("Charcoal layout contains data/local images. Use only remote https body images.")
    cache: dict[str, str] = {}
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        source = match.group(2)
        if source not in cache:
            cache[source] = upload_inline_image(token, source)
        count += 1
        return match.group(1) + cache[source] + match.group(3)

    return IMG_SRC.sub(replace, html), count


def create_draft(token: str, *, title: str, digest: str, author: str, cover_media_id: str, html: str, show_cover_pic: int) -> str:
    article = {
        "title": title,
        "author": author,
        "digest": digest,
        "content": html,
        "content_source_url": "",
        "thumb_media_id": cover_media_id,
        "show_cover_pic": show_cover_pic,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }
    result = request_json(
        f"{API_ROOT}/draft/add?{urllib.parse.urlencode({'access_token': token})}",
        data=json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    media_id = result.get("media_id")
    if not isinstance(media_id, str) or not media_id:
        raise WeChatError("WeChat did not return a draft media_id")
    return media_id


def verify_draft(token: str, media_id: str) -> bool:
    result = request_json(
        f"{API_ROOT}/draft/get?{urllib.parse.urlencode({'access_token': token})}",
        data=json.dumps({"media_id": media_id}).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    return bool(result.get("news_item"))


def receipt(article_dir: Path, media_id: str, html: str, images: int, verified: bool) -> Path:
    result = {
        "media_id": media_id,
        "created_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "renderer": "flexfox-charcoal-layout",
        "content_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
        "body_image_count": images,
        "verified": verified,
    }
    path = article_dir / "wechat-draft.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def article_digest(article_dir: Path) -> str:
    path = article_dir / "digest.md"
    if not path.is_file():
        return ""
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    digest = "".join(line for line in lines if line and not line.startswith("#"))
    if len(digest) > 25:
        raise WeChatError("digest.md exceeds the AI飞升录 25-character limit")
    return digest


def command_validate(config: dict[str, str]) -> None:
    _, expires_in = access_token(config)
    suffix = config["FLEXFOX_WECHAT_APPID"][-4:]
    print(f"WeChat credential check passed (AppID ending {suffix}; token TTL {expires_in}s).")


def command_draft(args: argparse.Namespace, config: dict[str, str]) -> None:
    if not args.confirm_draft:
        die("Refusing to create a draft without --confirm-draft.")
    article_dir = args.article_dir.resolve()
    if not article_dir.is_dir():
        die(f"Article directory does not exist: {article_dir}")
    title = args.title.strip()
    if not title:
        die("Draft title must not be empty.")
    body = args.body.resolve() if args.body else article_dir / "wechat-body.md"
    if not body.is_file():
        die(f"No rendered-body source at {body}. Run scripts/prepare_wechat_body.py first.")
    html = render_file(body)
    token, _ = access_token(config)
    rendered, image_count = replace_images(token, html)
    cover = args.cover.resolve() if args.cover else article_dir / "images/cover-900x383.png"
    cover_media_id = upload_cover(token, cover)
    media_id = create_draft(
        token,
        title=title,
        digest=args.digest.strip() if args.digest is not None else article_digest(article_dir),
        author=args.author if args.author is not None else config.get("FLEXFOX_WECHAT_AUTHOR", ""),
        cover_media_id=cover_media_id,
        html=rendered,
        show_cover_pic=int(config.get("FLEXFOX_WECHAT_SHOW_COVER_PIC", "0")),
    )
    verified = verify_draft(token, media_id)
    saved = receipt(article_dir, media_id, rendered, image_count, verified)
    print(f"Draft created and {'verified' if verified else 'not verified'}; receipt: {saved}")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=root / "config/wechat.local.env")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="verify local credentials without creating a draft")
    draft = subparsers.add_parser("draft", help="render the prepared charcoal body and upload it into the draft box")
    draft.add_argument("--article-dir", type=Path, required=True)
    draft.add_argument("--title", required=True)
    draft.add_argument("--digest", help="override digest.md; omit to use the article's digest.md")
    draft.add_argument("--author")
    draft.add_argument("--cover", type=Path)
    draft.add_argument("--body", type=Path, help="override the default article-dir/wechat-body.md")
    draft.add_argument("--confirm-draft", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = parse_env(args.config)
    try:
        if args.command == "validate":
            command_validate(config)
        else:
            command_draft(args, config)
    except WeChatError as error:
        die(str(error))


if __name__ == "__main__":
    main()
