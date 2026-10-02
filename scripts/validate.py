#!/usr/bin/env python3
"""Portable structural checks for the FlexFox public package."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
FORBIDDEN = re.compile(r"/Users/|~/.codex|~/.claude")
CREDENTIAL_VALUE = re.compile(
    r"(?im)^FLEXFOX_WECHAT_APP(?:ID|SECRET)=(?!\s*$|<[^>]+>$)[^\s#]+"
)
MEDIA_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mov"}


def private_profile(path: Path) -> bool:
    """Exclude ignored account-specific overlays from public-package checks."""
    relative = path.relative_to(ROOT)
    return len(relative.parts) > 1 and relative.parts[0] == "profiles" and relative.parts[1].endswith("-private")


def fail(message: str) -> None:
    print(f"Validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def frontmatter(text: str, path: Path) -> dict[str, object]:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail(f"{path.relative_to(ROOT)} is missing YAML frontmatter")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} frontmatter is not a mapping")
    return data


def main() -> None:
    manifest = json.loads((ROOT / "plugin.json").read_text())
    if manifest.get("name") != "flexfox-wechat-writing-system":
        fail("plugin.json has an unexpected package name")

    plugin_manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
    if plugin_manifest.get("name") != manifest["name"]:
        fail("the two plugin manifests disagree on package name")

    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if not skill_dirs:
        fail("no Skills found")

    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            fail(f"{skill_dir.relative_to(ROOT)} has no SKILL.md")
        text = skill_file.read_text()
        metadata = frontmatter(text, skill_file)
        if metadata.get("name") != skill_dir.name:
            fail(f"{skill_file.relative_to(ROOT)} name must match its directory")
        if not isinstance(metadata.get("description"), str) or not metadata["description"].strip():
            fail(f"{skill_file.relative_to(ROOT)} has no usable description")
        for reference in re.findall(r"`(\.\./[^`]+\.md)`", text):
            if not (skill_dir / reference).resolve().exists():
                fail(f"{skill_file.relative_to(ROOT)} points to missing {reference}")

    for directory in (SKILLS, ROOT / "references", ROOT / "profiles", ROOT / "assets"):
        for path in directory.rglob("*"):
            if path.is_file() and not private_profile(path):
                text = path.read_text(errors="ignore")
                if FORBIDDEN.search(text) or CREDENTIAL_VALUE.search(text):
                    fail(f"{path.relative_to(ROOT)} contains a local dependency or credential value")

    for path in ROOT.rglob("*"):
        if (
            ".git" not in path.parts
            and "articles" not in path.parts
            and not private_profile(path)
            and path.is_file()
            and path.suffix.lower() in MEDIA_SUFFIXES
        ):
            fail(f"bundled media is not allowed: {path.relative_to(ROOT)}")

    print(f"FlexFox package validation passed ({len(skill_dirs)} Skills).")


if __name__ == "__main__":
    main()
