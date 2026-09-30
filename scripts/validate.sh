#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it from https://docs.astral.sh/uv/" >&2
  exit 1
fi

uv run --with pyyaml python3 "$repo_root/scripts/validate.py"
PYTHONDONTWRITEBYTECODE=1 python3 "$repo_root/scripts/test_renderer.py"
PYTHONDONTWRITEBYTECODE=1 python3 "$repo_root/scripts/test_article_validator.py"
PYTHONDONTWRITEBYTECODE=1 python3 "$repo_root/scripts/test_prepare_wechat_body.py"
PYTHONDONTWRITEBYTECODE=1 python3 "$repo_root/scripts/test_handoff_validator.py"
