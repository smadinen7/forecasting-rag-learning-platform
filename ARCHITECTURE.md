# Personal Learning Portal - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PERSONAL LEARNING PORTAL (PLP)                     │
│                Corporate Forecasting & Structural Breaks                │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 1. INGESTION PIPELINE (ingest.py)                                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  data/                                                                   │
│  ├── structural_breaks.md         ──┐                                   │
│  ├── forecasting_overlays.md        │                                   │
│  ├── evaluation_governance.md       ├──> Load & Parse                   │
│  ├── *.txt, *.pdf (<30MB)         ──┘                                   │
│                                      │                                   │
│                                      ▼                                   │
│                      RecursiveCharacterTextSplitter                      │
│                      (chunk_size=600, overlap=80)                        │
│                                      │                                   │
│                                      ▼                                   │
│                      HuggingFaceEmbeddings                               │
│                      (all-MiniLM-L6-v2)                                  │
│                                      │                                   │
│                                      ▼                                   │
│                      FAISS Index (CPU)                                   │
│                      index/faiss_index/                                  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 2. STREAMLIT APP (app.py)                                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐                  ┌────────────────────────────┐    │
│  │   SIDEBAR       │                  │   MAIN PANEL               │    │
│  ├─────────────────┤                  ├────────────────────────────┤    │
│  │ ☐ Mechanisms    │                  │  Query Input Box           │    │
│  │ ☐ Detection     │                  │  ├─> "What are breaks?"    │    │
│  │ ☐ Overlays      │                  │                            │    │
│  │ ☐ Nowcasting    │                  │  🔍 Search Button          │    │
│  │ ☐ Evaluation    │                  │                            │    │
│  │ ☐ Reflection    │                  │         ▼                  │    │
│  │                 │                  │  RETRIEVAL PIPELINE        │    │
│  │ Progress: 67%   │                  │  ├─> FAISS.search(k=20)    │    │
│  │ ▓▓▓▓▓▓▓░░░░░░   │                  │  ├─> rerank() [optional]   │    │
│  │                 │                  │  └─> Top-5 docs            │    │
│  │ Path: QuickStart│                  │                            │    │
│  │ ├─ Mechanisms ✓ │                  │         ▼                  │    │
│  │ └─ Detection ☐  │                  │  ANSWER GENERATION         │    │
│  │                 │                  │  ┌──────────────────────┐  │    │
│  │ Provider: Gemini│                  │  │ if PROVIDER=gemini:  │  │    │
│  │ Reranker: OFF   │                  │  │   gemini-1.5-pro     │  │    │
│  │ Top-K: 5        │                  │  │ elif PROVIDER=openai:│  │    │
│  └─────────────────┘                  │  │   gpt-4o-mini        │  │    │
│                                       │  │ else:                │  │    │
│  ┌─────────────────────────────────┐  │  │   extractive bullets │  │    │
│  │  📈 WEEKLY ANALYTICS             │  │  └──────────────────────┘  │    │
│  ├─────────────────────────────────┤  │                            │    │
│  │ Helpful Rate:      78%          │  │         ▼                  │    │
│  │ Avg Novelty:       1.4/2        │  │  📝 Answer with [1][2]...  │    │
│  │ Avg Confidence:    1.6/2        │  │  📚 Citations [1-5]        │    │
│  │ Total Queries:     23           │  │                            │    │
│  │                                 │  │         ▼                  │    │
│  │ 💡 Next Action:                 │  │  📊 MICRO-SURVEY           │    │
│  │ "Performance stable; expand     │  │  ├─ Helpful? Y/N          │    │
│  │  corpus with case studies"      │  │  ├─ Novelty: 0-2          │    │
│  │                                 │  │  └─ Confidence: 0-2        │    │
│  └─────────────────────────────────┘  │         │                  │    │
│                                       │         ▼                  │    │
│                                       │  logs/run_YYYYMMDD.jsonl   │    │
│                                       └────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 3. EVALUATION PIPELINE                                                   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  eval/queries.yaml (5 sample queries)                                   │
│       │                                                                  │
│       ├────────────────────┬─────────────────────────────────────┐      │
│       ▼                    ▼                                     ▼      │
│  eval_basic.py        eval_judge_llm.py               (Future: RAGAs)   │
│                                                                          │
│  ┌─────────────────┐   ┌──────────────────────────┐                     │
│  │ BASIC METRICS   │   │ LLM-AS-JUDGE             │                     │
│  ├─────────────────┤   ├──────────────────────────┤                     │
│  │ • Recall@5      │   │ For each query:          │                     │
│  │   (keyword      │   │   1. Generate answer     │                     │
│  │    matching)    │   │   2. Prompt Gemini/OAI   │                     │
│  │                 │   │   3. Score (0-5):        │                     │
│  │ • Avg Relevance │   │      - Groundedness      │                     │
│  │   (cosine sim)  │   │      - Relevance         │                     │
│  │                 │   │      - Completeness      │                     │
│  │ • Per-query +   │   │      - Citation correct  │                     │
│  │   aggregate     │   │   4. Extract rationales  │                     │
│  │                 │   │                          │                     │
│  │ Output:         │   │ Output:                  │                     │
│  │ basic_eval.json │   │ llm_judge_eval.json      │                     │
│  └─────────────────┘   │ llm_judge_eval.jsonl     │                     │
│                        └──────────────────────────┘                     │
│                                                                          │
│  Graceful Fallback: If no API keys → skip LLM judge with notice         │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 4. CONFIGURATION (config.py)                                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CHUNKING                    RETRIEVAL                  PROVIDERS       │
│  ├─ chunk_size: 600          ├─ k_candidates: 20       ├─ Gemini       │
│  └─ overlap: 80              ├─ top_k: 5               ├─ OpenAI       │
│                              └─ use_reranker: False    └─ Extractive   │
│  MODULES                     PATHS                                      │
│  ├─ Mechanisms               ├─ QuickStart             PROMPTS          │
│  ├─ Detection                ├─ QuantDeepDive          ├─ SYSTEM_PROMPT │
│  ├─ Overlays                 └─ OpsPlaybooks           └─ JUDGE_PROMPT  │
│  ├─ Nowcasting                                                          │
│  ├─ Evaluation                                                          │
│  └─ Reflection                                                          │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 5. DATA FLOW                                                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  User Query                                                              │
│      │                                                                   │
│      ├──> FAISS.similarity_search(query, k=20)                           │
│      │        └──> [Doc1, Doc2, ..., Doc20] with metadata               │
│      │                                                                   │
│      ├──> rerank(query, docs) [if USE_RERANKER=True]                     │
│      │        └──> [Doc3, Doc1, Doc7, ...] reordered by relevance       │
│      │                                                                   │
│      ├──> Top-5 docs                                                     │
│      │                                                                   │
│      ├──> generate_answer(query, top_5)                                  │
│      │    ├──> Try Gemini (if key + provider=gemini)                     │
│      │    ├──> Fallback OpenAI (if key)                                  │
│      │    └──> Fallback extractive (always works)                        │
│      │                                                                   │
│      └──> Display: Answer + Citations [1-5] + Survey                     │
│                │                                                         │
│                └──> log_interaction(query, answer, survey_data)          │
│                         └──> logs/run_YYYYMMDD.jsonl                     │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 6. TESTING & VALIDATION                                                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  tests/                                                                  │
│  ├── test_ingest.py          ──> Validates FAISS index builds & loads   │
│  ├── test_retrieval.py       ──> Tests similarity search & reranking    │
│  └── test_eval.py            ──> Checks eval results structure          │
│                                                                          │
│  Run: make test (pytest)                                                 │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 7. DOCUMENTATION                                                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  docs/                                                                   │
│  ├── learning_questions.md      ──> 7 questions (Step 1)                │
│  ├── objectives.md              ──> 5 Bloom objectives (Step 2a)        │
│  ├── features_inspired.md       ──> Platform adaptations (Step 2b)      │
│  ├── sources_template.csv       ──> Corpus documentation                │
│  └── reflection_template.md     ──> Iteration tracking (Step 6)         │
│                                                                          │
│  README.md                       ──> Comprehensive guide                 │
│  QUICKSTART.md                   ──> Fast reference                      │
│  BUILD_SUMMARY.md                ──> Project status                      │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 8. ASSIGNMENT MAPPING                                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Step 1: Learning Questions       ✅ docs/learning_questions.md          │
│  Step 2a: Objectives              ✅ docs/objectives.md (5 Bloom levels) │
│  Step 2b: Platform Features       ✅ docs/features_inspired.md           │
│  Step 3: Deep Search Corpus       ✅ data/ (3 docs + extensible)         │
│  Step 4: RAG with Citations       ✅ app.py (Gemini/OpenAI/extractive)   │
│  Step 5a: Basic Eval              ✅ eval_basic.py                        │
│  Step 5b: LLM Judge               ✅ eval_judge_llm.py                    │
│  Step 6: Reflection               ✅ docs/reflection_template.md          │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

LEGEND:
  ──> Data flow
  │   Sequential step
  ├─  Branch/option
  ✅  Complete
  ☐   Incomplete (user action)
  ▓   Progress bar filled
  ░   Progress bar empty
```
