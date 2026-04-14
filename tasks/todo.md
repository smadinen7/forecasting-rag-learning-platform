# Time Series Tutor — RAG Pipeline & Corpus

## Vision
Single query surfaces model recommendation + Python code, eliminating hours of manual cross-referencing.
Target metric: Recall@5 ≥ 0.80 (currently at 0.88).

---

## Completed

- [x] Phase 0: Update Gemini model → `gemini-3.1-flash-lite-preview` (config.py)
- [x] Phase 1: Fix pipeline bugs
  - [x] Remove context truncation in app.py (lines ~40, ~86): `[:500]` → full content
  - [x] Expand system prompt scope (config.py) — covers all time series topics
  - [x] Tune retrieval: TOP_K=7, USE_RERANKER=True, MAX_TOKENS=1500, CHUNK_SIZE=1200, CHUNK_OVERLAP=200
- [x] Phase 2: Re-ingest with larger chunks → 795 chunks (was 653)
- [x] Phase 3a: Priority 1 markdown reference files (branch: `feat/code-samples-and-papers`)
  - [x] markov_regime_switching_models.md
  - [x] nowcasting_mixed_frequency_methods.md
  - [x] structural_break_governance_monitoring.md
  - [x] break_adjusted_evaluation_metrics.md
  - [x] classical_time_series_methods.md
  - [x] cointegration_error_correction_models.md
  - [x] garch_volatility_models.md
  - [x] kalman_filter_state_space_models.md
  - [x] spectral_analysis_frequency_domain.md
- [x] Phase 3b: New research paper summaries
  - [x] exponential_smoothing_ets_models.md (Hyndman 2008, Gardner 1985)
  - [x] vector_autoregression_var_models.md (Sims 1980, Lütkepohl 2005)
  - [x] transformer_forecasting_models.md (PatchTST, iTransformer, Informer)
  - [x] change_point_detection_algorithms.md (PELT, BOCPD, ruptures)
  - [x] forecast_combination_ensembles.md (Bates & Granger 1969, M4/M5)
- [x] Phase 3c: Code sample files
  - [x] code_arima_sarima.md (statsmodels, pmdarima)
  - [x] code_garch_models.md (arch library)
  - [x] code_structural_break_detection.md (ruptures, statsmodels CUSUM)
  - [x] code_markov_regime_switching.md (statsmodels)
  - [x] code_stl_prophet.md (statsmodels STL, prophet)
  - [x] code_model_selection_guide.md — decision tree + scenario recipes
- [x] Phase 3d: Bayesian & trend-break detection papers
  - [x] pesaran_pettenuzzo_timmermann_2006.md (absorbing HMM, hierarchical prior)
  - [x] chib_1998_bayesian_changepoints.md (forward-backward MCMC, Bayes factors)
  - [x] bayesian_structural_time_series_bsts.md (BSTS, spike-and-slab, CausalImpact)
  - [x] bayesian_var_tvp_var.md (Minnesota prior, TVP-VAR, Primiceri 2005)
  - [x] trend_break_detection_correction.md (Perron, Zivot-Andrews, Perron-Yabu, 6 correction methods)
- [x] Copilot code review bugs fixed (8 bugs across code_* files — see PR #1)
- [x] Recall@5: 0.20 → 0.88 (eval_basic.py)

---

## Pending

### High Priority
- [ ] Merge `feat/code-samples-and-papers` → `main` via PR
- [ ] Extend `eval/queries.yaml` with new queries covering:
  - Bayesian methods (BSTS, BVAR, Chib changepoints)
  - Code retrieval queries ("show Python code for GARCH")
  - Trend break correction queries
  - Confirm recall still ≥ 0.80 against expanded query set

### Medium Priority
- [ ] Add RAGAS evaluation (deferred — user said "keep RAGAS for later")
- [ ] Upgrade embeddings: `all-MiniLM-L6-v2` (384d) → `all-mpnet-base-v2` (768d)
  - Re-ingest required after upgrade
  - Expected recall improvement on semantic queries
- [ ] App UX: model recommendation flow, code syntax highlighting in Streamlit

### Lower Priority
- [ ] Add N-BEATS / TFT code samples (deep learning forecasting)
- [ ] Add VECM / cointegration code samples
- [ ] Add Bayesian structural break code samples (Chib MCMC, BSTS in Python)
- [ ] Consider RAGAS integration for answer quality scoring (not just retrieval recall)

---

### In Progress
- [ ] feat/conversational-chat — multi-turn chat UI + session history

---

## Current State
- **Branch:** `feat/conversational-chat`
- **Recall@5:** 0.88
- **Chunks:** 795
- **Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`
- **LLM:** `gemini-3.1-flash-lite-preview`
- **Index location:** `index/faiss_index/`
- **Chat:** Multi-turn `st.chat_input` UI; session history in `logs/sessions/`
