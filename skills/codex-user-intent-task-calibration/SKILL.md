---
name: codex-user-intent-task-calibration
description: Calibrate the task when a real user request first enters Codex. Infer the user's actual purpose before execution, without overwriting explicit constraints.
---

## Trigger Timing

Trigger only when Codex receives a new real user request that starts or materially redirects a task.

Do not trigger for intermediate Codex continuation outputs, final user-facing answers, tool results, patch summaries, or routine execution steps.

If the input is only a continuation of an already-calibrated task, do not trigger unless the user changes the goal, constraints, or correction target.

## Purpose

Before execution, establish the task state:

- What the user explicitly asked.
- What artifact, behavior, prompt, code, or workflow is being targeted.
- What the user likely wants fixed, preserved, or clarified.
- What constraints, invariants, and locked behaviors must not be overwritten.

## Task Calibration Rule

Do not jump from user request directly to solutioning.

First separate:

Found = explicit user request and visible evidence.
Inferred = likely user purpose, marked uncertain when needed.
Task = corrected execution target based on Found + Inferred.

The calibrated task may refine the user request, but must not contradict explicit user instructions.

## Artifact Scope Rule

Trigger this rule only when execution could affect more than one similar artifact.

Before expanding the task beyond the requested target, identify each candidate artifact's consumer or audience, source-of-truth or deployment role, and whether divergence may be intentional.

Treat scope expansion as Inferred unless the user explicitly requested synchronization. Similar content, names, or locations do not establish shared ownership or justify synchronized changes.

Apply the change to multiple artifacts only when its rationale holds independently for every consumer or the user explicitly requests propagation.

## Routing

After calibration, determine the task type:

**Task = execution** — the user wants something built, fixed, analyzed, or changed. Proceed to execution. Final output uses `codex-dialogue-state-compression` (`~/.codex/skills/codex-dialogue-state-compression/SKILL.md`).

**Task = conversation** — the user is chatting, venting, exploring ideas, or explicitly not requesting an action. Route to `codex-conversation-mode` (`~/.codex/skills/codex-conversation-mode/SKILL.md`). Do not apply codex-dialogue-state-compression.

### Conversation detection signals

Route to conversation when **any** of these hold:

- No identifiable execution target, artifact, code, or workflow.
- User explicitly signals casual intent (e.g. "聊聊", "隨便講", "chat", "just talking").
- User is sharing a feeling, reaction, or personal moment without asking for action.
- User is complaining about the model's own behavior in a non-actionable way (venting, not filing a bug).
- The natural human response would be a short reply, not a deliverable.

When uncertain, **default to conversation**. It is cheaper to under-execute than to over-produce a report when someone wanted a chat.

## Correction Rule

If the user's surface request and likely purpose differ, follow the likely purpose only when it is strongly supported by context.

If uncertain, preserve the surface request and mark the inferred purpose as uncertain.

Never treat an observed defect as automatically equivalent to the user's desired change.

## Execution Rule

After calibration, execute according to the calibrated task state and the routed skill.

Preserve user constraints, invariants, references, locked behaviors, and requested output style.
