# Break-Adjusted Evaluation Metrics for Forecasting

## Overview

Standard forecast evaluation metrics — RMSE, MAE, MAPE — assume a stable data-generating process over the evaluation window. When structural breaks occur, these metrics conflate two distinct sources of error: the model's inherent forecasting skill and its failure to adapt to a regime change. Break-adjusted evaluation isolates these components, enabling fairer comparison of models and more informative model selection.

**Key Reference:** Rossi, B. (2013). "Advances in forecasting under instability." In Elliott, G. and Timmermann, A. (eds.), *Handbook of Economic Forecasting*, Vol. 2, Part B. North-Holland.

## Why Standard RMSE Fails Under Breaks

Consider a forecasting model estimated on data from Regime 1. A break occurs at time $\tau$, shifting the data-generating process to Regime 2. Forecasts made after $\tau$ will be systematically biased until the model adapts (via retraining or rolling estimation).

The conventional RMSE over the full evaluation window $[1, T]$ mixes:
- Pre-break performance (may be excellent)
- Post-break performance (typically poor due to structural mismatch)

This produces a misleading average that obscures the break's true impact. A model that detects and adapts to breaks quickly may have higher pre-break RMSE (due to added flexibility) but far lower post-break RMSE — and be the superior choice operationally.

## Regime-Conditional RMSE

Regime-conditional RMSE separates performance by regime:

$$\text{RMSE}_j = \sqrt{\frac{1}{|T_j|} \sum_{t \in T_j} (y_t - \hat{y}_t)^2}$$

where $T_j$ is the set of time periods identified as belonging to regime $j$. Reporting $\text{RMSE}_1$ and $\text{RMSE}_2$ separately reveals whether a model's overall RMSE is driven by poor performance in one specific regime.

This requires regime labels — typically from a Markov-switching model's smoothed probabilities or from a structural break test's identified break dates.

## Rolling Window Evaluation

Rolling window evaluation naturally handles breaks by using a fixed-length estimation window that moves through time:

$$\text{RMSE}_{\text{roll}}(t) = \sqrt{\frac{1}{h} \sum_{s=t}^{t+h-1} (y_s - \hat{y}_{s|s-1})^2}$$

where $\hat{y}_{s|s-1}$ is the one-step-ahead forecast from a model re-estimated through period $s-1$ using a rolling window of length $w$.

**Rolling vs. expanding window trade-off:**
- **Rolling window:** Adapts to breaks by forgetting old data; but discards useful pre-break information and increases parameter estimation variance.
- **Expanding window:** Uses all available data; slower to adapt to breaks but lower estimation variance in stable periods.

**Giacomini-White test** (2006) formally tests whether the relative performance of two forecasting models is stable over time using rolling windows. A rejection suggests that one model is superior in certain sub-periods — potentially corresponding to different regimes.

**Reference:** Giacomini, R. and White, H. (2006). "Tests of conditional predictive ability." *Econometrica*, 74(6), 1545–1578.

## Break-Adjusted Diebold-Mariano Test

The standard Diebold-Mariano (DM) test compares the predictive accuracy of two forecasting models by testing whether their mean squared error difference is zero:

$$d_t = e_{1,t}^2 - e_{2,t}^2$$
$$\text{DM} = \frac{\bar{d}}{\sqrt{\hat{V}(\bar{d}) / T}} \sim N(0,1)$$

However, the DM test assumes covariance stationarity of the loss differential series $d_t$. A structural break in the loss differentials — e.g., if one model adapts quickly to a regime change and the other does not — violates this assumption and invalidates inference.

**Break-robust DM testing:** Giacomini and Rossi (2010) propose the **Fluctuation Test**, which evaluates the DM statistic over rolling sub-windows to detect time-variation in relative forecast accuracy:

$$\text{FT}(\tau) = \frac{1}{\sqrt{m}} \sum_{t=\tau-m+1}^{\tau} d_t / \hat{\sigma}$$

Rejection at any window indicates that relative performance is unstable — consistent with structural breaks affecting one model more than the other.

**Reference:** Giacomini, R. and Rossi, B. (2010). "Forecast comparisons in unstable environments." *Journal of Applied Econometrics*, 25(4), 595–620.

## Coverage Rates of Prediction Intervals Under Breaks

Prediction intervals are calibrated under an assumed data-generating process. After a structural break, the interval width may be too narrow (failing to account for the new level of uncertainty) or too wide (if the break reduced volatility). Empirical coverage rate measures whether nominal $(1-\alpha)$% intervals actually contain the true value at the claimed rate:

$$\text{Coverage} = \frac{1}{T} \sum_{t=1}^T \mathbf{1}[y_t \in [\hat{L}_t, \hat{U}_t]]$$

In break-adjusted evaluation, coverage is computed separately for pre-break and post-break periods. Poor post-break coverage signals that interval construction does not adapt adequately to regime changes.

## Robustness Checks

A full break-adjusted evaluation suite includes:
1. **Full-sample RMSE** — baseline comparison
2. **Pre-break and post-break RMSE** — regime-conditional assessment
3. **Rolling RMSE plot** — visual identification of when a model deteriorates
4. **Fluctuation test** — formal test for time-varying relative accuracy
5. **Coverage rates by regime** — interval calibration check
6. **MASE (Mean Absolute Scaled Error)** — scale-invariant metric that uses random walk as benchmark; more stable than MAPE under level shifts

## Key References

- Rossi, B. (2013). "Advances in forecasting under instability." *Handbook of Economic Forecasting*, Vol. 2.
- Diebold, F.X. and Mariano, R.S. (1995). "Comparing predictive accuracy." *Journal of Business and Economic Statistics*, 13(3), 253–263.
- Giacomini, R. and White, H. (2006). "Tests of conditional predictive ability." *Econometrica*, 74(6), 1545–1578.
- Giacomini, R. and Rossi, B. (2010). "Forecast comparisons in unstable environments." *Journal of Applied Econometrics*, 25(4), 595–620.
- Hyndman, R.J. and Koehler, A.B. (2006). "Another look at measures of forecast accuracy." *International Journal of Forecasting*, 22(4), 679–688.
