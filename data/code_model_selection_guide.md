# Time Series Model Selection Guide: Recommendations + Python Code

## How to Choose the Right Model

Use this decision framework: characterize your data, then pick the model. Each section includes starter Python code.

---

## Step 1: Characterize Your Data

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, kpss, acf, pacf
from statsmodels.tsa.seasonal import seasonal_decompose

def characterize_series(series, freq=None):
    """
    Quick diagnostic suite to characterize a time series.
    Outputs: stationarity, trend, seasonality, volatility clustering, length.
    """
    n = len(series)
    print(f"=== Series Diagnostics ===")
    print(f"Length: {n} observations")
    print(f"Missing values: {series.isna().sum()}")
    
    # Stationarity
    adf_p = adfuller(series.dropna(), autolag='AIC')[1]
    kpss_p = kpss(series.dropna(), regression='c', nlags='auto')[1]
    stationary = (adf_p < 0.05) and (kpss_p > 0.05)
    print(f"\nStationarity: {'✓ Stationary' if stationary else '✗ Non-stationary'}")
    print(f"  ADF p={adf_p:.3f} (reject unit root if <0.05)")
    print(f"  KPSS p={kpss_p:.3f} (reject stationarity if <0.05)")
    
    # Trend (simple linear fit)
    t = np.arange(n)
    slope = np.polyfit(t, series.fillna(method='ffill'), 1)[0]
    rel_slope = abs(slope) / abs(series.mean()) * n
    print(f"\nTrend: {'Strong' if rel_slope > 0.1 else 'Weak/None'} (relative slope={rel_slope:.3f})")
    
    # Seasonality (if frequency given)
    if freq:
        decomp = seasonal_decompose(series.dropna(), model='additive', period=freq)
        seasonal_strength = 1 - decomp.resid.var() / (decomp.seasonal + decomp.resid).var()
        print(f"\nSeasonality (period={freq}): strength={seasonal_strength:.3f} "
              f"({'Strong' if seasonal_strength > 0.6 else 'Weak'})")
    
    # Volatility clustering (ARCH test)
    from statsmodels.stats.diagnostic import het_arch
    _, arch_p, _, _ = het_arch(series.dropna(), nlags=12)
    print(f"\nVolatility clustering (ARCH): {'✓ Present' if arch_p < 0.05 else '✗ Absent'} (p={arch_p:.3f})")
    
    print(f"\n=== Recommendation ===")
    _recommend(n, stationary, rel_slope, freq, arch_p, kpss_p)

def _recommend(n, stationary, trend_strength, seasonal_period, arch_p, kpss_p):
    has_trend = trend_strength > 0.1
    has_season = seasonal_period is not None
    has_vol_clust = arch_p < 0.05
    
    if n < 50:
        print("⚠ Very short series (<50 obs): use simple models only")
        print("→ RECOMMENDED: ETS (auto) or simple exponential smoothing")
        return
    
    if has_vol_clust:
        print("→ Volatility clustering detected")
        print("  RECOMMENDED: ARIMA for mean + GARCH for variance")
        print("  See: code_garch_models.md")
    
    if has_season and has_trend:
        print("→ Seasonal series with trend")
        print("  RECOMMENDED: SARIMA or Prophet or Holt-Winters (ETS)")
        print("  See: code_arima_sarima.md, code_stl_prophet.md")
    elif has_season:
        print("→ Seasonal series, no strong trend")
        print("  RECOMMENDED: SARIMA or STL + ARIMA")
        print("  See: code_arima_sarima.md, code_stl_prophet.md")
    elif has_trend and not stationary:
        print("→ Trending, non-stationary series")
        print("  RECOMMENDED: ARIMA(p,1,q) — fit on first differences")
        print("  See: code_arima_sarima.md")
    elif stationary:
        print("→ Stationary series, no trend or seasonality")
        print("  RECOMMENDED: ARMA(p,q) or ETS(A,N,N)")
    else:
        print("→ Complex structure — consider structural break first")
        print("  RECOMMENDED: check for breaks with ruptures, then model per segment")
        print("  See: code_structural_break_detection.md")

# characterize_series(df['value'], freq=12)
```

---

## Decision Tree: Which Model?

```
Is the series univariate or multivariate?
├── Univariate:
│   ├── Stationary?
│   │   ├── Yes → ARMA(p,q)
│   │   └── No → Difference → ARIMA(p,d,q)
│   ├── Seasonal?
│   │   ├── Stable seasonality → SARIMA or Holt-Winters
│   │   ├── Changing seasonality → Prophet or STL-ARIMA
│   │   └── Multiple seasonalities → Prophet (add_seasonality)
│   ├── Volatility clustering?
│   │   └── Yes → ARIMA mean + GARCH variance
│   ├── Structural breaks?
│   │   ├── Known break → ARIMAX with intervention dummy
│   │   └── Unknown breaks → ruptures PELT → fit per segment
│   ├── Long horizon (>100 steps)?
│   │   └── Neural: N-BEATS, PatchTST (if enough data)
│   └── Short series (<100 obs)?
│       └── ETS (ETSModel with auto-selection in statsmodels)
└── Multivariate:
    ├── All stationary → VAR(p)
    ├── Cointegrated → VECM
    ├── Regime changes → MS-VAR (Markov switching VAR)
    └── High-dimensional, large data → iTransformer, TFT
```

---

## Scenario Recipes

### Scenario A: Monthly Sales with Trend + Seasonality + Level Shift

```python
# Problem: monthly sales data, clear annual seasonality,
# suspected level shift in 2022 (e.g., post-COVID recovery)

import ruptures as rpt
from statsmodels.tsa.statespace.sarimax import SARIMAX
import statsmodels.api as sm

def model_sales_with_break(series, break_date, period=12):
    """
    SARIMA with intervention dummy for a known/detected break.
    """
    # Step 1: Create intervention dummy
    dummy = (series.index >= pd.Timestamp(break_date)).astype(int)
    
    # Step 2: Fit SARIMAX with intervention as exogenous variable
    model = SARIMAX(
        series,
        exog=dummy,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, period),
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    result = model.fit(disp=False)
    print(result.summary())
    
    # Step 3: Forecast — need to provide future dummy values
    future_dummy = np.ones(24)  # post-break regime continues
    forecast = result.get_forecast(steps=24, exog=future_dummy)
    
    return result, forecast

# result, forecast = model_sales_with_break(df['value'], '2022-01-01')
```

### Scenario B: Financial Returns — ARIMA-GARCH

```python
def arima_garch_pipeline(returns):
    """
    Two-step ARIMA-GARCH: model mean with ARIMA, residual variance with GARCH.
    """
    from statsmodels.tsa.arima.model import ARIMA
    from arch import arch_model
    
    # Step 1: Fit ARIMA to returns
    arima = ARIMA(returns, order=(1, 0, 1)).fit()
    
    # Step 2: Fit GARCH on ARIMA residuals
    resid = arima.resid
    garch = arch_model(resid, vol='Garch', p=1, q=1, dist='t').fit(disp='off')
    
    # Combined 1-day VaR
    sigma_next = np.sqrt(garch.forecast(horizon=1, reindex=False).variance.iloc[-1, 0])
    mu_next = arima.forecast(steps=1).iloc[0]
    
    from scipy import stats
    nu = garch.params['nu']
    z = stats.t.ppf(0.01, df=nu)
    VaR_99 = mu_next + z * sigma_next * np.sqrt((nu-2)/nu)
    
    print(f"1-day 99% VaR: {VaR_99:.4f} ({abs(VaR_99):.2f}% potential loss)")
    return arima, garch, VaR_99

# arima_fit, garch_fit, var = arima_garch_pipeline(returns)
```

### Scenario C: Multiple Series — Forecast Combination

```python
def ensemble_forecast(series, horizon=12, period=12):
    """
    Combine ETS, ARIMA, and STL-ARIMA forecasts via simple averaging.
    Consistently outperforms any individual model.
    """
    import pmdarima as pm
    from statsmodels.tsa.exponential_smoothing.ets import ETSModel
    from statsmodels.tsa.forecasting.stl import STLForecast
    from statsmodels.tsa.arima.model import ARIMA
    
    forecasts = {}
    
    # ETS (auto)
    try:
        ets = ETSModel(series, error='add', trend='add', seasonal='add',
                       damped_trend=True, seasonal_periods=period).fit(disp=False)
        forecasts['ETS'] = ets.forecast(horizon)
    except Exception as e:
        print(f"ETS failed: {e}")
    
    # Auto ARIMA — align index with ETS/STL-ARIMA forecasts
    try:
        arima = pm.auto_arima(series, seasonal=True, m=period,
                              suppress_warnings=True, error_action='ignore')
        # Build a forecast index consistent with the other methods
        last_idx = series.index[-1]
        if isinstance(series.index, pd.DatetimeIndex):
            freq = pd.infer_freq(series.index)
            fc_index = pd.date_range(start=last_idx, periods=horizon + 1, freq=freq)[1:]
        else:
            fc_index = range(len(series), len(series) + horizon)
        forecasts['ARIMA'] = pd.Series(arima.predict(n_periods=horizon), index=fc_index)
    except Exception as e:
        print(f"ARIMA failed: {e}")
    
    # STL-ARIMA
    try:
        stlf = STLForecast(series, ARIMA, model_kwargs={"order": (1,1,1)},
                           period=period).fit(disp=False)
        forecasts['STL-ARIMA'] = stlf.forecast(horizon)
    except Exception as e:
        print(f"STL-ARIMA failed: {e}")
    
    if not forecasts:
        raise ValueError("All models failed")

    # Normalise all forecasts to a common RangeIndex before combining
    # to avoid NaN misalignment when indices differ across models
    df_fc = pd.DataFrame(
        {k: v.values for k, v in forecasts.items()},
        index=next(iter(forecasts.values())).index
    )
    ensemble = df_fc.mean(axis=1)
    
    print(f"\nEnsemble of {len(forecasts)} model(s): {list(forecasts.keys())}")
    print("Simple averaging — add inverse-MSE weighting if you have a validation set")
    
    return ensemble, df_fc

# ensemble, components = ensemble_forecast(df['value'], horizon=24, period=12)
```

### Scenario D: Detecting + Modeling Regime Changes

```python
def regime_aware_forecast(series, horizon=12, period=None):
    """
    1. Detect change points with PELT
    2. Fit model on most recent segment
    3. Forecast forward
    """
    import ruptures as rpt
    
    signal = series.values.reshape(-1, 1)
    algo = rpt.Pelt(model="normal", min_size=max(5, len(series)//20)).fit(signal)
    bkps = algo.predict(pen=np.log(len(series)) * 2)  # BIC-like penalty
    
    # Most recent segment
    last_break = bkps[-2] if len(bkps) > 1 else 0
    recent_segment = series.iloc[last_break:]
    
    print(f"Total breaks found: {len(bkps)-1}")
    print(f"Most recent segment: {len(recent_segment)} observations "
          f"({series.index[last_break] if hasattr(series.index[0], 'date') else last_break} onward)")
    
    # Fit ARIMA on recent segment
    import pmdarima as pm
    model = pm.auto_arima(recent_segment, seasonal=period is not None,
                          m=period or 1, suppress_warnings=True, error_action='ignore')
    forecast = model.predict(n_periods=horizon)
    
    print(f"Model fitted on recent segment: {model.order}")
    return forecast, last_break

# forecast, break_idx = regime_aware_forecast(df['value'], horizon=24, period=12)
```

---

## Quick Reference: Library Lookup

| Method | Library | Install |
|--------|---------|---------|
| ARIMA, SARIMA, SARIMAX | `statsmodels` | `pip install statsmodels` |
| Auto-ARIMA | `pmdarima` | `pip install pmdarima` |
| ETS / Holt-Winters | `statsmodels` | included |
| GARCH, EGARCH, GJR | `arch` | `pip install arch` |
| Markov switching | `statsmodels` | included |
| Change points | `ruptures` | `pip install ruptures` |
| STL, STL-ARIMA | `statsmodels` | included |
| Prophet | `prophet` | `pip install prophet` |
| VAR, VECM | `statsmodels` | included |
| N-BEATS, TFT | `neuralforecast` | `pip install neuralforecast` |
| PatchTST, iTransformer | `neuralforecast` or `pytorch-forecasting` | see docs |
| Forecast combination | custom or `mlforecast` | `pip install mlforecast` |
