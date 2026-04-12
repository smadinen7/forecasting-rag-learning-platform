# Vector Autoregression (VAR) Models

## Overview

Vector Autoregression (VAR) is the standard framework for modeling the joint dynamics of multiple time series. Introduced by Sims (1980) as a critique of large structural macroeconomic models, VAR treats all variables as endogenous and allows each to depend on lagged values of all variables in the system. VAR models are central to empirical macroeconomics, monetary policy analysis, and multivariate forecasting.

**Key Reference:** Sims, C.A. (1980). "Macroeconomics and reality." *Econometrica*, 48(1), 1–48.

## VAR(p) Model

A VAR(p) model for an $n$-dimensional vector $\mathbf{y}_t = (y_{1t}, \ldots, y_{nt})^\top$ is:

$$\mathbf{y}_t = \mathbf{c} + A_1 \mathbf{y}_{t-1} + A_2 \mathbf{y}_{t-2} + \cdots + A_p \mathbf{y}_{t-p} + \boldsymbol{\varepsilon}_t$$

where $\mathbf{c}$ is an $n \times 1$ intercept vector, $A_i$ are $n \times n$ coefficient matrices, and $\boldsymbol{\varepsilon}_t \sim \text{WN}(\mathbf{0}, \Sigma)$ with contemporaneous covariance matrix $\Sigma$.

**Key insight:** Each equation in the VAR is an OLS regression of $y_{it}$ on $p$ lags of all $n$ variables. With $n$ variables and $p$ lags, each equation has $np$ slope coefficients — the total parameter count is $n^2 p + n$. This grows rapidly with $n$ and $p$, creating an over-fitting risk for large systems.

## Lag Length Selection

The lag order $p$ is selected by minimizing information criteria over the full system:

$$\text{AIC}(p) = \ln|\hat{\Sigma}_p| + \frac{2n^2 p}{T}$$
$$\text{BIC}(p) = \ln|\hat{\Sigma}_p| + \frac{n^2 p \ln T}{T}$$

where $|\hat{\Sigma}_p|$ is the determinant of the residual covariance matrix. BIC tends to select more parsimonious models; AIC may overfit in small samples. The Hannan-Quinn criterion (HQ) is a compromise. In practice, test multiple criteria and inspect residual autocorrelation at the chosen lag.

## Granger Causality

Granger (1969) proposed a statistical definition of causality: $x$ **Granger-causes** $y$ if past values of $x$ improve the prediction of $y$ beyond what past values of $y$ alone provide. In a bivariate VAR:

$$y_t = \sum_{i=1}^p \alpha_i y_{t-i} + \sum_{i=1}^p \beta_i x_{t-i} + \varepsilon_t$$

Test $H_0: \beta_1 = \beta_2 = \cdots = \beta_p = 0$ via an F-test. Rejection means $x$ Granger-causes $y$.

**Important caveat:** Granger causality is a statement about predictability, not physical causality. It can be spurious if both series are driven by a common omitted factor.

**Reference:** Granger, C.W.J. (1969). "Investigating causal relations by econometric models and cross-spectral methods." *Econometrica*, 37(3), 424–438.

## Impulse Response Functions (IRF)

An IRF traces the dynamic response of each variable in the system to a one-unit shock to one variable, holding all other shocks at zero. It answers: "If interest rates unexpectedly rise by 1 percentage point, how does GDP respond over the next 12 quarters?"

The $h$-step IRF is derived from the VAR moving average (VMA) representation:
$$\mathbf{y}_t = \boldsymbol{\mu} + \sum_{j=0}^{\infty} \Phi_j \boldsymbol{\varepsilon}_{t-j}$$

where $\Phi_0 = I$ and $\Phi_j = \sum_{i=1}^{\min(j,p)} A_i \Phi_{j-i}$. The element $[\Phi_h]_{ij}$ gives the response of variable $i$ to a shock to variable $j$ after $h$ periods.

**Identification:** Since $\Sigma$ is generally non-diagonal, raw shocks are correlated. **Cholesky decomposition** orthogonalizes the shocks using a lower-triangular matrix $P$ such that $\Sigma = PP^\top$. The orthogonalized IRF is $\Phi_h P$, and the ordering of variables matters (Cholesky gives the first variable full contemporaneous impact on all others).

## Forecast Error Variance Decomposition (FEVD)

FEVD decomposes the $h$-step forecast error variance of each variable into contributions from each structural shock. It answers: "What fraction of the forecast error variance of GDP is attributable to monetary policy shocks vs. demand shocks?"

$$\text{FEVD}_{ij}(h) = \frac{\sum_{s=0}^{h-1} ([\Phi_s P]_{ij})^2}{\sum_{s=0}^{h-1} \sum_{k=1}^n ([\Phi_s P]_{ik})^2}$$

At $h=1$, FEVD equals the fraction of variance from contemporaneous shocks. As $h \to \infty$, FEVD converges to the unconditional contribution of each shock.

## Structural VAR (SVAR)

The reduced-form VAR's contemporaneous covariance $\Sigma$ does not identify structural shocks. SVAR imposes economic restrictions on the contemporaneous impact matrix $B_0$ in:

$$B_0 \mathbf{y}_t = \mathbf{c} + B_1 \mathbf{y}_{t-1} + \cdots + B_p \mathbf{y}_{t-p} + \boldsymbol{\eta}_t$$

where $\boldsymbol{\eta}_t$ are uncorrelated structural shocks with unit variance. Common identification strategies:
- **Short-run restrictions:** Zero restrictions on $B_0$ (e.g., monetary policy does not affect output contemporaneously)
- **Long-run restrictions:** Blanchard-Quah (1989) — some shocks have no long-run effect on certain variables
- **Sign restrictions:** Bounds on IRF signs over specified horizons

**Reference:** Lütkepohl, H. (2005). *New Introduction to Multiple Time Series Analysis*. Springer-Verlag.

## VAR with Structural Breaks

Standard VAR assumes constant coefficients. Under structural instability, allow time-varying coefficient VAR:

$$\mathbf{y}_t = A_{1,t} \mathbf{y}_{t-1} + \cdots + A_{p,t} \mathbf{y}_{t-p} + \boldsymbol{\varepsilon}_t$$

Approaches include: MS-VAR (Markov-switching VAR, where $A_{i,t}$ jumps between regimes), TVP-VAR (time-varying parameter VAR estimated via Kalman filter), and segmented VAR (estimate separate VARs before/after detected break dates).

## Forecasting from VAR

$h$-step forecasts are computed by iterating forward from the last observation:
$$\hat{\mathbf{y}}_{T+h|T} = \hat{A}_1 \hat{\mathbf{y}}_{T+h-1|T} + \cdots + \hat{A}_p \hat{\mathbf{y}}_{T+h-p|T}$$

VAR forecasts often outperform equation-by-equation univariate models when variables are genuinely related, but under-perform when the system is large and the sample is small (over-fitting). Bayesian VAR (BVAR) with Minnesota prior shrinkage typically outperforms OLS VAR in forecasting competitions.

## Key References

- Sims, C.A. (1980). "Macroeconomics and reality." *Econometrica*, 48(1), 1–48.
- Granger, C.W.J. (1969). "Investigating causal relations by econometric models." *Econometrica*, 37(3), 424–438.
- Lütkepohl, H. (2005). *New Introduction to Multiple Time Series Analysis*. Springer-Verlag.
- Blanchard, O.J. and Quah, D. (1989). "The dynamic effects of aggregate demand and supply disturbances." *American Economic Review*, 79(4), 655–673.
- Litterman, R.B. (1986). "Forecasting with Bayesian vector autoregressions." *Review of Economics and Statistics*, 68(4), 664–671.
