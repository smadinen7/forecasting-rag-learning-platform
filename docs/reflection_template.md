# Reflection Template

Use this template after each iteration of the PLP to document changes, metric deltas, and next actions.

---

## Iteration Metadata
- **Date:** YYYY-MM-DD
- **Version:** vX.Y
- **Evaluator(s):** [Names]

---

## 1. What Changed?

Describe the changes made in this iteration (code, data, prompts, evaluation criteria, etc.).

**Examples:**
- Added 5 new source documents on regime-switching models.
- Increased `CHUNK_SIZE` from 600 to 800 tokens.
- Enabled `USE_RERANKER=True` with BM25 scoring.
- Updated `SYSTEM_PROMPT` to emphasize citation correctness.
- Switched `PROVIDER` from "openai" to "gemini".

**Your Notes:**
```
[Describe changes here]
```

---

## 2. Metric Deltas

Compare key metrics before and after the changes. Use results from `eval_basic.py` and `eval_judge_llm.py`.

| Metric                  | Before | After | Change (Δ) | Notes                          |
|-------------------------|--------|-------|------------|--------------------------------|
| **Avg Recall@5**        | 0.XX   | 0.YY  | +/-Z.ZZ    | [Interpretation]               |
| **Avg Groundedness**    | 0.XX   | 0.YY  | +/-Z.ZZ    | [Interpretation]               |
| **Helpful Rate (%)**    | XX%    | YY%   | +/-ZZ%     | [Interpretation]               |
| **LLM Judge: Grounded** | X.X/5  | Y.Y/5 | +/-Z.Z     | [Interpretation]               |
| **LLM Judge: Relevance**| X.X/5  | Y.Y/5 | +/-Z.Z     | [Interpretation]               |
| **LLM Judge: Complete** | X.X/5  | Y.Y/5 | +/-Z.Z     | [Interpretation]               |
| **LLM Judge: Citations**| X.X/5  | Y.Y/5 | +/-Z.Z     | [Interpretation]               |

**Your Notes:**
```
[Discuss unexpected results, hypothesis confirmation/rejection, etc.]
```

---

## 3. Qualitative Observations

What did you notice during user testing, manual review, or error analysis?

**Examples:**
- Citations [1], [2] now correctly map to source filenames in 90% of answers.
- Gemini responses are more concise than OpenAI but sometimes miss nuance.
- Reranker improved relevance for queries about "nowcasting" but degraded recall for "detection."
- Users found the Analytics card helpful but requested CSV export.

**Your Notes:**
```
[Describe observations here]
```

---

## 4. Next Actions

Based on metrics and observations, what are the top 3 next steps?

1. **Action 1:**  
   - **Why:** [Rationale]  
   - **How:** [Concrete steps]  
   - **Expected Impact:** [Metric improvement or feature gain]

2. **Action 2:**  
   - **Why:** [Rationale]  
   - **How:** [Concrete steps]  
   - **Expected Impact:** [Metric improvement or feature gain]

3. **Action 3:**  
   - **Why:** [Rationale]  
   - **How:** [Concrete steps]  
   - **Expected Impact:** [Metric improvement or feature gain]

**Your Notes:**
```
[Additional context, dependencies, or timeline]
```

---

## 5. Open Questions / Risks

What remains unclear or risky for the next iteration?

**Examples:**
- Unclear if chunking at 800 tokens will degrade embedding quality for short documents.
- Risk: Gemini API rate limits may impact user experience during peak usage.
- Open question: Should we add cross-encoder reranking (heavy dependency)?

**Your Notes:**
```
[List questions and risks here]
```

---

## 6. Lessons Learned

What did you learn about RAG system design, evaluation, or the domain?

**Your Notes:**
```
[Capture insights for future iterations or documentation]
```

---

**Assignment Alignment:**  
This template supports Step 6 (Reflection) and feeds into iterative improvement cycles.
