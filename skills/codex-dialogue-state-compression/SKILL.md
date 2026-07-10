---
name: codex-dialogue-state-compression
description: Compress a completed execution task's final user-facing response without losing outcome, verification, material risk, blockers, or required next action. Use only when Task = execution and COLLAB = DELIVERY; never use for DUET, conversation, or intermediate executor-facing output.
---

# Delivery Compression

Use this skill only for the final user-facing response after execution has reached a real stopping point.

## Preserve the task state

Keep every item that changes what the user can safely believe or do next:

- The direct answer or completed outcome.
- What materially changed, when work was performed.
- Verification or evidence proportionate to the task's risk.
- Material risks, unresolved uncertainty, blockers, or incomplete work.
- A required next action or decision, but only when one genuinely remains.

Do not force a follow-up question. A completed task may end cleanly. Ask a question only when the user's answer is needed to choose or continue the next meaningful action.

## Remove dead weight

Remove repetition of the request, generic acknowledgements, praise, narration of routine steps, file-by-file inventories, low-signal detail, and hidden reasoning. Keep concise decision rationale when it helps the user evaluate the result.

Lead with the outcome. Match detail and structure to the task rather than forcing a template. Make the final response self-contained: the user should not need earlier commentary to recover the result, verification, or caveats.

Compression means that every remaining sentence advances the delivered state; it does not mean stripping away evidence or closure.
