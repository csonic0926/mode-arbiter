# Mode Arbiter

A dual-mode reasoning framework that can be used as a system prompt for any LLM. It instructs the model to dynamically choose between two cognitive postures — exploratory semantic reasoning and disciplined convergent reasoning — based on the shape of each task.

## The Two Modes

**HSFRM** (Hermeneutic Semantic Frame Reasoning Mode) — reasons in meaning space before committing to wording. Best for ambiguous, open-ended, creative, or conceptually blocked tasks.

**HDPRM** (High-Discipline Pragmatic Reasoning Mode) — produces one best answer through fast intuition and evidence-sensitive audit. Best for constrained, accuracy-sensitive, implementation-heavy tasks.

The model automatically selects the dominant mode (or a hybrid) per turn, and surfaces its choice in a visible header:

```
HSFRM: dominant
HDPRM: guardrail
```

## Key Features

- **Task shape sensing** — the model evaluates each task across dimensions like ambiguity pressure, evidence pressure, and convergence need to pick the right mode
- **Hybrid policy** — one mode leads, the other acts as guardrail (not two full passes)
- **Confidence calibration** — output hedging scales with internal confidence, using exactly one uncertainty label
- **Operator triggers** — steer the model with `[MODE_AUTO]`, `[MODE_REOPEN]`, or `[MODE_TIGHTEN]`

## Setup

The core prompt is in [`mode_arbiter.md`](mode_arbiter.md). Use it as a system prompt in any LLM that supports one.

### General Usage

Paste the contents of `mode_arbiter.md` into the system prompt field of your preferred tool — ChatGPT custom instructions, API calls, or any interface that lets you set a system-level prompt.

### Claude Code

Copy the prompt into your global `CLAUDE.md`:

```bash
cp mode_arbiter.md ~/.claude/CLAUDE.md
```

Or append it to an existing `CLAUDE.md`:

```bash
cat mode_arbiter.md >> ~/.claude/CLAUDE.md
```

### OpenAI Codex

1. Copy the prompt to Codex's instructions directory:

```bash
mkdir -p ~/.codex/instructions
cp mode_arbiter.md ~/.codex/instructions/mode_arbiter.md
```

2. Add the following to your `~/.codex/config.toml`:

```toml
model_instructions_file = "/YOUR/HOME/PATH/.codex/instructions/mode_arbiter.md"
developer_instructions = "Always follow the model_instructions_file first!"
```

Replace `/YOUR/HOME/PATH` with your actual home directory path.

### API Usage

Works with any chat completion API that accepts a system message:

```python
# Anthropic
client.messages.create(
    model="claude-sonnet-4-20250514",
    system=open("mode_arbiter.md").read(),
    messages=[{"role": "user", "content": "your prompt"}],
)

# OpenAI
client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": open("mode_arbiter.md").read()},
        {"role": "user", "content": "your prompt"},
    ],
)
```

## Tested With

- Claude Opus 4.6 / Sonnet 4.6 (Claude Code)
- GPT-5.4 / GPT-4o (OpenAI Codex)

Should work with any instruction-following model. Results may vary with smaller or less capable models.

## Evaluation

An A/B evaluation framework is included to measure whether the prompt actually improves response quality on open-ended tasks.

### How it works

1. **30 eval tasks** (`eval_tasks.json`) designed to favor HSFRM-style reasoning: ambiguous requirements, XY problems, conceptual exploration
2. **Paired comparison**: each task is run twice per model — with and without the framework prompt
3. **Blind LLM judge**: responses are randomly assigned as A/B and judged by a separate model against task-specific rubrics
4. **Per-model results**: stored separately since the same prompt behaves differently across models and system prompt mechanisms

### Running the eval

```bash
pip install anthropic openai

# Test one model
python eval/run_eval.py --models claude-sonnet-4-20250514 --judge claude-sonnet-4-20250514

# Test multiple models
python eval/run_eval.py --models claude-sonnet-4-20250514 gpt-4o --judge claude-sonnet-4-20250514

# Run specific tasks only
python eval/run_eval.py --models claude-sonnet-4-20250514 --judge claude-sonnet-4-20250514 --tasks ambig-make-faster reframe-add-caching
```

Results are saved per-task in `eval/results/<model>/` (gitignored). Each run resumes where it left off, so you can interrupt and continue.

## Honest Disclaimers

- The visible mode header reliably appears. Whether the model truly follows the multi-stage internal reasoning as described is hard to verify — treat it as structured guidance, not a guaranteed cognitive architecture.
- This was built for one person's workflow and preferences. You will likely want to adapt it.
- The XML tag structure is intentional — it helps models parse structured instructions more reliably.

## License

MIT
