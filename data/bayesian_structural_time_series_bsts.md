# Bayesian Structural Time Series (BSTS)

## Reference
Scott, S.L. and Varian, H.R. (2014). "Predicting the present with Bayesian structural time series." *International Journal of Mathematical Modelling and Numerical Optimisation*, 5(1/2), 4–23.

## Overview

Bayesian Structural Time Series (BSTS) combines three powerful ideas: (1) state space time series decomposition (trend, seasonality, regression), (2) Bayesian inference via MCMC for full uncertainty quantification, and (3) spike-and-slab variable selection for handling many potential predictors. The framework was developed at Google to nowcast economic activity using search query data and has since become a widely used tool for causal impact analysis and forecasting with covariate uncertainty.

## Model Structure

A BSTS model decomposes the observed series $y_t$ into additive components:

$$y_t = \mu_t + \tau_t + \boldsymbol{\beta}^\top \mathbf{x}_t + \varepsilon_t, \quad \varepsilon_t \sim N(0, \sigma_\varepsilon^2)$$

where:
- $\mu_t$: unobserved **local trend** (evolves over time)
- $\tau_t$: **seasonal component** (sum-to-zero constraint)
- $\boldsymbol{\beta}^\top \mathbf{x}_t$: **regression component** with contemporaneous predictors $\mathbf{x}_t$
- $\varepsilon_t$: observation noise

Each component is specified as a state equation, placing the entire model in **state space form**:

$$\mathbf{y}_t = \mathbf{Z}^\top \boldsymbol{\alpha}_t + \varepsilon_t$$
$$\boldsymbol{\alpha}_{t+1} = \mathbf{T} \boldsymbol{\alpha}_t + \mathbf{R} \boldsymbol{\eta}_t, \quad \boldsymbol{\eta}_t \sim N(\mathbf{0}, \mathbf{Q})$$

where $\boldsymbol{\alpha}_t = (\mu_t, b_t, \tau_t, \ldots)$ is the full state vector. The Kalman filter handles inference on $\boldsymbol{\alpha}_t$ given observations.

## Local Level and Local Linear Trend

**Local level (random walk trend):**
$$\mu_{t+1} = \mu_t + \eta_t, \quad \eta_t \sim N(0, \sigma_\mu^2)$$

Setting $\sigma_\mu^2 = 0$ gives a fixed level; larger $\sigma_\mu^2$ allows the level to drift. This is equivalent to exponential smoothing (ETS(A,N,N)).

**Local linear trend (level + slope):**
$$\mu_{t+1} = \mu_t + b_t + \eta_{\mu,t}$$
$$b_{t+1} = b_t + \eta_{b,t}, \quad \eta_{b,t} \sim N(0, \sigma_b^2)$$

The slope $b_t$ evolves as a random walk. Setting $\sigma_b^2$ small gives a near-constant slope (smooth trend); larger $\sigma_b^2$ allows rapid trend changes. This corresponds to ETS(A,A,N) in the exponential smoothing family.

**Semi-local linear trend (damped slope):**
$$b_{t+1} = D b_t + \eta_{b,t}$$

where $D \in (0,1)$ is a damping coefficient. As $|D| < 1$, the slope mean-reverts to zero, preventing explosive long-range extrapolation. This is often preferable for business data where long-run trend growth is uncertain.

## Spike-and-Slab Prior for Variable Selection

When many potential predictors $\mathbf{x}_t = (x_{1t}, \ldots, x_{pt})$ are available (e.g., hundreds of Google search queries), model selection is critical. BSTS uses a **spike-and-slab prior** on the regression coefficients:

$$\beta_j | \gamma_j \sim (1 - \gamma_j) \delta_0 + \gamma_j N(0, \sigma_\beta^2)$$
$$\gamma_j \sim \text{Bernoulli}(\pi_j)$$

where $\gamma_j \in \{0, 1\}$ is a binary inclusion indicator. The prior is a mixture of a point mass at zero ("spike") and a diffuse Normal ("slab"). 

**Interpretation:**
- $P(\gamma_j = 1) = \pi_j$: prior inclusion probability, typically $\pi_j = \bar{k}/p$ where $\bar{k}$ is the expected model size
- $\gamma_j = 0$: predictor $j$ is excluded from the model
- $\gamma_j = 1$: predictor $j$ is included with Normal prior on its coefficient

**Posterior inclusion probability (PIP):**
$$\text{PIP}_j = P(\gamma_j = 1 | \mathbf{y}) = \text{fraction of MCMC draws with } \gamma_j = 1$$

Predictors with PIP > 0.5 are reliably selected; those with PIP < 0.1 contribute negligibly and can be dropped.

## MCMC Estimation

The full BSTS posterior is sampled by alternating between:

1. **Sample state vector** $\boldsymbol{\alpha}_{1:T}$ via Kalman filter + simulation smoother (Durbin & Koopman 2002): draw a trajectory of latent states consistent with observations and parameters
2. **Sample variance parameters** $(\sigma_\varepsilon^2, \sigma_\mu^2, \sigma_b^2)$ from their inverse-Gamma posteriors
3. **Sample regression coefficients and indicators** $(\boldsymbol{\beta}, \boldsymbol{\gamma})$ via stochastic search variable selection (George & McCulloch 1997)

Each MCMC iteration produces a complete model (which predictors to include, their coefficients, and the state trajectory), naturally averaging over model uncertainty in final forecasts.

## Forecasting and Uncertainty

The $h$-step-ahead predictive distribution is obtained by:
1. For each MCMC draw $(\boldsymbol{\theta}^{(s)}, \boldsymbol{\gamma}^{(s)})$, simulate the state forward $h$ steps
2. Average the resulting distributions over all MCMC draws

This propagates **four sources of uncertainty**: (i) observation noise, (ii) state evolution noise, (iii) regression coefficient uncertainty, and (iv) model uncertainty (which predictors are included). The resulting prediction intervals are wider and better-calibrated than point-forecast confidence intervals.

## CausalImpact: Counterfactual Estimation

Brodersen et al. (2015) extended BSTS to causal inference via the **CausalImpact** framework:

1. Fit BSTS model to pre-intervention data, using control series as predictors
2. Forecast counterfactual (what would have happened without intervention) during the post-intervention period
3. Causal impact = actual outcome − counterfactual forecast

The Bayesian framework provides a posterior distribution over the causal effect at each time point, with credible intervals. This is widely used for policy evaluation, A/B testing with temporal data, and assessing the impact of structural breaks (e.g., regulatory changes, product launches).

**Reference:** Brodersen, K.H. et al. (2015). "Inferring causal impact using Bayesian structural time-series models." *Annals of Applied Statistics*, 9(1), 247–274.

## Comparison to Alternative Approaches

| Feature | ARIMA/ETS | Prophet | BSTS |
|---------|-----------|---------|------|
| Trend model | Fixed specification | Piecewise linear | Flexible state space |
| Covariate selection | Manual | Manual | Automatic (spike-slab) |
| Uncertainty quantification | Asymptotic CIs | Bootstrap | Full posterior |
| Structural break handling | Post-hoc | Automatic changepoints | Via state space flexibility |
| Variable selection | Not available | Not available | Spike-and-slab PIP |
| Causal inference | Not designed for | Not designed for | CausalImpact extension |

## Software

- **R:** `bsts` package (Scott 2017) — the reference implementation
- **Python:** `tfp.sts` (TensorFlow Probability) implements BSTS with VI or HMC
- **Python:** `causalimpact` package wraps CausalImpact methodology

## Key References

- Scott, S.L. and Varian, H.R. (2014). "Predicting the present with Bayesian structural time series." *International Journal of Mathematical Modelling and Numerical Optimisation*, 5(1/2), 4–23.
- Brodersen, K.H., Gallusser, F., Koehler, J., Remy, N., and Scott, S.L. (2015). "Inferring causal impact using Bayesian structural time-series models." *Annals of Applied Statistics*, 9(1), 247–274.
- Harvey, A.C. (1989). *Forecasting, Structural Time Series Models and the Kalman Filter*. Cambridge University Press.
- George, E.I. and McCulloch, R.E. (1997). "Approaches for Bayesian variable selection." *Statistica Sinica*, 7(2), 339–374.
- Durbin, J. and Koopman, S.J. (2002). "A simple and efficient simulation smoother for state space time series analysis." *Biometrika*, 89(3), 603–616.
