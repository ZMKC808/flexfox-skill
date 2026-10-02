#!/usr/bin/env python3
"""Validate a FlexFox long-form article before editing, layout, or draft delivery."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


FRONTMATTER = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
H1 = re.compile(r"^#\s+.*$", re.MULTILINE)
H2 = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
IMAGE = re.compile(r"^!\[[^\]]*\]\([^\n]+\)\s*$")
IMAGE_SOURCE = re.compile(r"^!\[[^\]]*\]\(([^)]+)\)\s*$")
DISPLAY_CHARACTER = re.compile(r"[\u4e00-\u9fffA-Za-z0-9]")
SOURCE_TAG = re.compile(r"\[(S\d{2,})\]")
FACT_TAG = re.compile(r"\[(E\d{2,})\]")
REQUIRED_FACT = re.compile(r"^\s*[-*]\s*\[必写\]\s*(E\d{2,})\b", re.MULTILINE)
STYLE_RED_FLAGS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("否定式翻转", re.compile(r"不是[^\n。！？]{0,30}而是")),
    ("公关连接词", re.compile(r"值得注意的是|总而言之|首先|其次")),
    ("假拟人口头禅", re.compile(r"说白了|说实话")),
    ("长破折号", re.compile(r"——")),
)


def article_body(markdown: str) -> str:
    body = FRONTMATTER.sub("", markdown)
    return H1.sub("", body, count=1).strip()


def count_paragraphs(section: str) -> int:
    """Count blank-line-separated semantic blocks, never physical lines."""
    cleaned_lines = [line for line in section.splitlines() if not IMAGE.fullmatch(line.strip())]
    cleaned = "\n".join(cleaned_lines).strip()
    if not cleaned:
        return 0
    return len([part for part in re.split(r"\n\s*\n", cleaned) if part.strip()])


def style_red_flags(body: str) -> list[dict[str, object]]:
    """Return deterministic review prompts; these never decide the structural gate."""
    flags: list[dict[str, object]] = []
    for name, pattern in STYLE_RED_FLAGS:
        matches = pattern.findall(body)
        if matches:
            flags.append({"name": name, "count": len(matches)})
    return flags


def load_successful_source_ids(path: Path) -> tuple[list[str], list[str]]:
    if not path.is_file():
        return [], [f"缺少来源账本：{path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"无法读取来源账本：{exc}"]
    sources = data.get("sources")
    if not isinstance(sources, list):
        return [], ["来源账本没有 sources 列表"]
    return [str(item["id"]) for item in sources if item.get("status") == "success" and item.get("id")], []


def inspect_images(body: str, root: Path) -> tuple[list[str], list[str], list[str], list[str]]:
    """Return sources, duplicate paths, duplicate local files, and spacing failures."""
    lines = body.splitlines()
    image_lines: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = IMAGE_SOURCE.fullmatch(line.strip())
        if match:
            image_lines.append((index, match.group(1)))

    sources = [source for _, source in image_lines]
    duplicate_paths = sorted({source for source in sources if sources.count(source) > 1})
    duplicate_hashes: list[str] = []
    seen_hashes: dict[str, str] = {}
    for source in sources:
        if source.startswith(("http://", "https://", "data:")):
            continue
        local_path = root / source
        if not local_path.is_file():
            duplicate_hashes.append(f"缺失：{source}")
            continue
        digest = hashlib.sha256(local_path.read_bytes()).hexdigest()
        if digest in seen_hashes:
            duplicate_hashes.append(f"{seen_hashes[digest]} = {source}")
        else:
            seen_hashes[digest] = source

    spacing_failures: list[str] = []
    for (first_index, first_source), (second_index, second_source) in zip(image_lines, image_lines[1:]):
        middle = lines[first_index + 1 : second_index]
        has_prose = any(
            line.strip() and not IMAGE.fullmatch(line.strip()) and not line.lstrip().startswith("#")
            for line in middle
        )
        if not has_prose:
            spacing_failures.append(f"{first_source} 与 {second_source} 之间没有正文段落")
    return sources, duplicate_paths, duplicate_hashes, spacing_failures


def write_reports(directory: Path, report: dict[str, object]) -> None:
    json_path = directory / "structure-check.json"
    md_path = directory / "structure-check.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# 文章结构门禁", "", f"- 状态：{report['status']}", "", "## 指标"]
    for name, value in report["metrics"].items():
        lines.append(f"- {name}：{value}")
    lines.extend(["", "## 结果"])
    checks = report["checks"]
    for check in checks:
        marker = "通过" if check["passed"] else "失败"
        lines.append(f"- [{marker}] {check['name']}：{check['detail']}")
    flags = report["metrics"].get("风格红旗", [])
    lines.extend(["", "## 风格红旗（供独立审稿复核，不影响结构门禁）"])
    if flags:
        for flag in flags:
            lines.append(f"- {flag['name']}：{flag['count']} 处")
    else:
        lines.append("- 无明确禁句命中；仍须进行人工 AI 指纹审稿。")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def process_dir(article_dir: Path) -> Path:
    """Use the compact article layout, while accepting pre-0.9 projects."""
    candidate = article_dir / "过程"
    return candidate if candidate.is_dir() else article_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article", type=Path, required=True, help="Path to article.md")
    parser.add_argument("--sources", type=Path, help="Path to sources/index.json for a multi-source article")
    parser.add_argument("--evidence", type=Path, help="Defaults to 过程/evidence.md when 过程 exists")
    parser.add_argument("--outline", type=Path, help="Defaults to 过程/outline.md when 过程 exists")
    parser.add_argument("--brief", type=Path, help="Defaults to 过程/brief.md when 过程 exists")
    parser.add_argument("--min-han", type=int, default=2200)
    parser.add_argument("--max-han", type=int, default=3000)
    parser.add_argument("--min-images", type=int, default=6)
    parser.add_argument("--max-images", type=int, default=10)
    args = parser.parse_args()

    article = args.article.resolve()
    if not article.is_file():
        raise SystemExit(f"Article not found: {article}")
    root = article.parent
    process = process_dir(root)
    body = article_body(article.read_text(encoding="utf-8"))
    headings = H2.findall(body)
    sections = re.split(r"^##\s+.+?\s*$", body, flags=re.MULTILINE)[1:]
    heading_widths = [len(DISPLAY_CHARACTER.findall(re.sub(r"\s+", "", heading))) for heading in headings]
    paragraph_counts = [count_paragraphs(section) for section in sections]
    han_count = len(re.findall(r"[\u4e00-\u9fff]", "\n".join(line for line in body.splitlines() if not IMAGE.fullmatch(line.strip()))))
    bold_count = len(re.findall(r"\*\*[^*]+\*\*", body))
    red_flags = style_red_flags(body)
    image_sources, duplicate_images, image_file_errors, spacing_failures = inspect_images(body, root)
    image_manifest = root / "images" / "manifest.md"
    manifest_text = image_manifest.read_text(encoding="utf-8") if image_manifest.is_file() else ""
    local_image_sources = [
        source for source in image_sources if not source.startswith(("http://", "https://", "data:"))
    ]
    missing_manifest_entries = [source for source in local_image_sources if source not in manifest_text]

    checks: list[dict[str, object]] = [
        {
            "name": "正文字数",
            "passed": args.min_han <= han_count <= args.max_han,
            "detail": f"{han_count} 汉字；要求 {args.min_han}–{args.max_han}",
        },
        {
            "name": "二级小标题数量",
            "passed": 3 <= len(headings) <= 5,
            "detail": f"{len(headings)} 个；要求 3–5 个",
        },
        {
            "name": "二级小标题长度",
            "passed": bool(headings) and all(4 <= width <= 6 for width in heading_widths),
            "detail": f"{dict(zip(headings, heading_widths))}；要求每个 4–6 个显示字符",
        },
        {
            "name": "小节语义块数",
            "passed": len(paragraph_counts) == len(headings) and all(3 <= count <= 5 for count in paragraph_counts),
            "detail": f"{paragraph_counts}；要求每节 3–5 个空行分隔的语义块，图片不计入",
        },
        {
            "name": "加粗数量",
            "passed": 2 <= bold_count <= 4,
            "detail": f"{bold_count} 处；要求 2–4 处",
        },
        {
            "name": "正文图片数量",
            "passed": args.min_images <= len(image_sources) <= args.max_images,
            "detail": f"{len(image_sources)} 张；要求 {args.min_images}–{args.max_images} 张",
        },
        {
            "name": "图片去重与文件",
            "passed": not duplicate_images and not image_file_errors,
            "detail": "; ".join(duplicate_images + image_file_errors) or "图片路径和本地文件均不重复",
        },
        {
            "name": "图片与正文间隔",
            "passed": not spacing_failures,
            "detail": "; ".join(spacing_failures) or "每两张图之间均有正文段落",
        },
        {
            "name": "图片证据清单",
            "passed": image_manifest.is_file() and not missing_manifest_entries,
            "detail": (
                "缺少 images/manifest.md"
                if not image_manifest.is_file()
                else "未登记：" + ", ".join(missing_manifest_entries)
                if missing_manifest_entries
                else "所有本地正文图均已登记"
            ),
        },
    ]

    if args.sources:
        evidence = (args.evidence or process / "evidence.md").resolve()
        outline = (args.outline or process / "outline.md").resolve()
        brief = (args.brief or process / "brief.md").resolve()
        source_ids, source_errors = load_successful_source_ids(args.sources.resolve())
        evidence_tags = SOURCE_TAG.findall(evidence.read_text(encoding="utf-8")) if evidence.is_file() else []
        outline_tags = SOURCE_TAG.findall(outline.read_text(encoding="utf-8")) if outline.is_file() else []
        evidence_text = evidence.read_text(encoding="utf-8") if evidence.is_file() else ""
        outline_text = outline.read_text(encoding="utf-8") if outline.is_file() else ""
        brief_text = brief.read_text(encoding="utf-8") if brief.is_file() else ""
        required_facts = REQUIRED_FACT.findall(brief_text)
        evidence_facts = FACT_TAG.findall(evidence_text)
        outline_facts = FACT_TAG.findall(outline_text)
        missing_evidence = [source_id for source_id in source_ids if source_id not in evidence_tags]
        missing_outline = [source_id for source_id in source_ids if source_id not in outline_tags]
        missing_fact_evidence = [fact_id for fact_id in required_facts if fact_id not in evidence_facts]
        missing_fact_outline = [fact_id for fact_id in required_facts if fact_id not in outline_facts]
        checks.extend(
            [
                {
                    "name": "来源账本",
                    "passed": not source_errors,
                    "detail": "; ".join(source_errors) if source_errors else f"{len(source_ids)} 个成功来源",
                },
                {
                    "name": "证据覆盖",
                    "passed": evidence.is_file() and not missing_evidence,
                    "detail": "缺少：" + ", ".join(missing_evidence) if missing_evidence else "所有成功来源均进入 evidence.md",
                },
                {
                    "name": "大纲覆盖",
                    "passed": outline.is_file() and not missing_outline,
                    "detail": "缺少：" + ", ".join(missing_outline) if missing_outline else "所有成功来源均被分配到 outline.md",
                },
                {
                    "name": "素材关系与关键证据",
                    "passed": brief.is_file() and "素材关系与关键证据" in brief_text and bool(required_facts),
                    "detail": f"{required_facts} 已标记为必写" if required_facts else "brief.md 缺少「素材关系与关键证据」或 [必写] E## 标记",
                },
                {
                    "name": "必写事实进入大纲",
                    "passed": not missing_fact_evidence and not missing_fact_outline,
                    "detail": (
                        ("evidence 缺少：" + ", ".join(missing_fact_evidence) + "；" if missing_fact_evidence else "")
                        + ("outline 缺少：" + ", ".join(missing_fact_outline) if missing_fact_outline else "所有必写事实均进入大纲")
                    ),
                },
            ]
        )

    report = {
        "status": "pass" if all(bool(check["passed"]) for check in checks) else "needs-revision",
        "article": str(article),
        "metrics": {
            "有效汉字": han_count,
            "二级小标题": len(headings),
            "小标题显示字符数": heading_widths,
            "各节正文语义块数": paragraph_counts,
            "加粗片段": bold_count,
            "正文图片": len(image_sources),
            "图片路径": image_sources,
            "未登记图片": missing_manifest_entries,
            "必写事实": required_facts if args.sources else [],
            "风格红旗": red_flags,
        },
        "checks": checks,
    }
    write_reports(process, report)
    print(f"Article structure check: {report['status']} -> {process / 'structure-check.md'}")
    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
