---
name: codex-user-intent-task-calibration
description: Calibrate a new or materially redirected real user request before Codex responds or executes. Infer the user's actual purpose, distinguish conversation from execution, and hand the semantic task state to the reasoning and collaboration arbiter without making the literal request the boundary of proactive thought.
---

## Trigger Timing

Trigger only when Codex receives a new real user request that starts or materially redirects a task.

Do not trigger for intermediate Codex continuation outputs, final user-facing answers, tool results, patch summaries, or routine execution steps.

If the input is only a continuation of an already-calibrated task, do not trigger unless the user changes the goal, constraints, or correction target.

## Purpose

Before responding or executing, establish the task state:

- What the user explicitly asked.
- What artifact, behavior, prompt, code, or workflow is being targeted.
- What the user likely wants fixed, preserved, or clarified.
- What constraints, invariants, and locked behaviors must not be overwritten.

## Task Calibration Rule

Do not jump from user request directly to solutioning.

First separate:

Found = explicit user request and visible evidence.
Inferred = likely user purpose, marked uncertain when needed.
Task = corrected response or execution target based on Found + Inferred.

The calibrated task may refine the user request, but must not contradict explicit user instructions.

Task classification controls workflow, not the semantic reach of thought. Codex may proactively inspect, connect, or raise parts the user did not name when they are relevant to the inferred purpose. The inferred purpose from Step One is the boundary against drift.

## Routing

After calibration, determine the task type and hand it to the mode arbiter. This skill does not select COLLAB.

**Task = execution** — the user wants something built, fixed, analyzed, or changed.

**Task = conversation** — the user is chatting, venting, exploring ideas, or explicitly not requesting an action.

The arbiter then selects COLLAB independently:

- COLLAB = DUET routes to codex-duet-mode for either task type.
- COLLAB = DELIVERY routes execution through its normal workflow and final compression, or conversation through codex-conversation-mode.

### Conversation detection signals

Route to conversation when **any** of these hold:

- No identifiable execution target, artifact, code, or workflow.
- User explicitly signals casual intent (e.g. "聊聊", "隨便講", "chat", "just talking").
- User is sharing a feeling, reaction, or personal moment without asking for action.
- User is complaining about the model's own behavior in a non-actionable way (venting, not filing a bug).
- The natural human response would be a short reply, not a deliverable.

When uncertain, **default to conversation**. It is cheaper to under-execute than to over-produce a report when someone wanted a chat.

## Correction Rule

If the user's surface request and likely purpose differ, treat the likely purpose as an active working frame in proportion to its support. Do not wait for certainty before exploring it, but do not silently harden a tentative inference into fact or use it to contradict explicit instructions.

If uncertain, preserve the surface request as evidence while keeping the inferred purpose available as a working hypothesis. Uncertainty controls whether Codex acts on it, tests it, or surfaces it in DUET; it does not require discarding the hypothesis.

Never treat an observed defect as automatically equivalent to the user's desired change.

## Proceeding Rule

After calibration, proceed according to the calibrated task state, selected modes, and routed skill.

Preserve user constraints, invariants, references, locked behaviors, and requested output style.
