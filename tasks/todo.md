# Time Series Tutor — RAG Enrichment & Pipeline Fixes

## Goal
Fix "Insufficient information" responses by repairing pipeline bugs and expanding corpus coverage. Target: avg_recall@5 from ~0.20 → ≥0.65.

## Tasks

- [x] Phase 0: Update model to gemini-3.1-flash-lite-preview
- [ ] Phase 1: Fix pipeline bugs
  - [ ] Remove context truncation (app.py:40, :86) — 500 chars → full content
  - [ ] Update system prompt (config.py:64-73) — expand to full time series scope
  - [ ] Tune retrieval: TOP_K=7, USE_RERANKER=True, MAX_TOKENS=1500
- [ ] Phase 2: Increase chunk size (CHUNK_SIZE=1200, CHUNK_OVERLAP=200) + re-ingest
- [ ] Phase 3a: Create Priority 1 markdown reference files
  - [ ] markov_regime_switching_models.md
  - [ ] nowcasting_mixed_frequency_methods.md
  - [ ] structural_break_governance_monitoring.md
  - [ ] break_adjusted_evaluation_metrics.md
- [ ] Phase 3b: Create Priority 2 markdown reference files + re-ingest
  - [ ] classical_time_series_methods.md
  - [ ] cointegration_error_correction_models.md
  - [ ] garch_volatility_models.md
  - [ ] kalman_filter_state_space_models.md
  - [ ] spectral_analysis_frequency_domain.md
- [ ] Phase 4: Extend eval/queries.yaml + run python eval_basic.py — verify ≥0.65
- [ ] Create PR

## Results
(to be filled after evaluation)
