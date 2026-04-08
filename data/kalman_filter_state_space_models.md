# Kalman Filter and State Space Models

## Overview

The Kalman filter (Kalman, 1960) is an optimal recursive algorithm for estimating the unobserved state of a linear dynamical system from noisy observations. State space models provide a flexible framework that unifies many time series models — including ARIMA, unobserved components models, dynamic factor models, and time-varying parameter models — under a single estimation framework.

**Key Reference:** Kalman, R.E. (1960). "A new approach to linear filtering and prediction problems." *Journal of Basic Engineering*, 82(1), 35–45.

## State Space Representation

A general linear state space model has two equations:

**Measurement (observation) equation:**
$$y_t = Z_t \alpha_t + d_t + \varepsilon_t, \quad \varepsilon_t \sim N(0, H_t)$$

**Transition (state) equation:**
$$\alpha_t = T_t \alpha_{t-1} + c_t + R_t \eta_t, \quad \eta_t \sim N(0, Q_t)$$

where:
- $y_t$: $p \times 1$ observation vector
- $\alpha_t$: $m \times 1$ unobserved state vector
- $Z_t, T_t, R_t$: system matrices (may be time-varying)
- $d_t, c_t$: deterministic components (intercepts, trends)
- $H_t, Q_t$: observation and state noise covariance matrices

**Assumption:** $\varepsilon_t$ and $\eta_t$ are mutually uncorrelated; the system is initialized with $\alpha_1 \sim N(a_1, P_1)$.

## The Kalman Filter Recursion

The Kalman filter operates in two steps per period:

**Prediction step** (prior to observing $y_t$):
$$a_{t|t-1} = T_t a_{t-1|t-1} + c_t$$
$$P_{t|t-1} = T_t P_{t-1|t-1} T_t^\top + R_t Q_t R_t^\top$$

**Update step** (upon observing $y_t$):
$$v_t = y_t - Z_t a_{t|t-1} - d_t \quad \text{(innovation)}$$
$$F_t = Z_t P_{t|t-1} Z_t^\top + H_t \quad \text{(innovation variance)}$$
$$K_t = P_{t|t-1} Z_t^\top F_t^{-1} \quad \text{(Kalman gain)}$$
$$a_{t|t} = a_{t|t-1} + K_t v_t$$
$$P_{t|t} = (I - K_t Z_t) P_{t|t-1}$$

The **Kalman gain** $K_t$ determines the weight placed on the new observation vs. the prior state prediction. When $H_t$ is small (precise measurements), $K_t \to Z_t^{-1}$ and the state tracks observations closely. When $Q_t$ is small (slow-evolving state), $K_t$ is small and the estimate is anchored to the prediction.

**Reference:** Durbin, J. and Koopman, S.J. (2012). *Time Series Analysis by State Space Methods* (2nd ed.). Oxford University Press.

## Log-Likelihood via Prediction Error Decomposition

The log-likelihood is computed from the innovations (prediction errors):
$$\ln L = -\frac{1}{2}\sum_{t=1}^T \left[p \ln(2\pi) + \ln |F_t| + v_t^\top F_t^{-1} v_t\right]$$

This prediction error decomposition allows direct MLE of unknown parameters (variance matrices, autoregressive coefficients) by treating them as optimization targets.

## Kalman Smoother (RTS Smoother)

The Kalman filter produces **filtered** estimates $a_{t|t}$ using data up to $t$. The **Rauch-Tung-Striebel (RTS) smoother** passes backward through the filtered output to produce **smoothed** estimates $a_{t|T}$ using the full sample $t = 1, \ldots, T$:

$$a_{t|T} = a_{t|t} + L_t (a_{t+1|T} - a_{t+1|t})$$
$$P_{t|T} = P_{t|t} + L_t (P_{t+1|T} - P_{t+1|t}) L_t^\top$$

where $L_t = P_{t|t} T_{t+1}^\top P_{t+1|t}^{-1}$.

Smoothed estimates have lower variance than filtered estimates and are used for: historical decomposition, parameter estimation (EM algorithm), and retrospective analysis.

## Unobserved Components Model

The **structural time series** or **unobserved components (UC)** model decomposes a series into interpretable components:

$$y_t = \mu_t + \gamma_t + \psi_t + \varepsilon_t$$

where $\mu_t$ (trend), $\gamma_t$ (seasonal), $\psi_t$ (cycle), $\varepsilon_t$ (irregular) each have their own state space representation. For example, the **local linear trend**:

$$\mu_t = \mu_{t-1} + \nu_{t-1} + \eta_t, \quad \eta_t \sim N(0, \sigma_\eta^2)$$
$$\nu_t = \nu_{t-1} + \zeta_t, \quad \zeta_t \sim N(0, \sigma_\zeta^2)$$

Setting $\sigma_\eta^2 = 0$ gives a random walk with drift; setting $\sigma_\zeta^2 = 0$ gives a smooth trend.

**Reference:** Harvey, A.C. (1989). *Forecasting, Structural Time Series Models and the Kalman Filter*. Cambridge University Press.

## Time-Varying Parameter Models

State space models naturally accommodate **time-varying coefficients**. The state vector contains the regression coefficients, which evolve as a random walk:

$$y_t = x_t^\top \beta_t + \varepsilon_t$$
$$\beta_t = \beta_{t-1} + \eta_t$$

This is equivalent to allowing the forecasting model to drift slowly over time — useful when relationships between variables are expected to evolve (e.g., changing monetary policy transmission, shifting factor loadings in macro forecasting).

## Relation to ARIMA

Any ARIMA($p$,$d$,$q$) model can be written in state space form, making the Kalman filter an alternative estimation approach to conditional maximum likelihood. The state space representation is particularly useful for:
- Handling missing observations (skip the update step for $t$ with missing $y_t$)
- Non-Gaussian or non-linear extensions (particle filters, extended Kalman filter)
- Directly incorporating explanatory variables with time-varying coefficients

## Missing Data Handling

A key advantage of state space models is seamless handling of missing observations. When $y_t$ is missing, simply skip the update step: $a_{t|t} = a_{t|t-1}$ and $P_{t|t} = P_{t|t-1}$. This is why state space / Kalman filter methods are the standard tool for nowcasting with ragged-edge data (see Giannone et al., 2008).

## Key References

- Kalman, R.E. (1960). "A new approach to linear filtering and prediction problems." *Journal of Basic Engineering*, 82(1), 35–45.
- Harvey, A.C. (1989). *Forecasting, Structural Time Series Models and the Kalman Filter*. Cambridge University Press.
- Durbin, J. and Koopman, S.J. (2012). *Time Series Analysis by State Space Methods* (2nd ed.). Oxford University Press.
- Hamilton, J.D. (1994). *Time Series Analysis*. Princeton University Press. Chapters 13–14.
