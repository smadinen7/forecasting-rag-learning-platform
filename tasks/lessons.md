# Lessons Learned

## 2026-04-08 — Model Selection
When the user specifies a model name, use it exactly as stated. Don't substitute with a "better" or "more stable" model on their behalf without asking. The user has reasons (cost, speed, testing comparison) for their choice.

**Rule:** User-specified model names are requirements, not suggestions. Change only when explicitly asked.

## 2026-04-08 — Plan Mode Exit
Do not use ExitPlanMode unless the user has approved the plan. If the user rejects or modifies the plan mid-exit, incorporate their changes first, then re-exit.
