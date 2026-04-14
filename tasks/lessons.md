# Lessons Learned

## Model Selection
**Rule:** User-specified model names are requirements, not suggestions. Use exactly as stated — do not substitute with a "better" or "more stable" model without asking. User has reasons (cost, speed, comparison testing) for their choice.

**Why:** Was corrected multiple times in this project (1.5-pro → 2.0-flash → 3.1-pro → 3.1-flash-lite-preview). Each substitution was wrong.

**How to apply:** When config.py or any file specifies a model ID, change it only to exactly what the user says.

---

## Plan Mode Exit
**Rule:** Do not call ExitPlanMode unless the user has explicitly approved the plan. If the user rejects or modifies the plan mid-exit, incorporate their changes first, then re-exit.

**Why:** User rejected an ExitPlanMode call mid-session when changes hadn't been reviewed.

**How to apply:** Wait for a clear "yes" / "looks good" / "proceed" before exiting plan mode.

---

## Branching Before Implementation
**Rule:** For any multi-file feature work, create a new branch first. Never implement directly on main.

**Why:** User explicitly said "Let's do it on another branch" twice when work was about to start on main.

**How to apply:** Before writing any new files for a feature, check current branch. If on main, create a feature branch first.

---

## Test Before Commit
**Rule:** Always run the app and/or eval before staging a commit. Never commit untested changes.

**Why:** User rejected a git add tool call twice with "Let's first test what we've built."

**How to apply:** After writing code or content files, run `python ingest.py && python eval_basic.py` (or `streamlit run app.py` for manual test) before committing.

---

## Context Truncation Is a Silent Killer
**Rule:** Never truncate retrieved document content before passing to the LLM. Pass full `doc.page_content`.

**Why:** `app.py` had `content = doc.page_content[:500]` — chunks are 1200 chars, so the LLM never saw >40% of each chunk. This was the root cause of "Insufficient information" responses. Fixing this alone doubled retrieval usefulness.

**How to apply:** When writing RAG pipelines, grep for `[:N]` on page_content. If found, remove the truncation.

---

## System Prompt Scope Must Match Corpus Scope
**Rule:** The system prompt must explicitly name ALL topic areas the corpus covers. A narrowly scoped prompt causes the LLM to refuse queries on topics the corpus actually has good coverage for.

**Why:** Original prompt said "corporate forecasting and structural breaks in finance" — queries about ARIMA, GARCH, cointegration all returned "Insufficient information" even though corpus had relevant chunks.

**How to apply:** After adding new data files, review the system prompt and add any newly covered topics.

---

## Code Review: Validate API Calls Against Actual Library Docs
**Rule:** Before finalizing any code in reference/tutorial files, verify the API calls against the actual library. Do not assume function signatures from memory.

**Why:** Copilot PR review caught 8 real bugs: wrong `k` in Chow test, invalid `statsmodels.tsa.breakpoint_test` import, wrong `ruptures` cost API, double-squaring in ARCH test, `auto_arima` misidentified as ETS, unused SARIMAX import, index misalignment in ensemble.

**How to apply:** For each library used in code samples, verify: (1) import path exists, (2) function signature is correct, (3) return values are used correctly.

---

## Merge Conflicts: Pull Before Push
**Rule:** Before pushing a branch that has remote changes (e.g., from Copilot auto-fixes), always `git pull --rebase` first.

**Why:** Copilot had pushed a fix to `feat/code-samples-and-papers` remotely. Direct push failed. Had to stash, pull, resolve conflict, then push.

**How to apply:** If push is rejected, check `git status` and `git log --oneline origin/branch..HEAD` before force-pushing or rebasing.

---

## Conversational RAG: Retrieval Query Must Include Prior Topic
**Rule:** In a multi-turn chat RAG system, when the user asks a vague follow-up ("show me code for that", "can you elaborate on it"), the FAISS retrieval must also receive an expanded query that includes the prior topic — not just the literal follow-up string.

**Why:** "Show me Python code for that" returned structural break and Markov-switching docs instead of GARCH docs, because FAISS had no context that "that" = GARCH. The LLM prompt had the right prior context but retrieved the wrong chunks.

**How to apply:** Add a `build_retrieval_query(current_query, messages)` helper that detects vague queries (short length or pronoun-heavy) and prepends the last user message topic before calling `similarity_search`.

---

## Gitignore: Check Before Staging Eval Results
**Rule:** `eval/results/` is in `.gitignore`. Do not try to `git add eval/results/*.json`.

**Why:** Got an error staging `eval/results/basic_eval.json`. The results directory is intentionally excluded.

**How to apply:** Only commit eval query definitions (`eval/queries.yaml`), not result files.
