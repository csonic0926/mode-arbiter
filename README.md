# Mode Arbiter for Codex

## Author's Note

> If you miss the human-computer interaction experience of Claude Code back when Opus 4.6 was still available, you can try this Codex model instruction.

## What this is

Mode Arbiter for Codex is a public, installable instruction pack for local OpenAI Codex users. It intentionally replaces the built-in model instructions with its own reasoning and collaboration contract.

It is intentionally **not** a general LLM prompt collection and not a multi-agent framework. It installs one Codex model instruction file plus five small Codex skills that make local Codex:

- use the inferred user intent, rather than the literal request alone, as the boundary for proactive exploration;
- choose independently between exploratory reasoning and disciplined convergence;
- choose independently between delivering a stable result and entering reciprocal DUET co-discovery;
- preserve natural conversation without turning every exchange into a report;
- keep completed execution replies concise without deleting verification, risks, or closure.

## Installed files

The installer writes these files into your local Codex config area:

```text
~/.codex/instructions/mode_arbiter_codex.md
~/.codex/skills/codex-user-intent-task-calibration/SKILL.md
~/.codex/skills/codex-dialogue-state-compression/SKILL.md
~/.codex/skills/codex-conversation-mode/SKILL.md
~/.codex/skills/codex-continuation-phase-gate/SKILL.md
~/.codex/skills/codex-duet-mode/SKILL.md
```

It also updates `~/.codex/config.toml` with:

```toml
model_instructions_file = "~/.codex/instructions/mode_arbiter_codex.md"
```

If `~/.codex/config.toml` already exists, the installer updates only the `model_instructions_file` entry and does not create backup artifacts.

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
cp -R skills/codex-duet-mode ~/.codex/skills/
```

Then add this to `~/.codex/config.toml`:

```toml
model_instructions_file = "~/.codex/instructions/mode_arbiter_codex.md"
```

## Two independent axes

The instruction pack selects one reasoning posture and one collaboration posture on every turn. Codex surfaces both axes in a small header:

```text
HSFRM: dominant
HDPRM: guardrail
COLLAB: duet
```

**HSFRM** is the exploratory mode. It helps with ambiguous, open-ended, creative, or reframing-heavy work.

**HDPRM** is the disciplined convergence mode. It helps with constrained, implementation-heavy, evidence-bound, or correctness-sensitive work.

Most useful Codex work is hybrid: one mode leads and the other acts as a guardrail.

**DELIVERY** returns a sufficiently stable result clearly and self-containedly.

**DUET** makes reciprocal human-model exchange part of the reasoning process. Codex surfaces selected unfinished associations, hypotheses, tensions, or causal gaps so human input can change the frame before it closes. It does not expose raw chain-of-thought, and it does not hard-code human and model strengths as fixed capability boundaries.

## Included skills

### `codex-user-intent-task-calibration`

Runs at the start of a new or redirected real user request. It separates explicit evidence from likely intent and classifies the workflow as execution or conversation without making that label the boundary of proactive thought.

### `codex-dialogue-state-compression`

Runs for final user-facing replies when Task = execution and COLLAB = DELIVERY. It removes dead weight while preserving the outcome, verification, material risks, blockers, and any genuinely required next action.

### `codex-conversation-mode`

Runs when Task = conversation and COLLAB = DELIVERY. It keeps Codex from turning ordinary casual dialogue into a report.

### `codex-continuation-phase-gate`

Runs for intermediate executor-facing outputs inside unresolved Codex task loops. It prevents half-finished inspection from being presented as a final answer.

### `codex-duet-mode`

Runs whenever COLLAB = DUET, regardless of whether the topic is conversation- or execution-shaped. It uses short turns to exchange selected frontier material and seek the smallest human input that can distinguish live paths without forcing a premature deliverable.

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
rm -rf ~/.codex/skills/codex-duet-mode
```

Then remove or change this line in `~/.codex/config.toml`:

```toml
model_instructions_file = "~/.codex/instructions/mode_arbiter_codex.md"
```

## Notes and limitations

- This repo targets local OpenAI Codex workflows.
- It assumes Codex can read `~/.codex/instructions` and `~/.codex/skills`.
- It does not try to support Claude Code, ChatGPT custom instructions, Anthropic API, Gemini, or generic agent frameworks.
- The visible three-line mode header is intentional. If you dislike that style, edit the `visible_mode_header` block in `mode_arbiter_codex.md`.

## License

MIT
