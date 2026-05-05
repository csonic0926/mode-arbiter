---
name: codex-continuation-phase-gate
description: Phase gate for Codex intermediate executor-facing outputs. Triggers only inside unresolved Codex task loops, never for final user-facing answers.
---

## Trigger Timing

Trigger only during an unresolved Codex execution loop when the current output is executor-facing: a mid-task handoff, state marker, or continuation cue meant to let Codex keep working.

Do not trigger for any user-facing final response, completion summary, clarification request, or stop-point report.

If the phase is ambiguous, treat it as final-user-facing and do not trigger.

## Output Rule

When triggered, keep output staged and status-labeled:

Found = observed facts only.  
Inferred = best-effort user purpose, with uncertainty marked when needed.  
Proposed = direction justified by Found + Inferred.

Never merge findings with rewrite/fix direction.

For inspect-then-rewrite tasks, output Found before Inferred or Proposed. Do not advance to Proposed unless the current phase explicitly requires direction.

Preserve user constraints, invariants, references, and locked behaviors.