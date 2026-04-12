# Forecasting Time Series Subject to Multiple Structural Breaks

## Reference
Pesaran, M.H., Pettenuzzo, D., and Timmermann, A. (2006). "Forecasting time series subject to multiple structural breaks." *Review of Economic Studies*, 73(4), 1057–1084.

## Overview

This paper addresses one of the most practically important problems in time series forecasting: how to generate accurate predictions when the data-generating process has undergone — and may continue to undergo — discrete structural breaks. Standard forecasting approaches either ignore breaks entirely (biasing forecasts toward a misspecified model) or use only post-break data (discarding useful historical information). Pesaran, Pettenuzzo, and Timmermann (PPT) propose a Bayesian framework that explicitly models the break process, forecasts the probability of future breaks, and optimally pools information across regimes.

## The Core Problem: Forecasting Through Breaks

When a structural break occurs at unknown date $\tau$, the forecaster faces a fundamental trade-off:

- **Use all data ($t = 1, \ldots, T$):** Full-sample estimates are biased if post-break parameters differ substantially from pre-break parameters. The bias grows with the magnitude of the break.
- **Use only post-break data ($t = \tau+1, \ldots, T$):** Unbiased but high-variance estimates due to short post-break sample. Parameter uncertainty can dominate forecast error.
- **Optimal approach:** Weight pre- and post-break data by the ratio of estimation variance to break-induced bias — which depends on unknown break magnitude and timing.

PPT provide a framework that achieves this weighting automatically through Bayesian updating.

## Hierarchical Hidden Markov Chain Model

The model assumes the process switches among $m$ regimes according to a hidden Markov chain $\{s_t\}$, but with a key restriction: the chain is **absorbing** — once a break occurs, the process moves to a new regime and never returns to a previous one. This distinguishes it from standard Markov-switching models (Hamilton 1989) where regimes recur.

In each regime $j$, the data follow:
$$y_t = x_t^\top \beta_j + \sigma_j \varepsilon_t, \quad \varepsilon_t \sim N(0,1)$$

where $\beta_j$ and $\sigma_j^2$ are regime-specific parameters. The transition probability from regime $j$ to $j+1$ is $p_j$ (probability of a break occurring), with $p_m = 0$ (terminal regime stays forever).

**Hierarchical prior:** Rather than specifying independent priors on each $(\beta_j, \sigma_j^2)$, PPT use a hierarchical prior where all regime parameters are drawn from a common hyperprior:
$$\beta_j \sim N(\mu_\beta, \Sigma_\beta), \quad \sigma_j^{-2} \sim \text{Gamma}(a_\sigma, b_\sigma)$$

This hierarchical structure is critical: it allows information to be shared across regimes. Even if the current regime has few observations, the posterior for its parameters is shrunk toward the hyperprior mean — which is itself estimated from all past regimes. This produces a natural, data-driven pooling of information.

## Bayesian Estimation via MCMC

The model is estimated by Gibbs sampling, cycling through:

1. **Sample regime allocations** $\{s_t\}$ given data and parameters (forward-backward algorithm, as in Chib 1996)
2. **Sample regime-specific parameters** $(\beta_j, \sigma_j^2)$ given regime allocations
3. **Sample hyperparameters** $(\mu_\beta, \Sigma_\beta, a_\sigma, b_\sigma)$ given all regime parameters
4. **Sample transition probabilities** $\{p_j\}$ from their Beta posterior

The key computational challenge is that the number of regimes $m$ is unknown. PPT address this by specifying a maximum number of regimes $m_{\max}$ and allowing some regimes to be empty.

## Forecasting Under Break Uncertainty

The $h$-step-ahead predictive distribution integrates over three sources of uncertainty:

$$p(y_{T+h} | \mathbf{y}_{1:T}) = \int p(y_{T+h} | \theta_{s_{T+h}}) \cdot P(s_{T+h} | \mathbf{y}_{1:T}) \cdot p(\theta_{s_{T+h}} | \mathbf{y}_{1:T}) \, d\theta$$

1. **Parameter uncertainty:** Given a regime, $\beta_j$ and $\sigma_j^2$ are uncertain
2. **Regime uncertainty:** The current regime $s_T$ is not directly observed; filtered probabilities provide a distribution
3. **Future break uncertainty:** With probability $p_{s_T}$, a new break occurs before the forecast horizon, shifting to regime $s_T + 1$ with its own (uncertain) parameters

For long horizons, the probability of a future break becomes substantial. The PPT model explicitly accounts for this by simulating future regime paths from the transition structure and averaging forecasts over them. This produces **wider, better-calibrated prediction intervals** than models that ignore future break risk.

## Key Empirical Findings

**Application: U.S. Treasury bill rates**
- The data exhibit multiple documented breaks (early 1980s Volcker disinflation, mid-1980s decline in rates)
- PPT model produces significantly better out-of-sample RMSE than:
  - Full-sample OLS (biased by pre-break data)
  - Rolling/recursive windows (high variance, ignores structure)
  - Standard Markov-switching (allows regime recurrence, unrealistic for rates)
- Gains are largest at medium horizons (6–18 months) where break uncertainty is most relevant

## Connection to Related Work

**Versus Markov-switching (Hamilton 1989):** PPT restricts regimes to be non-recurring (absorbing chain). This is appropriate for structural breaks (e.g., regulatory changes, long-run trend shifts) but not for business cycle regimes that recur.

**Versus Bai-Perron (2003):** Bai-Perron estimates breaks as deterministic events at fixed dates. PPT treats break dates as random and integrates over break uncertainty in forecasts. The PPT approach is more appropriate when forecasting forward.

**Pettenuzzo & Timmermann (2011) extension:** Apply the PPT framework to equity return predictability, showing that accounting for future breaks significantly improves asset allocation decisions and avoids large welfare losses from ignoring break risk.

## Practical Implications

1. **Rolling window vs. full-sample:** PPT provides theoretical justification for using the full sample with shrinkage toward recent data — neither extreme (full sample OLS nor post-break only) is optimal.
2. **Prediction interval width:** Models that ignore future break risk systematically produce intervals that are too narrow, especially at long horizons.
3. **Regime pooling:** The hierarchical prior prevents over-fitting to short post-break samples — a common failure of break-corrected forecasting approaches.

## Key References

- Pesaran, M.H., Pettenuzzo, D., and Timmermann, A. (2006). "Forecasting time series subject to multiple structural breaks." *Review of Economic Studies*, 73(4), 1057–1084.
- Pettenuzzo, D. and Timmermann, A. (2011). "Predictability of stock returns and asset allocation under structural breaks." *Journal of Econometrics*, 164(1), 60–78.
- Chib, S. (1998). "Estimation and comparison of multiple change-point models." *Journal of Econometrics*, 86(2), 221–241.
- Hamilton, J.D. (1989). "A new approach to the economic analysis of nonstationary time series." *Econometrica*, 57(2), 357–384.
- Bai, J. and Perron, P. (2003). "Computation and analysis of multiple structural change models." *Journal of Applied Econometrics*, 18(1), 1–22.
