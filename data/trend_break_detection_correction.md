# Trend Break Detection and Correction Methods

## Overview

Trend breaks — changes in the level, slope, or both of a time series trend — are among the most consequential structural changes in practice. A level shift changes the intercept of the trend; a slope break changes its growth rate; a combined break changes both simultaneously. This document surveys the key detection methods (from Perron 1989 through modern sequential tests) and correction strategies (intervention models, robust estimation, adaptive filtering).

## Types of Trend Breaks

**Level shift (additive outlier, AO):** An abrupt, permanent change in the mean level with no change in trend slope:
$$y_t = \mu_1 + \beta t + \delta \cdot \mathbf{1}[t \geq \tau] + \varepsilon_t$$
where $\delta$ is the level shift magnitude.

**Slope break (innovation outlier, IO):** A gradual change in the trend growth rate beginning at $\tau$:
$$y_t = \mu + \beta_1 t + \beta_2 (t - \tau)^+ + \varepsilon_t$$
where $(t - \tau)^+ = \max(0, t - \tau)$.

**Level + slope break:** Both intercept and slope change at $\tau$ — the most general form of a trend break. Empirically most common in economic data (e.g., post-recession recoveries, demographic transitions).

## Perron (1989): Unit Root Testing Under Structural Breaks

Perron (1989) demonstrated that standard ADF unit root tests have very low power against trend-stationary alternatives with a structural break: a stationary series with a level shift looks like a unit root process to the ADF test. He proposed modified ADF tests that allow for a **known break date** $\tau^*$ under the alternative hypothesis.

**Model A (crash model):** Level shift under $H_1$:
$$y_t = \mu + \beta t + \delta D(TB)_t + \sum_{j=1}^p c_j \Delta y_{t-j} + \varepsilon_t$$
where $D(TB)_t = 1$ if $t = \tau^* + 1$ (impulse dummy).

**Model B (changing growth):** Slope change under $H_1$:
$$y_t = \mu + \beta t + \gamma DT_t^* + \sum_{j=1}^p c_j \Delta y_{t-j} + \varepsilon_t$$
where $DT_t^* = t - \tau^*$ for $t > \tau^*$, zero otherwise.

**Model C (both):** Level + slope change under $H_1$.

**Critical values** are tabulated by Perron (1989) and depend on the break fraction $\lambda = \tau^*/T$. The test statistic is the $t$-ratio for the unit root coefficient in the augmented regression.

**Reference:** Perron, P. (1989). "The great crash, the oil price shock, and the unit root hypothesis." *Econometrica*, 57(6), 1361–1401.

## Zivot-Andrews (1992): Unknown Break Date

Perron (1989) required the break date to be **known** — typically set exogenously (e.g., 1973 oil shock). Zivot and Andrews (1992) extended the test to an **unknown break date** by estimating it endogenously as the breakpoint that most favors the trend-stationary alternative:

$$\hat{\tau} = \arg\min_{\tau} t_{\alpha}(\tau)$$

i.e., the break date that gives the smallest (most negative) $t$-statistic for the unit root null. Critical values are obtained by Monte Carlo, accounting for the search over all possible $\tau$.

**Limitation:** Tests for a single break only. Multiple breaks require sequential procedures (Bai & Perron 2003) or the Lumsdaine-Papell (1997) extension for two simultaneous breaks.

**Reference:** Zivot, E. and Andrews, D.W.K. (1992). "Further evidence on the great crash, the oil price shock, and the unit root hypothesis." *Journal of Business and Economic Statistics*, 10(3), 251–270.

## Perron-Yabu (2009): Trend Break Testing Without Unit Root Pre-Testing

A persistent problem: trend break tests must condition on whether the data is I(0) or I(1), but unit root tests have low power, especially near the boundary. Perron and Yabu (2009) propose a **quasi-feasible GLS** approach that is asymptotically valid whether or not the series has a unit root:

The test statistic $\text{Exp-W}_{\text{QF}}^{FS}$ has the same limiting distribution under both I(0) and I(1) data, eliminating the need for a preliminary unit root pre-test. This is particularly useful in practice because pre-testing distorts the size of the subsequent trend break test.

**Reference:** Perron, P. and Yabu, T. (2009). "Testing for shifts in trend with an integrated or stationary noise component." *Journal of Business and Economic Statistics*, 27(3), 369–396.

## Elliott-Müller (2006): Optimal Tests for General Trend Breaks

Elliott and Müller (2006) derive **optimal tests** (in the sense of maximizing power uniformly over break magnitudes and timing) for the null of no trend break. Their key insight: tests based on the full posterior of the break magnitude under a Gaussian prior dominate standard Wald-type tests. The resulting $q_{LL}$ and $W_{LL}$ statistics have better power against small breaks near the sample boundaries where other tests tend to fail.

**Reference:** Elliott, G. and Müller, U.K. (2006). "Efficient tests for general persistent time variation in regression coefficients." *Review of Economic Studies*, 73(4), 907–940.

## Correction Methods: What to Do After Detecting a Break

### Method 1: Dummy Variable (Intervention Analysis)

The simplest correction adds a dummy variable for the break:

```python
# Level shift at break_date
dummy_level = (df.index >= break_date).astype(int)

# Slope break (change in growth rate)
dummy_slope = np.maximum(0, (df.index - break_date).days / 365)

# ARIMA with intervention
from statsmodels.tsa.statespace.sarimax import SARIMAX
model = SARIMAX(df['y'], exog=dummy_level, order=(1,1,1)).fit()
```

**Advantage:** Simple, interpretable. **Limitation:** Assumes the break date is known and the break is instantaneous.

### Method 2: Segment-Specific Models

Fit separate models before and after the break, then combine forecasts:

```python
pre_break  = df[df.index < break_date]
post_break = df[df.index >= break_date]

model_pre  = ARIMA(pre_break['y'],  order=(1,1,1)).fit()
model_post = ARIMA(post_break['y'], order=(1,1,1)).fit()

# Forecast from post-break model only (ignore pre-break)
forecast = model_post.get_forecast(steps=12)
```

**Advantage:** Post-break model is correctly specified. **Limitation:** Wastes pre-break information; high variance if post-break sample is short.

### Method 3: Rolling Window Estimation

Use only the most recent $w$ observations for estimation, discarding data before the rolling window:

```python
w = 60  # 5 years of monthly data
recent = df['y'].iloc[-w:]
model = pm.auto_arima(recent, suppress_warnings=True).fit(recent)
```

**Advantage:** Automatically adapts to recent breaks. **Limitation:** Discards pre-break data that may still be informative; variance increases as $w$ decreases.

### Method 4: Bayesian Shrinkage (Optimal Pooling)

As in Pesaran, Pettenuzzo & Timmermann (2006), optimally weight pre- and post-break information via Bayesian hierarchical model. This achieves lower MSE than either extreme (full sample or post-break only) by estimating the bias-variance trade-off from data.

### Method 5: STL + Re-Trending

After removing seasonality via STL, re-fit a trend model to the deseasoned series with a break dummy, then add the seasonal component back for forecasting:

```python
from statsmodels.tsa.seasonal import STL
stl = STL(df['y'], period=12, robust=True).fit()
deseasoned = df['y'] - stl.seasonal

# Fit trend model with break dummy on deseasoned series
model = SARIMAX(deseasoned, exog=dummy_level, order=(1,1,0)).fit()
```

### Method 6: Adaptive/Discounted Estimation

Weight recent observations more heavily via exponential discounting. Equivalent to using a rolling window with soft edges:

$$\hat{\beta}_T = \left(\sum_{t=1}^T \lambda^{T-t} x_t x_t^\top\right)^{-1} \sum_{t=1}^T \lambda^{T-t} x_t y_t$$

where $\lambda \in (0.9, 0.99)$ is the forgetting factor. Small $\lambda$ adapts rapidly to breaks; large $\lambda$ approaches full-sample OLS. This is the **recursive least squares with forgetting** estimator, widely used in adaptive forecasting systems.

## Practical Decision Guide

```
Break detected?
├── Known break date + large post-break sample (≥50 obs)?
│   └── → Segment-specific ARIMA on post-break data
├── Known break date + small post-break sample (<50 obs)?
│   └── → Dummy variable + Bayesian shrinkage (PPT framework)
├── Unknown break date + single break suspected?
│   └── → Zivot-Andrews test → then dummy variable
├── Unknown break date + multiple breaks?
│   └── → PELT/Bai-Perron → separate models per segment
├── Gradual change (drift rather than sharp break)?
│   └── → TVP-VAR or rolling window estimation
└── Future breaks expected?
    └── → Bayesian hierarchical model (PPT 2006) or forecast combination
```

## Key References

- Perron, P. (1989). "The great crash, the oil price shock, and the unit root hypothesis." *Econometrica*, 57(6), 1361–1401.
- Zivot, E. and Andrews, D.W.K. (1992). "Further evidence on the great crash, the oil price shock, and the unit root hypothesis." *Journal of Business and Economic Statistics*, 10(3), 251–270.
- Perron, P. and Yabu, T. (2009). "Testing for shifts in trend with an integrated or stationary noise component." *Journal of Business and Economic Statistics*, 27(3), 369–396.
- Elliott, G. and Müller, U.K. (2006). "Efficient tests for general persistent time variation in regression coefficients." *Review of Economic Studies*, 73(4), 907–940.
- Pesaran, M.H., Pettenuzzo, D., and Timmermann, A. (2006). "Forecasting time series subject to multiple structural breaks." *Review of Economic Studies*, 73(4), 1057–1084.
- Bai, J. and Perron, P. (2003). "Computation and analysis of multiple structural change models." *Journal of Applied Econometrics*, 18(1), 1–22.
