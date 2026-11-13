#!/bin/sh
# Does not install or invoke network actions implicitly.
set -eu
base=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python=${FLEXFOX_PYTHON:-"$base/.venv/bin/python3"}
if [ ! -x "$python" ]; then
  if command -v python3 >/dev/null 2>&1; then
    python=$(command -v python3)
  else
    printf '%s\n' '缺少 Python 3。请安装 Python 3.10+ 或设置 FLEXFOX_PYTHON。' >&2
    exit 1
  fi
fi
command=${1:-help}
if [ "$#" -gt 0 ]; then shift; fi
case "$command" in
  preview|check) exec "$python" "$base/scripts/local_wechat.py" "$command" "$@" ;;
  diagnose) exec "$python" "$base/scripts/wechat_delivery_check.py" "$@" ;;
  draft)
    article_dir=''
    need_dir=0
    for arg in "$@"; do
      if [ "$need_dir" -eq 1 ]; then article_dir=$arg; need_dir=0; fi
      case "$arg" in
        --article-dir) need_dir=1 ;;
        --article-dir=*) article_dir=${arg#--article-dir=} ;;
      esac
    done
    if [ -z "$article_dir" ]; then
      printf '%s\n' '缺少 --article-dir 参数。' >&2
      exit 1
    fi
    "$python" "$base/scripts/wechat_delivery_check.py" --article-dir "$article_dir"
    exec "$python" "$base/scripts/wechat_draft.py" draft "$@"
    ;;
  validate) exec "$python" "$base/scripts/wechat_draft.py" validate "$@" ;;
  *) printf '%s\n' '用法：sh 运行环境/wechat.sh preview|check|diagnose|validate|draft [参数]' ;;
esac
