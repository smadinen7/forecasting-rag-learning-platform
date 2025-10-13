---
title: "Forecasting Under Breaks: Regime Overlays and Adaptive Methods"
source: "Internal Training Materials - Quantitative Strategies"
type: "Methodology"
relevance: "Advanced Techniques"
---

# Forecasting Under Breaks: Regime Overlays and Adaptive Methods

## The Challenge

Traditional forecasting models (ARIMA, VAR, linear regression) assume parameter stability. When structural breaks occur, these models fail catastrophically. **Overlay mechanisms** are techniques that allow forecasts to remain robust under regime uncertainty by adapting to detected or suspected breaks.

## Taxonomy of Overlay Methods

### 1. Regime-Switching Models

**Markov-Switching Models** (Hamilton, 1989) assume the economy alternates between discrete regimes (e.g., "expansion" vs. "recession") governed by a hidden Markov process.

- **Strengths**: Captures regime persistence; endogenous regime probabilities.
- **Weaknesses**: Computationally intensive; requires regime interpretation.
- **Use Case**: Modeling business cycle dynamics in GDP forecasting.

**Threshold Autoregressive (TAR) Models** switch regimes based on observable thresholds (e.g., if unemployment > 7%, switch to regime 2).

- **Strengths**: Interpretable; links regimes to observable triggers.
- **Weaknesses**: Requires domain knowledge to set thresholds.
- **Use Case**: Interest rate forecasting conditioned on inflation thresholds.

### 2. Ensemble Methods

**Forecast Combination** averages predictions from multiple models (e.g., pre-break model + post-break model + regime-switching model).

- **Strengths**: Reduces sensitivity to single-model failures; simple to implement.
- **Weaknesses**: May dilute strong signals; equal weighting is naive.
- **Use Case**: Combining short-term and long-term forecasts with different break sensitivities.

**Bayesian Model Averaging (BMA)** weights models by posterior probabilities given data.

- **Strengths**: Principled uncertainty quantification; adapts weights as evidence accumulates.
- **Weaknesses**: Computationally expensive; requires prior specification.
- **Use Case**: Meta-forecasting across multiple competing break hypotheses.

### 3. Adaptive Filtering

**Exponentially Weighted Moving Average (EWMA)** down-weights older data, effectively "forgetting" pre-break patterns.

- **Strengths**: Simple; online updates; works with any base model.
- **Weaknesses**: Arbitrary decay rate; no explicit break detection.
- **Use Case**: Real-time volatility forecasting (e.g., RiskMetrics).

**Kalman Filters** with time-varying parameters allow coefficients to drift gradually.

- **Strengths**: Optimal under Gaussian assumptions; handles gradual breaks.
- **Weaknesses**: Assumes smooth parameter evolution; misses abrupt breaks.
- **Use Case**: Tracking evolving beta coefficients in factor models.

**Particle Filters** (Sequential Monte Carlo) handle nonlinear/non-Gaussian state-space models.

- **Strengths**: Flexible; captures complex regime dynamics.
- **Weaknesses**: High computational cost; tuning required.
- **Use Case**: Nowcasting with heterogeneous data sources.

### 4. Hybrid Approaches

Combine break detection with overlay mechanisms:
1. **Detect** break using CUSUM or Bai-Perron.
2. **Re-estimate** model on post-break data only.
3. **Overlay** regime-switching model for ambiguous periods.

**Example Pipeline:**
- If break detected at $t=\tau$: truncate training data to $t \geq \tau$.
- If no break: use full history with BMA over candidate models.
- If uncertain: run regime-switching model with 2 states.

## Practical Considerations

### Model Selection
- **High-frequency data** (daily, intraday): Prefer adaptive filters (EWMA, Kalman).
- **Low-frequency data** (monthly, quarterly): Prefer regime-switching or ensemble methods.
- **Known break dates** (e.g., policy change): Use piecewise models.
- **Unknown breaks**: Use online detection + adaptive overlays.

### Computational Costs
- **Fast:** EWMA, TAR, forecast combination.
- **Moderate:** Kalman filters, 2-state Markov-switching.
- **Slow:** Particle filters, BMA with many models.

### Interpretability
- **High:** TAR (threshold-based), piecewise regression.
- **Moderate:** Markov-switching (requires regime labeling).
- **Low:** Particle filters, deep ensemble methods.

## Case Study: Nowcasting GDP During COVID-19

**Problem:** 2020 pandemic caused unprecedented structural break in GDP dynamics.

**Solution:**
1. **Detection:** CUSUM flagged break in March 2020.
2. **Overlay:** 
   - Short-term (1-2 months): EWMA on high-frequency indicators (unemployment claims, mobility data).
   - Medium-term (3-6 months): 2-state Markov-switching (pre-COVID vs. COVID regimes).
   - Long-term (12+ months): BMA over multiple recovery scenarios.
3. **Result:** Ensemble reduced MAE by 40% vs. pre-COVID ARIMA baseline.

## Key Takeaways

- No single overlay method dominates all scenarios.
- Combine detection (reactive) with regime modeling (proactive).
- Balance accuracy, speed, and interpretability based on use case.
- Continuously monitor and update as new data arrives.

---

**References:**
- Hamilton, J. D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series." *Econometrica*.
- Stock, J. H., & Watson, M. W. (2004). "Combination Forecasts of Output Growth in a Seven-Country Data Set." *Journal of Forecasting*.
- Giannone, D., Reichlin, L., & Small, D. (2008). "Nowcasting: The Real-Time Informational Content of Macroeconomic Data." *Journal of Monetary Economics*.
