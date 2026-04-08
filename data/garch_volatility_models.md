# GARCH Models and Volatility Forecasting

## Overview

GARCH (Generalized AutoRegressive Conditional Heteroskedasticity) models capture the time-varying volatility that characterizes financial returns. The key stylized facts motivating GARCH are: (1) volatility clusters — large moves tend to follow large moves; (2) returns have fat tails (leptokurtosis) relative to the normal distribution; (3) volatility is mean-reverting over the long run.

**Key References:**
- Engle, R.F. (1982). "Autoregressive conditional heteroskedasticity with estimates of the variance of United Kingdom inflation." *Econometrica*, 50(4), 987–1007.
- Bollerslev, T. (1986). "Generalized autoregressive conditional heteroskedasticity." *Journal of Econometrics*, 31(3), 307–327.

## ARCH Model (Engle, 1982)

Engle (1982) introduced the ARCH($q$) model, where the conditional variance depends on past squared returns:

$$y_t = \mu + \varepsilon_t, \quad \varepsilon_t = \sigma_t z_t, \quad z_t \sim \text{i.i.d. } N(0,1)$$
$$\sigma_t^2 = \omega + \alpha_1 \varepsilon_{t-1}^2 + \alpha_2 \varepsilon_{t-2}^2 + \cdots + \alpha_q \varepsilon_{t-q}^2$$

with $\omega > 0$ and $\alpha_i \geq 0$ for stationarity. Large past squared shocks $\varepsilon_{t-i}^2$ increase today's conditional variance $\sigma_t^2$, producing volatility clustering.

**Limitation:** High $q$ may be needed to capture persistence, leading to many parameters.

## GARCH Model (Bollerslev, 1986)

Bollerslev (1986) generalized ARCH by including lagged conditional variances:

$$\sigma_t^2 = \omega + \sum_{i=1}^q \alpha_i \varepsilon_{t-i}^2 + \sum_{j=1}^p \beta_j \sigma_{t-j}^2$$

The GARCH(1,1) model is by far the most widely used specification:
$$\sigma_t^2 = \omega + \alpha \varepsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

**Stationarity condition:** $\alpha + \beta < 1$. The degree of volatility persistence is measured by $\alpha + \beta$; values close to 1 indicate highly persistent volatility.

**Long-run variance:** $\bar{\sigma}^2 = \omega / (1 - \alpha - \beta)$, toward which the conditional variance reverts.

## Estimation

GARCH models are estimated by maximum likelihood. The log-likelihood for $T$ observations assuming normally distributed innovations is:

$$\ln L = -\frac{T}{2}\ln(2\pi) - \frac{1}{2}\sum_{t=1}^T \left[\ln \sigma_t^2 + \frac{\varepsilon_t^2}{\sigma_t^2}\right]$$

In practice, the GARCH(1,1) is estimated starting from initial value $\sigma_1^2 = \hat{\sigma}^2$ (sample variance). Non-normal error distributions (Student-$t$, GED) are frequently used to better capture fat tails.

## Asymmetric GARCH Models

Standard GARCH is symmetric: positive and negative shocks of equal magnitude have equal impact on future volatility. Financial data exhibits the **leverage effect** — negative shocks (price declines) tend to increase volatility more than positive shocks of equal size.

**GJR-GARCH (Glosten, Jagannathan, Runkle, 1993):**
$$\sigma_t^2 = \omega + (\alpha + \gamma \mathbf{1}_{\varepsilon_{t-1}<0}) \varepsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

where $\gamma > 0$ captures additional volatility impact from negative returns. This is the most popular asymmetric GARCH specification.

**EGARCH (Nelson, 1991):**
$$\ln \sigma_t^2 = \omega + \beta \ln \sigma_{t-1}^2 + \alpha \left|\frac{\varepsilon_{t-1}}{\sigma_{t-1}}\right| + \gamma \frac{\varepsilon_{t-1}}{\sigma_{t-1}}$$

EGARCH models log-variance (ensuring positivity without parameter constraints) and explicitly captures asymmetry through the $\gamma$ term. Negative $\gamma$ produces the leverage effect.

**Reference:** Nelson, D.B. (1991). "Conditional heteroskedasticity in asset returns: A new approach." *Econometrica*, 59(2), 347–370.

## Integrated GARCH (IGARCH)

When $\alpha + \beta = 1$, the GARCH process is **integrated** — shocks to variance are permanent. IGARCH arises when volatility persistence is extremely high (common in daily return data). The RiskMetrics model (J.P. Morgan, 1994) uses an IGARCH(1,1) with fixed parameters $\alpha = 0.06$, $\beta = 0.94$, no intercept.

## Realized Volatility

With high-frequency (intraday) data, **realized volatility** (RV) is computed as the sum of squared intraday returns:
$$RV_t = \sum_{j=1}^M r_{t,j}^2$$

where $r_{t,j}$ is the $j$-th intraday return on day $t$ and $M$ is the number of intraday intervals. Under mild conditions, $RV_t$ is a consistent estimator of integrated variance.

**HAR-RV model** (Corsi, 2009): Heterogeneous Autoregressive model for Realized Volatility captures long-memory in volatility by using daily, weekly, and monthly averages:
$$RV_{t+1} = \beta_0 + \beta_d RV_t + \beta_w \overline{RV}_{t-4,t} + \beta_m \overline{RV}_{t-21,t} + \varepsilon_{t+1}$$

**Reference:** Corsi, F. (2009). "A simple approximate long-memory model of realized volatility." *Journal of Financial Econometrics*, 7(2), 174–196.

## Value-at-Risk (VaR) Applications

GARCH models are widely used for risk management. The 1-day 99% VaR is:
$$\text{VaR}_{t+1}^{99\%} = \hat{\mu}_{t+1} - z_{0.01} \hat{\sigma}_{t+1}$$

where $\hat{\sigma}_{t+1}$ comes from the GARCH forecast and $z_{0.01}$ is the 1st percentile of the assumed return distribution. GARCH-VaR outperforms constant-volatility VaR, especially during high-volatility periods.

## Model Diagnostics

After fitting GARCH, check:
1. **Standardized residuals** $\hat{z}_t = \hat{\varepsilon}_t / \hat{\sigma}_t$ should be i.i.d. — test with Ljung-Box on $\hat{z}_t$ and $\hat{z}_t^2$.
2. **ARCH-LM test** on residuals — should show no remaining ARCH effects.
3. **Sign bias tests** (Engle & Ng, 1993) — detect asymmetry not captured by symmetric GARCH.

## Key References

- Engle, R.F. (1982). *Econometrica*, 50(4), 987–1007.
- Bollerslev, T. (1986). *Journal of Econometrics*, 31(3), 307–327.
- Nelson, D.B. (1991). *Econometrica*, 59(2), 347–370.
- Glosten, L.R., Jagannathan, R., and Runkle, D.E. (1993). "On the relation between expected value and the volatility of the nominal excess return on stocks." *Journal of Finance*, 48(5), 1779–1801.
- Corsi, F. (2009). *Journal of Financial Econometrics*, 7(2), 174–196.
- Andersen, T.G. and Bollerslev, T. (1998). "Answering the skeptics: Yes, standard volatility models do provide accurate forecasts." *International Economic Review*, 39(4), 885–905.
