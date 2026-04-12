# Bayesian VAR and Time-Varying Parameter Models

## Overview

Bayesian Vector Autoregression (BVAR) and Time-Varying Parameter VAR (TVP-VAR) are the workhorses of modern empirical macroeconomics. BVAR addresses the over-fitting problem of large VARs through prior shrinkage; TVP-VAR allows VAR coefficients to evolve continuously over time, capturing gradual structural change rather than abrupt breaks. Both approaches deliver superior forecasts compared to classical OLS VAR, particularly in small samples and unstable environments.

## Bayesian VAR (BVAR): The Minnesota Prior

### Motivation

A VAR(p) with $n$ variables has $n^2 p + n$ parameters. For $n=7$ variables and $p=4$ lags, this is 200 parameters. With only 200 quarterly observations, OLS estimation is unreliable — each equation has as many regressors as observations. The Bayesian approach regularizes estimation via a prior that embeds economic knowledge about likely parameter values.

### The Minnesota Prior (Litterman 1986)

Litterman (1986) proposed the **Minnesota prior** based on the observation that macroeconomic variables behave approximately as random walks. The prior centers coefficients as follows:

- **Own first lag:** $E[\phi_{ii,1}] = 1$ (each variable follows a random walk)
- **Own higher lags:** $E[\phi_{ii,k}] = 0$ for $k > 1$ (higher lags are zero)
- **Cross-variable lags:** $E[\phi_{ij,k}] = 0$ for $i \neq j$ (other variables don't help)

**Prior variance (tightness):** The variance around these means decreases with lag length and with cross-variable coefficients:

$$\text{Var}(\phi_{ij,k}) = \frac{\lambda^2}{k^2} \cdot \frac{\sigma_i^2}{\sigma_j^2}$$

where $\lambda > 0$ is the overall tightness hyperparameter. Small $\lambda$ → strong shrinkage toward random walk; $\lambda \to \infty$ → OLS. The $k^2$ decay shrinks higher lags more aggressively. The ratio $\sigma_i^2/\sigma_j^2$ scales coefficients by variable variances.

**Key Reference:** Litterman, R.B. (1986). "Forecasting with Bayesian vector autoregressions — five years of experience." *Journal of Business and Economic Statistics*, 4(1), 25–38.

### Normal-Wishart Extension

Kadiyala and Karlsson (1997) and Sims and Zha (1998) generalize the Minnesota prior to a **Normal-Wishart prior** that also places a prior on the error covariance $\Sigma$:

$$\text{vec}(\mathbf{B}) | \Sigma \sim N(\text{vec}(\mathbf{B}_0), \Sigma \otimes \mathbf{\Omega}_0)$$
$$\Sigma \sim \text{Inverse-Wishart}(\mathbf{S}_0, \nu_0)$$

This yields a closed-form **Normal-Wishart posterior** — no MCMC required. The posterior mean is a matrix-weighted average of the prior mean and the OLS estimate, with weights determined by prior precision and sample size.

### Large BVAR (LBVAR)

Bańbura, Giannone, and Reichlin (2010) demonstrate that **large BVARs** (20+ variables) with Minnesota prior shrinkage outperform small VARs and factor models for short-horizon forecasting. As the model grows, the prior automatically provides more shrinkage (through the tightness parameter $\lambda$). The optimal $\lambda$ is selected by maximizing the marginal likelihood — the Bayesian analogue of information criteria.

**Reference:** Bańbura, M., Giannone, D., and Reichlin, L. (2010). "Large Bayesian vector auto regressions." *Journal of Applied Econometrics*, 25(1), 71–92.

## Time-Varying Parameter VAR (TVP-VAR)

### Motivation

Standard BVAR assumes constant coefficients throughout the sample. But monetary policy transmission, fiscal multipliers, and financial market dynamics demonstrably evolve over time. TVP-VAR (Cogley & Sargent 2005; Primiceri 2005) allows all VAR coefficients to change at every time step via a random walk:

$$\mathbf{y}_t = \mathbf{B}_t^\top \mathbf{x}_t + \boldsymbol{\varepsilon}_t$$
$$\mathbf{B}_t = \mathbf{B}_{t-1} + \boldsymbol{\eta}_t, \quad \boldsymbol{\eta}_t \sim N(\mathbf{0}, \mathbf{Q})$$

where $\mathbf{x}_t = (\mathbf{y}_{t-1}^\top, \ldots, \mathbf{y}_{t-p}^\top, 1)^\top$ contains lagged variables and a constant.

Additionally, Primiceri (2005) allows the **error covariance** $\Sigma_t$ to evolve via a stochastic volatility process:

$$\boldsymbol{\varepsilon}_t = \mathbf{A}_t^{-1} \mathbf{H}_t^{1/2} \mathbf{u}_t$$

where $\mathbf{A}_t$ is a lower-triangular matrix with time-varying off-diagonal elements (capturing evolving contemporaneous correlations) and $\mathbf{H}_t$ is a diagonal matrix of time-varying variances.

**Key References:**
- Cogley, T. and Sargent, T.J. (2005). "Drifts and volatilities: Monetary policies and outcomes in the post WWII US." *Review of Economic Dynamics*, 8(2), 262–302.
- Primiceri, G.E. (2005). "Time varying structural vector autoregressions and monetary policy." *Review of Economic Studies*, 72(3), 821–852.

### Estimation via MCMC

The TVP-VAR state space system is estimated by Gibbs sampling:

1. **Sample coefficients** $\{\mathbf{B}_t\}_{t=1}^T$ — Kalman filter + simulation smoother given $\mathbf{Q}$, $\Sigma_t$
2. **Sample coefficient evolution variance** $\mathbf{Q}$ — Inverse-Wishart posterior
3. **Sample stochastic volatility** $\{h_{it}\}$ — Kim, Shephard & Chib (1998) auxiliary mixture sampler
4. **Sample contemporaneous correlations** $\{\mathbf{A}_t\}$ — equation-by-equation Gibbs given states

The computational cost is $O(T \cdot n^3)$ per MCMC iteration — feasible for moderate $n$ (≤ 10) and $T$ (≤ 200 quarters).

## Detecting Structural Change with TVP-VAR

TVP-VAR provides a continuous measure of parameter change rather than discrete break dates. Rapid changes in $\mathbf{B}_t$ infer structural breaks; slow drift suggests gradual evolution. Common diagnostics:

**Posterior of key coefficients over time:** Plot $E[B_{ij,t} | \mathbf{y}]$ across $t$. Sharp shifts in the posterior mean indicate break-like episodes; gradual trends indicate drift.

**Impulse response evolution:** Plot IRFs at different time points (e.g., pre/post financial crisis) to show how monetary policy transmission has changed over time.

## BVAR vs. TVP-VAR: When to Use Each

| Scenario | BVAR | TVP-VAR |
|----------|------|---------|
| Stable relationships, large $n$ | ✓ Preferred | ✗ Computationally heavy |
| Gradual parameter drift | ✗ Misspecified | ✓ Natural fit |
| Sharp structural breaks | ✗ Averages across break | ✓ Captures post-break |
| Forecasting accuracy | ✓ Strong | Mixed (can over-fit) |
| Identifying structural change | ✗ | ✓ Direct posterior |
| Short sample | ✓ Prior stabilizes | ✗ Needs many obs. |

A practical approach: use BVAR for forecasting, TVP-VAR for understanding how relationships have changed over time.

## Stochastic Search Variable Selection in BVAR

For very large systems, Korobilis (2013) combines spike-and-slab priors (as in BSTS) with BVAR to perform automatic variable selection in each VAR equation. This produces **sparse BVARs** that select only the most relevant lags and cross-variable predictors, further reducing over-fitting in high-dimensional systems.

**Reference:** Korobilis, D. (2013). "VAR forecasting using Bayesian variable selection." *Journal of Applied Econometrics*, 28(2), 204–230.

## Key References

- Litterman, R.B. (1986). *Journal of Business and Economic Statistics*, 4(1), 25–38.
- Bańbura, M., Giannone, D., and Reichlin, L. (2010). *Journal of Applied Econometrics*, 25(1), 71–92.
- Cogley, T. and Sargent, T.J. (2005). *Review of Economic Dynamics*, 8(2), 262–302.
- Primiceri, G.E. (2005). "Time varying structural vector autoregressions and monetary policy." *Review of Economic Studies*, 72(3), 821–852.
- Kadiyala, K.R. and Karlsson, S. (1997). "Numerical methods for estimation and inference in Bayesian VAR models." *Journal of Applied Econometrics*, 12(2), 99–132.
- Korobilis, D. (2013). "VAR forecasting using Bayesian variable selection." *Journal of Applied Econometrics*, 28(2), 204–230.
