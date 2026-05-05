# Mode Arbiter for Codex

## Author's Note

> If you miss the human-computer interaction experience of Claude Code back when Opus 4.6 was still available, you can try this Codex model instruction.

## What this is

Mode Arbiter for Codex is a public, installable instruction pack for local OpenAI Codex users.

It is intentionally **not** a general LLM prompt collection and not a multi-agent framework. It installs one Codex model instruction file plus four small Codex skills that make local Codex behave more deliberately:

- calibrate the user's real intent before executing;
- choose between exploratory reasoning and disciplined convergence per turn;
- inspect local context before acting on non-trivial tasks;
- avoid premature "next steps" when the task is not actually done;
- keep final user-facing replies compressed and useful.

## Installed files

The installer writes these files into your local Codex config area:

```text
~/.codex/instructions/mode_arbiter_codex.md
~/.codex/skills/codex-user-intent-task-calibration/SKILL.md
~/.codex/skills/codex-dialogue-state-compression/SKILL.md
~/.codex/skills/codex-conversation-mode/SKILL.md
~/.codex/skills/codex-continuation-phase-gate/SKILL.md
```

It also updates `~/.codex/config.toml` with:

```toml
model_instructions_file = "~/.codex/instructions/mode_arbiter_codex.md"
```

If `~/.codex/config.toml` already exists, the installer creates a timestamped backup before editing it.

## Quick install

```bash
git clone https://github.com/csonic0926/mode-arbiter.git
cd mode-arbiter
./install.sh
```

Then restart Codex or open a new Codex session.

## Manual install

```bash
mkdir -p ~/.codex/instructions
mkdir -p ~/.codex/skills

cp mode_arbiter_codex.md ~/.codex/instructions/mode_arbiter_codex.md
cp -R skills/codex-user-intent-task-calibration ~/.codex/skills/
cp -R skills/codex-dialogue-state-compression ~/.codex/skills/
cp -R skills/codex-conversation-mode ~/.codex/skills/
cp -R skills/codex-continuation-phase-gate ~/.codex/skills/
```

Then add this to `~/.codex/config.toml`:

```toml
model_instructions_file = "~/.codex/instructions/mode_arbiter_codex.md"
```

## The two modes

The instruction pack makes Codex surface a small mode header at the start of every response:

```text
HSFRM: dominant
HDPRM: guardrail
```

**HSFRM** is the exploratory mode. It helps with ambiguous, open-ended, creative, or reframing-heavy work.

**HDPRM** is the disciplined convergence mode. It helps with constrained, implementation-heavy, evidence-bound, or correctness-sensitive work.

Most useful Codex work is hybrid: one mode leads and the other acts as a guardrail.

## Included skills

### `codex-user-intent-task-calibration`

Runs at the start of a new or redirected real user request. It separates explicit evidence from likely intent, then routes the turn as either execution or conversation.

### `codex-dialogue-state-compression`

Runs for final user-facing replies after execution tasks. It removes filler and keeps only sentences that move the conversation forward.

### `codex-conversation-mode`

Runs when the request is conversation rather than execution. It keeps Codex from turning casual dialogue into a report.

### `codex-continuation-phase-gate`

Runs for intermediate executor-facing outputs inside unresolved Codex task loops. It prevents half-finished inspection from being presented as a final answer.

## Updating

```bash
cd mode-arbiter
git pull
./install.sh
```

## Uninstalling

Remove the installed files:

```bash
rm -f ~/.codex/instructions/mode_arbiter_codex.md
rm -rf ~/.codex/skills/codex-user-intent-task-calibration
rm -rf ~/.codex/skills/codex-dialogue-state-compression
rm -rf ~/.codex/skills/codex-conversation-mode
rm -rf ~/.codex/skills/codex-continuation-phase-gate
```

Then remove or change this line in `~/.codex/config.toml`:

```toml
model_instructions_file = "~/.codex/instructions/mode_arbiter_codex.md"
```

## Notes and limitations

- This repo targets local OpenAI Codex workflows.
- It assumes Codex can read `~/.codex/instructions` and `~/.codex/skills`.
- It does not try to support Claude Code, ChatGPT custom instructions, Anthropic API, Gemini, or generic agent frameworks.
- The visible mode header is intentional. If you dislike that style, edit the `visible_mode_header` block in `mode_arbiter_codex.md`.

## License

MIT
