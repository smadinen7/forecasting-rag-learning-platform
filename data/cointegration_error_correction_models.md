# Cointegration and Error Correction Models

## Overview

Cointegration describes a long-run equilibrium relationship between two or more non-stationary time series. Although individually integrated (non-stationary), a linear combination of cointegrated series is stationary — they share a common stochastic trend and cannot drift apart indefinitely. The Error Correction Model (ECM) captures both the long-run equilibrium and short-run adjustment dynamics.

**Key Reference:** Engle, R.F. and Granger, C.W.J. (1987). "Co-integration and error correction: Representation, estimation, and testing." *Econometrica*, 55(2), 251–276.

## The Spurious Regression Problem

Granger and Newbold (1974) demonstrated that regressing one I(1) series on another unrelated I(1) series frequently yields a high $R^2$ and significant $t$-statistics — yet the relationship is entirely spurious, an artifact of shared trending behavior. Standard OLS inference is invalid when both series have unit roots and are not cointegrated.

This motivates the need to test for cointegration before interpreting any long-run regression between integrated variables.

**Reference:** Granger, C.W.J. and Newbold, P. (1974). "Spurious regressions in econometrics." *Journal of Econometrics*, 2(2), 111–120.

## Definition of Cointegration

Two I(1) series $y_t$ and $x_t$ are cointegrated of order CI(1,1) if there exists a constant $\beta$ such that:
$$z_t = y_t - \beta x_t \sim I(0)$$

The vector $(1, -\beta)$ is the **cointegrating vector**, and $z_t$ is the stationary **cointegrating residual** (error correction term). The parameter $\beta$ represents the long-run equilibrium relationship.

More generally, an $n$-dimensional vector of I(1) series $\mathbf{y}_t$ can have up to $n-1$ linearly independent cointegrating relationships, collected as rows of the cointegrating matrix $\boldsymbol{\beta}$.

## Engle-Granger Two-Step Procedure

For the bivariate case, Engle and Granger (1987) proposed a simple two-step approach:

**Step 1:** Estimate the long-run (cointegrating) regression by OLS:
$$y_t = \alpha + \beta x_t + z_t$$

**Step 2:** Test whether the residuals $\hat{z}_t$ are stationary using the ADF test (Engle-Granger cointegration test). Critical values differ from standard ADF critical values because the residuals are estimated, not observed.

**Limitation:** The Engle-Granger procedure assumes a unique cointegrating vector and cannot handle more than two variables well. The Johansen procedure generalizes to multiple variables.

## Error Correction Model (ECM)

If $y_t$ and $x_t$ are cointegrated, the Granger Representation Theorem guarantees that there exists an error correction representation:

$$\Delta y_t = \alpha_y (y_{t-1} - \beta x_{t-1}) + \sum_{j=1}^p \gamma_j \Delta y_{t-j} + \sum_{j=0}^q \delta_j \Delta x_{t-j} + \varepsilon_t$$

The term $(y_{t-1} - \beta x_{t-1}) = z_{t-1}$ is the **error correction term** (ECT) — the lagged deviation from long-run equilibrium. The coefficient $\alpha_y$ is the **speed of adjustment**: how quickly $y_t$ corrects back toward equilibrium after a deviation.

**Interpretation:**
- $\alpha_y < 0$: $y_t$ error-corrects toward the equilibrium (as expected for a stable relationship)
- $|\alpha_y|$ large: fast adjustment; $|\alpha_y|$ small: slow adjustment
- $\alpha_y = 0$: $y_t$ does not adjust; all correction comes from $x_t$

Short-run dynamics (the $\Delta$ terms) capture transient fluctuations around the long-run trend.

## Johansen Cointegration Test

For $n$-dimensional systems, Johansen (1988) developed a maximum likelihood procedure that simultaneously estimates the number of cointegrating vectors and the VECM parameters.

The Vector Error Correction Model (VECM) is:
$$\Delta \mathbf{y}_t = \Pi \mathbf{y}_{t-1} + \sum_{j=1}^{p-1} \Gamma_j \Delta \mathbf{y}_{t-j} + \boldsymbol{\varepsilon}_t$$

where $\Pi = \alpha \beta^\top$ with $\alpha$ (adjustment coefficients) and $\beta$ (cointegrating vectors) each of dimension $n \times r$, and $r$ is the cointegrating rank.

**Johansen tests for cointegrating rank $r$:**

1. **Trace test:** $H_0$: at most $r$ cointegrating vectors
$$\lambda_{\text{trace}}(r) = -T \sum_{i=r+1}^n \ln(1 - \hat{\lambda}_i)$$

2. **Maximum eigenvalue test:** $H_0$: exactly $r$ vs. $H_1$: $r+1$ cointegrating vectors
$$\lambda_{\max}(r, r+1) = -T \ln(1 - \hat{\lambda}_{r+1})$$

where $\hat{\lambda}_i$ are the ordered eigenvalues from a reduced-rank regression.

**Reference:** Johansen, S. (1988). "Statistical analysis of cointegration vectors." *Journal of Economic Dynamics and Control*, 12(2-3), 231–254.
**Reference:** Johansen, S. and Juselius, K. (1990). "Maximum likelihood estimation and inference on cointegration." *Oxford Bulletin of Economics and Statistics*, 52(2), 169–210.

## Common Applications

**Purchasing Power Parity (PPP):** The real exchange rate (nominal exchange rate adjusted for relative price levels) should be I(0) if PPP holds. Testing PPP reduces to testing cointegration between the nominal exchange rate and the ratio of price levels.

**Stock price and dividends:** Gordon Growth Model implies a cointegrating relationship between log stock prices and log dividends.

**Interest rate term structure:** Long-term and short-term interest rates should be cointegrated; the spread is stationary.

**Consumption and income:** Permanent income hypothesis implies cointegration between consumption and income.

## Practical Considerations

- The Johansen procedure requires specifying whether the VECM includes intercepts and/or trends (in the cointegrating relations and/or the short-run dynamics). Five specifications exist (Case I–V in Johansen, 1995).
- Lag length selection in the VECM follows the same AIC/BIC criteria as VAR models.
- Cointegration tests have low power in small samples; findings should be interpreted cautiously for series shorter than ~100 observations.

## Key References

- Engle, R.F. and Granger, C.W.J. (1987). "Co-integration and error correction." *Econometrica*, 55(2), 251–276.
- Granger, C.W.J. and Newbold, P. (1974). "Spurious regressions in econometrics." *Journal of Econometrics*, 2(2), 111–120.
- Johansen, S. (1988). "Statistical analysis of cointegration vectors." *Journal of Economic Dynamics and Control*, 12(2-3), 231–254.
- Johansen, S. and Juselius, K. (1990). "Maximum likelihood estimation and inference on cointegration." *Oxford Bulletin of Economics and Statistics*, 52(2), 169–210.
- Johansen, S. (1995). *Likelihood-Based Inference in Cointegrated Vector Autoregressive Models*. Oxford University Press.
