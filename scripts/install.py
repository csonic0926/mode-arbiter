#!/usr/bin/env python3
"""Install Mode Arbiter for Codex into ~/.codex."""
from __future__ import annotations

import datetime as _dt
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

SKILLS = [
    "codex-user-intent-task-calibration",
    "codex-dialogue-state-compression",
    "codex-conversation-mode",
    "codex-continuation-phase-gate",
]


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"installed {dst}")


def update_config() -> None:
    CODEX.mkdir(parents=True, exist_ok=True)
    if CONFIG.exists():
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = CONFIG.with_suffix(f".toml.bak-{stamp}")
        shutil.copy2(CONFIG, backup)
        text = CONFIG.read_text()
    else:
        text = ""

    line = f'model_instructions_file = "{MODEL_INSTRUCTIONS_VALUE}"'
    pattern = re.compile(r'(?m)^\s*model_instructions_file\s*=\s*"[^"]*"\s*$')
    if pattern.search(text):
        text = pattern.sub(line, text)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        if text:
            text += "\n"
        text += line + "\n"

    CONFIG.write_text(text)
    print(f"updated {CONFIG}")


def main() -> None:
    copy_file(ROOT / "mode_arbiter_codex.md", INSTRUCTIONS_DIR / "mode_arbiter_codex.md")
    for skill in SKILLS:
        copy_file(ROOT / "skills" / skill / "SKILL.md", SKILLS_DIR / skill / "SKILL.md")
    update_config()
    print("\nDone. Restart Codex or open a new Codex session for the instruction file to take effect.")


if __name__ == "__main__":
    main()
