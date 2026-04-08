# Classical Time Series Methods: ARIMA and Box-Jenkins

## Overview

The Box-Jenkins methodology provides a systematic framework for identifying, estimating, and forecasting with ARIMA (AutoRegressive Integrated Moving Average) models. Developed by Box and Jenkins (1976), this approach remains the foundational toolkit for univariate time series forecasting.

**Key Reference:** Box, G.E.P., Jenkins, G.M., Reinsel, G.C., and Ljung, G.M. (2015). *Time Series Analysis: Forecasting and Control* (5th ed.). Wiley.

## Stationarity

A time series $\{y_t\}$ is **weakly (covariance) stationary** if:
1. $E[y_t] = \mu$ (constant mean)
2. $\text{Var}(y_t) = \sigma^2 < \infty$ (constant variance)
3. $\text{Cov}(y_t, y_{t-k}) = \gamma_k$ depends only on lag $k$, not on $t$

Stationarity is a prerequisite for ARIMA modeling. Non-stationary series (trending means, unit roots, heteroskedastic variance) must be transformed before model fitting.

**Testing for stationarity:**
- **Augmented Dickey-Fuller (ADF) test** (Said & Dickey, 1984): Tests the null hypothesis of a unit root ($H_0$: non-stationary) against the alternative of stationarity. Rejecting $H_0$ implies stationarity.
- **KPSS test** (Kwiatkowski et al., 1992): Tests $H_0$: stationarity against $H_1$: unit root. Failing to reject $H_0$ is evidence of stationarity.

Using both ADF and KPSS together provides a more reliable assessment: if ADF rejects and KPSS fails to reject, stationarity is strongly supported; if both reject, the series may have a more complex structure (e.g., fractional integration).

**References:**
- Dickey, D.A. and Fuller, W.A. (1979). "Distribution of the estimators for autoregressive time series with a unit root." *Journal of the American Statistical Association*, 74(366), 427–431.
- Said, S.E. and Dickey, D.A. (1984). "Testing for unit roots in autoregressive-moving average models of unknown order." *Biometrika*, 71(3), 599–607.
- Kwiatkowski, D., Phillips, P.C.B., Schmidt, P., and Shin, Y. (1992). "Testing the null hypothesis of stationarity against the alternative of a unit root." *Journal of Econometrics*, 54(1-3), 159–178.

## Differencing and Integration

If a series has a unit root (non-stationary), **first differencing** $\Delta y_t = y_t - y_{t-1}$ typically induces stationarity. The number of differences required to achieve stationarity is the **order of integration** $d$:
- $I(0)$: Already stationary
- $I(1)$: Stationary after one difference (most economic/financial series)
- $I(2)$: Stationary after two differences (rare in practice)

Seasonal differencing $\Delta_s y_t = y_t - y_{t-s}$ removes deterministic or stochastic seasonality of period $s$.

## Autoregressive (AR) Models

An AR($p$) model expresses $y_t$ as a linear function of its own $p$ lagged values:

$$y_t = c + \phi_1 y_{t-1} + \phi_2 y_{t-2} + \cdots + \phi_p y_{t-p} + \varepsilon_t$$

where $\varepsilon_t \sim \text{WN}(0, \sigma^2)$ (white noise). The AR($p$) is stationary when all roots of the characteristic polynomial $1 - \phi_1 z - \cdots - \phi_p z^p = 0$ lie outside the unit circle.

## Moving Average (MA) Models

An MA($q$) model expresses $y_t$ as a linear combination of current and past white noise shocks:

$$y_t = \mu + \varepsilon_t + \theta_1 \varepsilon_{t-1} + \cdots + \theta_q \varepsilon_{t-q}$$

MA processes are always stationary. **Invertibility** (analogous to stationarity for AR) requires that roots of $1 + \theta_1 z + \cdots + \theta_q z^q = 0$ lie outside the unit circle.

## ARMA and ARIMA Models

An ARMA($p$,$q$) model combines both components:
$$\phi(L) y_t = c + \theta(L) \varepsilon_t$$

where $\phi(L) = 1 - \phi_1 L - \cdots - \phi_p L^p$ and $\theta(L) = 1 + \theta_1 L + \cdots + \theta_q L^q$.

An **ARIMA($p$,$d$,$q$)** model applies the ARMA to the $d$-th differenced series:
$$\phi(L)(1-L)^d y_t = c + \theta(L) \varepsilon_t$$

## Box-Jenkins Identification via ACF and PACF

The **ACF (Autocorrelation Function)** $\rho_k = \text{Corr}(y_t, y_{t-k})$ and **PACF (Partial Autocorrelation Function)** $\phi_{kk}$ are used to identify $p$ and $q$:

| Model | ACF Pattern | PACF Pattern |
|-------|------------|-------------|
| AR($p$) | Decays exponentially or sinusoidally | Cuts off after lag $p$ |
| MA($q$) | Cuts off after lag $q$ | Decays exponentially |
| ARMA($p$,$q$) | Decays after lag $q-p$ | Decays after lag $p-q$ |

In practice, these patterns are often ambiguous. Information criteria provide a more objective guide.

## Model Selection: AIC and BIC

The **AIC (Akaike Information Criterion)** and **BIC (Bayesian Information Criterion)** penalize model complexity:

$$\text{AIC} = -2\ln\hat{L} + 2k$$
$$\text{BIC} = -2\ln\hat{L} + k\ln(T)$$

where $\hat{L}$ is the maximized likelihood and $k = p + q + 1$ is the number of parameters. BIC penalizes complexity more heavily and tends to select more parsimonious models. The `auto.arima` function in R and `pmdarima` in Python automate this search.

## Diagnostic Checking: Ljung-Box Test

After fitting an ARIMA model, residuals $\hat{\varepsilon}_t$ should be white noise. The **Ljung-Box test** (1978) tests the joint hypothesis that the first $m$ autocorrelations of residuals are zero:

$$Q = T(T+2) \sum_{k=1}^{m} \frac{\hat{\rho}_k^2}{T-k} \sim \chi^2(m - p - q)$$

A significant Ljung-Box statistic (p-value < 0.05) indicates model misspecification — the ARIMA order is insufficient to capture all autocorrelation structure.

**Reference:** Ljung, G.M. and Box, G.E.P. (1978). "On a measure of lack of fit in time series models." *Biometrika*, 65(2), 297–303.

## SARIMA for Seasonal Series

A **SARIMA($p$,$d$,$q$)($P$,$D$,$Q$)$_s$** model extends ARIMA to handle seasonality of period $s$:

$$\Phi(L^s)\phi(L)(1-L)^d(1-L^s)^D y_t = \Theta(L^s)\theta(L)\varepsilon_t$$

where $\Phi$ and $\Theta$ are seasonal AR and MA polynomials, $D$ is the order of seasonal differencing, and $s$ is the seasonal period (e.g., $s=12$ for monthly data, $s=4$ for quarterly).

## Forecasting from ARIMA

$h$-step-ahead forecasts are computed by iterating the AR structure forward, treating future errors as zero in expectation. Forecast intervals widen with the horizon $h$ at rate $O(\sqrt{h})$ for I(0) processes.

## Key References

- Box, G.E.P. and Jenkins, G.M. (1976). *Time Series Analysis: Forecasting and Control*. Holden-Day.
- Dickey, D.A. and Fuller, W.A. (1979). *Journal of the American Statistical Association*, 74(366), 427–431.
- Said, S.E. and Dickey, D.A. (1984). *Biometrika*, 71(3), 599–607.
- Hyndman, R.J. and Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3rd ed.). OTexts. Available at: https://otexts.com/fpp3/
