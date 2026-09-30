#!/usr/bin/env python3
"""Upload the account's local opening GIF once and save its WeChat URL locally."""

from __future__ import annotations

import argparse
import mimetypes
from pathlib import Path

try:
    from .wechat_draft import API_ROOT, WeChatError, access_token, multipart_upload, parse_env
except ImportError:  # Script execution, rather than package import.
    from wechat_draft import API_ROOT, WeChatError, access_token, multipart_upload, parse_env


def update_env(path: Path, key: str, value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    prefix = f"{key}="
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = prefix + value
            break
    else:
        lines.append(prefix + value)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=root / "config/wechat.local.env")
    args = parser.parse_args()
    config = parse_env(args.config)
    source_text = config.get("FLEXFOX_WECHAT_INTRO_GIF_PATH", "")
    if not source_text:
        raise SystemExit("Error: FLEXFOX_WECHAT_INTRO_GIF_PATH is not set in the local config.")
    source = Path(source_text).expanduser()
    if not source.is_file():
        raise SystemExit(f"Error: opening GIF does not exist: {source}")
    if source.suffix.lower() != ".gif":
        raise SystemExit("Error: opening asset must be a .gif file.")
    try:
        token, _ = access_token(config)
        result = multipart_upload(
            f"{API_ROOT}/media/uploadimg",
            token,
            "media",
            source.name,
            source.read_bytes(),
            mimetypes.guess_type(source.name)[0] or "image/gif",
        )
    except WeChatError as error:
        raise SystemExit(f"Error: opening GIF upload failed: {error}") from error
    url = result.get("url")
    if not isinstance(url, str) or not url:
        raise SystemExit("Error: WeChat did not return an opening GIF URL.")
    update_env(args.config, "FLEXFOX_WECHAT_INTRO_GIF_URL", url)
    print("Opening GIF uploaded and its URL saved in ignored local config.")


if __name__ == "__main__":
    main()
