# Python Code: ARIMA and SARIMA Forecasting

## Overview
Complete workflow for fitting ARIMA and SARIMA models in Python using `statsmodels` and `pmdarima`. Covers identification, fitting, diagnostics, and forecasting.

## Dependencies
```python
pip install statsmodels pmdarima pandas numpy matplotlib
```

## Step 1: Check Stationarity

```python
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss
import matplotlib.pyplot as plt

def check_stationarity(series, name="Series"):
    """Run ADF and KPSS tests and print results."""
    # ADF test (H0: unit root / non-stationary)
    adf_result = adfuller(series.dropna(), autolag='AIC')
    print(f"\n=== {name} ===")
    print(f"ADF Statistic: {adf_result[0]:.4f}")
    print(f"ADF p-value:   {adf_result[1]:.4f}")
    print(f"ADF Verdict:   {'Stationary' if adf_result[1] < 0.05 else 'Non-stationary'}")

    # KPSS test (H0: stationary)
    kpss_result = kpss(series.dropna(), regression='c', nlags='auto')
    print(f"KPSS Statistic: {kpss_result[0]:.4f}")
    print(f"KPSS p-value:   {kpss_result[1]:.4f}")
    print(f"KPSS Verdict:   {'Stationary' if kpss_result[1] > 0.05 else 'Non-stationary'}")

# Example usage
# check_stationarity(df['value'])
# check_stationarity(df['value'].diff().dropna(), name="First Difference")
```

## Step 2: Plot ACF and PACF

```python
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

def plot_acf_pacf(series, lags=40):
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    plot_acf(series.dropna(), lags=lags, ax=axes[0], title='ACF')
    plot_pacf(series.dropna(), lags=lags, ax=axes[1], title='PACF')
    plt.tight_layout()
    plt.show()

# ACF cuts off at lag q → MA(q)
# PACF cuts off at lag p → AR(p)
# Both decay → ARMA(p, q)
```

## Step 3a: Fit ARIMA Manually

```python
from statsmodels.tsa.arima.model import ARIMA

def fit_arima(series, order=(1, 1, 1)):
    """Fit ARIMA(p,d,q) model."""
    model = ARIMA(series, order=order)
    result = model.fit()
    print(result.summary())
    return result

# Example: ARIMA(1,1,1)
# result = fit_arima(df['value'], order=(1, 1, 1))
```

## Step 3b: Auto-ARIMA (Automatic Order Selection)

```python
import pmdarima as pm

def auto_arima_fit(series, seasonal=False, m=1):
    """
    Automatically select ARIMA order via AIC minimization.
    seasonal: True for SARIMA
    m: seasonal period (12=monthly, 4=quarterly, 7=weekly)
    """
    model = pm.auto_arima(
        series,
        start_p=0, max_p=5,
        start_q=0, max_q=5,
        d=None,              # auto-select differencing order
        seasonal=seasonal,
        m=m,
        information_criterion='aic',
        stepwise=True,       # faster than exhaustive search
        error_action='ignore',
        suppress_warnings=True,
        trace=True           # print search progress
    )
    print(model.summary())
    return model

# Automatic ARIMA
# model = auto_arima_fit(df['value'])

# Automatic SARIMA (monthly data)
# model = auto_arima_fit(df['value'], seasonal=True, m=12)
```

## Step 4: Diagnostics

```python
from statsmodels.stats.diagnostic import acorr_ljungbox

def run_diagnostics(result):
    """Check residuals for white noise."""
    residuals = result.resid

    # Plot residuals
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    residuals.plot(ax=axes[0, 0], title='Residuals')
    residuals.plot(kind='hist', ax=axes[0, 1], title='Residual Distribution')
    plot_acf(residuals, lags=40, ax=axes[1, 0], title='ACF of Residuals')
    plot_pacf(residuals, lags=40, ax=axes[1, 1], title='PACF of Residuals')
    plt.tight_layout()
    plt.show()

    # Ljung-Box test (H0: residuals are white noise)
    lb_test = acorr_ljungbox(residuals, lags=[10, 20], return_df=True)
    print("\nLjung-Box Test:")
    print(lb_test)
    print("Verdict: residuals are white noise" if (lb_test['lb_pvalue'] > 0.05).all()
          else "WARNING: residual autocorrelation remains — increase model order")

# run_diagnostics(result)
```

## Step 5: Forecast

```python
def forecast_arima(result, steps=12, alpha=0.05):
    """
    Generate h-step forecasts with confidence intervals.
    alpha: significance level (0.05 = 95% CI)
    """
    forecast = result.get_forecast(steps=steps)
    mean_forecast = forecast.predicted_mean
    conf_int = forecast.conf_int(alpha=alpha)

    # Plot
    plt.figure(figsize=(12, 5))
    plt.plot(result.model.endog, label='Historical')
    plt.plot(mean_forecast, label='Forecast', color='red')
    plt.fill_between(
        conf_int.index,
        conf_int.iloc[:, 0],
        conf_int.iloc[:, 1],
        alpha=0.3, color='red', label=f'{int((1-alpha)*100)}% CI'
    )
    plt.legend()
    plt.title('ARIMA Forecast')
    plt.show()

    return mean_forecast, conf_int

# forecast, ci = forecast_arima(result, steps=24)
```

## Step 6: SARIMA Example (Full Pipeline)

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX

def fit_sarima(series, order=(1,1,1), seasonal_order=(1,1,1,12)):
    """
    Fit SARIMA(p,d,q)(P,D,Q,s) model.
    seasonal_order = (P, D, Q, s) where s is seasonal period.
    """
    model = SARIMAX(
        series,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    result = model.fit(disp=False)
    print(result.summary())
    return result

# Monthly data with annual seasonality
# result = fit_sarima(df['value'],
#                     order=(1, 1, 1),
#                     seasonal_order=(1, 1, 1, 12))
```

## Model Selection via AIC/BIC Grid Search

```python
import itertools
import warnings

def arima_grid_search(series, p_range=range(3), d_range=range(2), q_range=range(3)):
    """Search over ARIMA orders and return AIC table."""
    best_aic = np.inf
    best_order = None
    results = []

    for p, d, q in itertools.product(p_range, d_range, q_range):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = ARIMA(series, order=(p, d, q)).fit()
                results.append({'order': (p,d,q), 'AIC': model.aic, 'BIC': model.bic})
                if model.aic < best_aic:
                    best_aic = model.aic
                    best_order = (p, d, q)
        except Exception:
            pass

    results_df = pd.DataFrame(results).sort_values('AIC')
    print(f"Best ARIMA order by AIC: {best_order} (AIC={best_aic:.2f})")
    return results_df

# table = arima_grid_search(df['value'])
# print(table.head(10))
```

## When to Use ARIMA vs. SARIMA

| Data Characteristics | Model |
|---------------------|-------|
| Stationary, no trend, no seasonality | ARMA(p,q) |
| Non-stationary (unit root), no seasonality | ARIMA(p,1,q) |
| Seasonal pattern, stationary | SARMA |
| Seasonal pattern + trend | SARIMA(p,d,q)(P,D,Q,s) |
| Unknown order | auto_arima() with AIC search |

**Rule of thumb:** Start with auto_arima, inspect the chosen order, verify with Ljung-Box, then forecast.
