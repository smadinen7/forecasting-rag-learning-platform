# Forecast Combination and Ensemble Methods

## Overview

Forecast combination — averaging or weighting multiple individual forecasts — consistently outperforms the best individual model in empirical studies. This finding, robust across decades of forecast competitions, is one of the most reliable results in forecasting. Bates and Granger (1969) established the theoretical foundation; the M4 and M5 competitions (2018, 2020) confirmed it comprehensively for modern methods.

**Key Reference:** Bates, J.M. and Granger, C.W.J. (1969). "The combination of forecasts." *OR*, 20(4), 451–468.

## Why Combination Works

Individual models make different errors. If these errors are not perfectly correlated, a combination will have lower mean squared error than any individual model — even if one model is clearly superior on average.

**Formal result (Bates & Granger, 1969):** For two forecasts $f_{1t}$ and $f_{2t}$ with errors $e_{1t}$, $e_{2t}$ having variances $\sigma_1^2$, $\sigma_2^2$ and correlation $\rho$, the optimal combination weight on $f_{1t}$ is:

$$w^* = \frac{\sigma_2^2 - \rho \sigma_1 \sigma_2}{\sigma_1^2 + \sigma_2^2 - 2\rho \sigma_1 \sigma_2}$$

The MSE of the optimal combination is always $\leq \min(\sigma_1^2, \sigma_2^2)$. Even when $\rho = 1$ (perfect correlation), the optimal combination reduces to the better forecast. The gains are largest when $\rho$ is low — diverse models that fail in different situations benefit most from combination.

## Simple Averaging

Despite the theoretical appeal of optimal weighting, **simple (equal) averaging** of forecasts is robustly competitive:

$$\hat{y}_{t+h}^{\text{combo}} = \frac{1}{M} \sum_{m=1}^M \hat{y}_{t+h}^{(m)}$$

This "wisdom of crowds" approach works because:
1. Optimal weights estimated from historical data tend to over-fit; equal weights are more robust out-of-sample
2. Estimation error in weights often exceeds the gain from unequal weighting
3. Equal weights are trivially robust to model selection error

**Empirical evidence:** In the M4 competition (100,000 time series), the simple average of the top-5 statistical methods outperformed most individual methods, including sophisticated ML models.

## Optimal (Variance-Minimizing) Combination

Given $M$ forecasts with error covariance matrix $\Sigma$ (estimated from a holdout period), the optimal combination weights minimize portfolio variance:

$$\mathbf{w}^* = \frac{\Sigma^{-1} \mathbf{1}}{\mathbf{1}^\top \Sigma^{-1} \mathbf{1}}$$

This is analogous to the minimum-variance portfolio in finance. In practice, $\Sigma$ must be estimated and may be ill-conditioned when $M$ is large. Shrinkage estimators (ridge regression, LASSO) or diagonal approximations stabilize the estimate.

**Shrinkage to equal weights:** A practical approach shrinks optimal weights toward equal weights as sample size decreases:
$$\mathbf{w}(\lambda) = (1-\lambda)\mathbf{w}^* + \lambda \frac{1}{M}\mathbf{1}$$

with $\lambda$ chosen by cross-validation. As $T \to \infty$, $\lambda \to 0$ (optimal weights); for small samples, $\lambda \to 1$ (equal weights).

## Stacking (Model Averaging via Regression)

**Stacking** (Wolpert, 1992) uses a meta-learner to combine forecasts:
1. Split data into training and validation sets
2. Train $M$ base models on the training set; generate their forecasts on the validation set
3. Train a meta-model (regression of actuals on base model forecasts) on the validation set
4. At test time, average base model forecasts using meta-model weights

The meta-model can be a simple OLS regression (equivalent to optimal combination), ridge regression (for stability), or a non-negative least squares regression (to constrain weights to be positive).

**Cross-validation stacking:** Use $K$-fold cross-validation on the training set to generate out-of-sample "stacking features" from base models, then train the meta-learner on these. This avoids information leakage.

## Bayesian Model Averaging (BMA)

BMA combines forecasts weighted by the posterior probability that each model generated the data:

$$\hat{y}_{t+h} = \sum_{m=1}^M P(M_m | \mathbf{y}) \cdot \hat{y}_{t+h}^{(m)}$$

where $P(M_m | \mathbf{y}) \propto P(\mathbf{y} | M_m) P(M_m)$. BMA is theoretically optimal under a flat prior over the model space. In practice, it requires computing the marginal likelihood $P(\mathbf{y} | M_m)$ — feasible analytically for linear Gaussian models, difficult otherwise.

**Approximation:** BIC-based model averaging approximates BMA using $P(M_m | \mathbf{y}) \propto \exp(-\text{BIC}_m / 2)$.

## M4 and M5 Competition Lessons

**M4 Competition (2018):** 100,000 time series across 6 frequencies (hourly to annual). Key findings:
- Hybrid methods (statistical + ML) won: the champion ES-RNN combined exponential smoothing with a recurrent neural network
- Simple combination of top statistical methods was highly competitive
- Pure ML models without statistical components underperformed
- **No single model dominated across all series types**

**M5 Competition (2020):** 42,840 hierarchical daily sales series (Walmart). Key findings:
- LightGBM dominated point forecasting (gradient boosted trees with lag features)
- Reconciliation of hierarchical forecasts (bottom-up, MinT) improved accuracy
- Probabilistic forecasting was harder: combining quantile regression with gradient boosting worked best
- Feature engineering (lags, rolling means, calendar features) mattered more than model architecture

**Reference:** Makridakis, S., Spiliotis, E., and Assimakopoulos, V. (2020). "The M4 Competition: 100,000 time series and 61 forecasting methods." *International Journal of Forecasting*, 36(1), 54–74.

## Practical Combination Strategy

For a production forecasting system:
1. Build 3–5 diverse base models (e.g., ARIMA, ETS, Prophet, LightGBM with lag features)
2. Evaluate each on a rolling out-of-sample validation set; record errors
3. Start with equal averaging as baseline
4. Optionally: estimate optimal weights via ridge regression on validation errors
5. Monitor relative performance over time; if one model consistently underperforms, downweight it

**Diversity matters:** Include models that fail in different ways — a statistical model (ARIMA/ETS) that assumes linearity, a tree-based model that captures non-linearities, and a pattern-matching model (Prophet). Their errors will be less correlated than three similar models.

## Key References

- Bates, J.M. and Granger, C.W.J. (1969). "The combination of forecasts." *OR*, 20(4), 451–468.
- Timmermann, A. (2006). "Forecast combinations." In Elliott, G., Granger, C., and Timmermann, A. (eds.), *Handbook of Economic Forecasting*, Vol. 1.
- Wolpert, D.H. (1992). "Stacked generalization." *Neural Networks*, 5(2), 241–259.
- Makridakis, S., Spiliotis, E., and Assimakopoulos, V. (2020). *International Journal of Forecasting*, 36(1), 54–74.
- Stock, J.H. and Watson, M.W. (2004). "Combination forecasts of output growth in a seven-country data set." *Journal of Forecasting*, 23(6), 405–430.
