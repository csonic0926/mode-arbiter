#!/usr/bin/env python3
"""Install Mode Arbiter for Codex into ~/.codex."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path.home()
CODEX = HOME / ".codex"
INSTRUCTIONS_DIR = CODEX / "instructions"
SKILLS_DIR = CODEX / "skills"
CONFIG = CODEX / "config.toml"
MODEL_INSTRUCTIONS_VALUE = "~/.codex/instructions/mode_arbiter_codex.md"
ROOT_MODEL_INSTRUCTIONS_PATTERN = re.compile(
    r'''(?m)^[ \t]*(?:model_instructions_file|"model_instructions_file"|'model_instructions_file')[ \t]*=[^\r\n]*(?:\r?\n|$)'''
)
TABLE_HEADER_PATTERN = re.compile(
    r"(?m)^[ \t]*\[{1,2}[^\[\]\r\n]+\]{1,2}[ \t]*(?:#.*)?(?:\r?\n|$)"
)

SKILLS = [
    "codex-user-intent-task-calibration",
    "codex-dialogue-state-compression",
    "codex-conversation-mode",
    "codex-continuation-phase-gate",
    "codex-duet-mode",
]


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"installed {dst}")


def set_root_model_instructions(text: str) -> str:
    """Set one root-level model_instructions_file without rewriting TOML tables."""
    line = f'model_instructions_file = "{MODEL_INSTRUCTIONS_VALUE}"'
    table_match = TABLE_HEADER_PATTERN.search(text)
    root_end = table_match.start() if table_match else len(text)
    root = ROOT_MODEL_INSTRUCTIONS_PATTERN.sub("", text[:root_end])
    body = root + text[root_end:]

    if not body:
        return line + "\n"
    separator = "" if body.startswith(("\n", "\r")) else "\n"
    return line + "\n" + separator + body


def update_config() -> None:
    CODEX.mkdir(parents=True, exist_ok=True)
    if CONFIG.exists():
        text = CONFIG.read_text()
    else:
        text = ""

    CONFIG.write_text(set_root_model_instructions(text))
    print(f"updated {CONFIG}")


def main() -> None:
    copy_file(ROOT / "mode_arbiter_codex.md", INSTRUCTIONS_DIR / "mode_arbiter_codex.md")
    for skill in SKILLS:
        copy_file(ROOT / "skills" / skill / "SKILL.md", SKILLS_DIR / skill / "SKILL.md")
    update_config()
    print("\nDone. Restart Codex or open a new Codex session for the instruction file to take effect.")


if __name__ == "__main__":
    main()
