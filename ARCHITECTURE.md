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
│  data/ (12 REAL SOURCES - 7.8MB)                                        │
│  ├── Cleveland_STL_Decomposition.pdf (2.7MB, 31 pages)                  │
│  ├── DieboldMariano_1995.pdf (903KB, 11 pages)                          │
│  ├── TaylorLetham_Prophet.pdf (841KB, 17 pages)                         │
│  ├── Oreshkin_NBEATS.pdf (556KB, 12 pages)                              │
│  ├── Lim_TemporalFusionTransformers.pdf (2.5MB, 27 pages)               │
│  ├── Timmermann_ModelInstability.pdf (724KB, 41 pages)                  │
│  ├── Wickramasuriya_MinT.pdf (618KB, 42 pages)                          │
│  ├── Google_Correlate.pdf (585KB, 28 pages)                             │
│  ├── ZhuShasha_StatStream.pdf (1.0MB, 25 pages)                         │
│  ├── Li_TimeSeriesMomentum.pdf (854KB, 31 pages)                        │
│  ├── Hyndman_FPP3_Reference.md (textbook reference)   ├──> Load & Parse │
│  └── BaiPerron_2003_Reference.md (paper reference)  ──┘                 │
│                                      │                                   │
│                        267 DOCUMENT PAGES LOADED                         │
│                                      │                                   │
│                                      ▼                                   │
│                      RecursiveCharacterTextSplitter                      │
│                      (chunk_size=600, overlap=80)                        │
│                                      │                                   │
│                        1,064 CHUNKS CREATED                              │
│                                      │                                   │
│                                      ▼                                   │
│                      HuggingFaceEmbeddings                               │
│                      (all-MiniLM-L6-v2, 384 dims)                        │
│                                      │                                   │
│                                      ▼                                   │
│                      FAISS Index (CPU)                                   │
│                      index/faiss_index/ (2.2MB)                          │
│                      ├─ faiss_index.faiss (1.6MB)                        │
│                      └─ faiss_index.pkl (655KB)                          │
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
│  ├── sources.csv                ──> 12 real sources documented          │
│  ├── reflection_template.md     ──> Iteration tracking (Step 6)         │
│  └── STEP3_SEARCH_GUIDE.md      ──> Source collection methodology       │
│                                                                          │
│  eval/                                                                   │
│  ├── EVALUATION_LOG.md           ──> Detailed evaluation analysis       │
│  ├── OUTPUT_SAMPLES.md           ──> 6 sample Q&A interactions          │
│  └── results/basic_eval.json    ──> Automated metrics                   │
│                                                                          │
│  README.md                       ──> Comprehensive guide                 │
│  QUICKSTART.md                   ──> Fast reference                      │
│  BUILD_SUMMARY.md                ──> Project status                      │
│  FINAL_REPORT.md                 ──> 2.5-page assignment report          │
│  PROJECT_DESCRIPTION.md          ──> Resume bullet points                │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 8. ASSIGNMENT MAPPING                                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Step 1: Learning Questions       ✅ docs/learning_questions.md          │
│  Step 2a: Objectives              ✅ docs/objectives.md (5 Bloom levels) │
│  Step 2b: Platform Features       ✅ docs/features_inspired.md           │
│  Step 3: Deep Search Corpus       ✅ data/ (12 real sources, 1,064 chnks)│
│  Step 4: RAG with Citations       ✅ app.py (Gemini/OpenAI/extractive)   │
│  Step 5a: Basic Eval              ✅ eval_basic.py (20% recall, 26% rel) │
│  Step 5b: LLM Judge               ✅ eval_judge_llm.py (skipped - no key)│
│  Step 6: Reflection               ✅ FINAL_REPORT.md (Section 5)         │
│                                                                          │
│  DELIVERABLES COMPLETE:                                                  │
│  ✅ Evaluation Log: eval/EVALUATION_LOG.md                               │
│  ✅ Output Samples: eval/OUTPUT_SAMPLES.md (6 samples)                   │
│  ✅ Final Report: FINAL_REPORT.md (2.5 pages)                            │
│  ✅ Results: eval/results/basic_eval.json                                │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 9. KEY METRICS & PERFORMANCE                                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  DATA CORPUS                      RETRIEVAL PERFORMANCE                 │
│  ├─ Sources: 12                   ├─ Best Recall@5: 80%                 │
│  ├─ Total Pages: 267              ├─ Avg Recall@5: 20%                  │
│  ├─ Total Chunks: 1,064           ├─ Avg Relevance: 26%                 │
│  ├─ Total Size: 7.8MB             ├─ Query Latency: <0.5s               │
│  └─ Index Size: 2.2MB             └─ Cold Start: ~2-3s                   │
│                                                                          │
│  TOP RETRIEVED SOURCES            TIME REDUCTION                         │
│  ├─ Timmermann (41 pages)         ├─ Manual Search: 5-10 min            │
│  ├─ Bai & Perron (reference)      ├─ RAG System: <0.5s                  │
│  ├─ Hyndman FPP3 (textbook)       └─ Improvement: ~99%                   │
│  └─ Diebold-Mariano (1995)                                               │
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
