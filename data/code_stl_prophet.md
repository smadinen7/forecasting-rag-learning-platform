# Python Code: STL Decomposition and Prophet Forecasting

## Overview
STL (Seasonal-Trend decomposition using LOESS) isolates trend, seasonality, and residuals. Prophet builds on additive decomposition with automatic changepoint detection. Both are excellent for business time series with seasonality and regime shifts.

## Dependencies
```python
pip install statsmodels prophet pandas numpy matplotlib
```

## Part A: STL Decomposition

### Step 1: Fit STL

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL, DecomposeResult

def fit_stl(series, period, seasonal=7, robust=True):
    """
    Fit STL decomposition.
    
    period:   seasonal period (12=monthly annual cycle, 7=daily weekly cycle)
    seasonal: length of seasonal smoother (must be odd, ≥ 7)
              larger → smoother seasonal component
    robust:   True = robust to outliers (uses iterative reweighting)
    
    Returns STL result with .trend, .seasonal, .resid attributes.
    """
    stl = STL(series, period=period, seasonal=seasonal, robust=robust)
    result = stl.fit()
    
    # Plot decomposition
    fig = result.plot()
    fig.set_size_inches(14, 8)
    plt.suptitle('STL Decomposition', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.show()
    
    # Seasonal strength
    var_resid = result.resid.var()
    var_detrended = (result.seasonal + result.resid).var()
    seasonal_strength = max(0, 1 - var_resid / var_detrended)
    
    # Trend strength
    var_deseasoned = (result.trend + result.resid).var()
    trend_strength = max(0, 1 - var_resid / var_deseasoned)
    
    print(f"Seasonal strength: {seasonal_strength:.3f} (>0.6 = strong seasonality)")
    print(f"Trend strength:    {trend_strength:.3f} (>0.6 = strong trend)")
    
    return result

# result = fit_stl(df['value'], period=12)  # annual seasonality in monthly data
# result = fit_stl(df['value'], period=7)   # weekly seasonality in daily data
```

### Step 2: STL + ARIMA Forecasting (STL-ARIMA)

```python
from statsmodels.tsa.forecasting.stl import STLForecast
from statsmodels.tsa.arima.model import ARIMA

def stl_arima_forecast(series, period, horizon=12, arima_order=(1, 1, 0)):
    """
    STL-ARIMA: decompose with STL, forecast trend+residual with ARIMA,
    re-add seasonal component.
    
    This handles seasonal series without needing SARIMA,
    and adapts better to changing seasonal patterns.
    """
    stlf = STLForecast(
        series,
        ARIMA,
        model_kwargs={"order": arima_order, "trend": "t"},
        period=period
    )
    result = stlf.fit(disp=False)
    forecast = result.forecast(horizon)
    
    # Plot
    plt.figure(figsize=(14, 5))
    plt.plot(series, label='Historical')
    plt.plot(forecast, label='Forecast', color='red')
    plt.legend()
    plt.title('STL-ARIMA Forecast')
    plt.show()
    
    return forecast

# forecast = stl_arima_forecast(df['value'], period=12, horizon=24)
```

### Step 3: Seasonally Adjusted Series

```python
def seasonal_adjustment(series, period):
    """Remove seasonal component to get seasonally adjusted series."""
    stl = STL(series, period=period, robust=True)
    result = stl.fit()
    
    seasonally_adjusted = series - result.seasonal
    
    plt.figure(figsize=(14, 5))
    plt.plot(series, label='Original', alpha=0.7)
    plt.plot(seasonally_adjusted, label='Seasonally Adjusted', linewidth=1.5)
    plt.legend()
    plt.title('Seasonally Adjusted Series')
    plt.show()
    
    return seasonally_adjusted

# sa = seasonal_adjustment(df['value'], period=12)
```

---

## Part B: Prophet Forecasting

### Step 1: Prepare Data for Prophet

```python
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from prophet.plot import plot_cross_validation_metric

def prepare_prophet_df(series, date_col=None, value_col=None):
    """
    Prophet requires a DataFrame with columns 'ds' (dates) and 'y' (values).
    """
    if isinstance(series, pd.Series):
        df = series.reset_index()
        df.columns = ['ds', 'y']
    else:
        df = series[[date_col, value_col]].rename(
            columns={date_col: 'ds', value_col: 'y'})
    
    df['ds'] = pd.to_datetime(df['ds'])
    return df

# prophet_df = prepare_prophet_df(df['value'])
```

### Step 2: Fit Prophet with Automatic Changepoints

```python
def fit_prophet(df, changepoint_prior_scale=0.05,
                seasonality_mode='additive',
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False):
    """
    Fit Prophet model.
    
    changepoint_prior_scale: flexibility of changepoints
        0.05 (default) = conservative — few trend changes
        0.5            = flexible — adapts rapidly to trend changes
        0.001          = rigid — almost no trend changes
    
    seasonality_mode: 'additive' or 'multiplicative'
        Use multiplicative when seasonal amplitude grows with the level.
    """
    model = Prophet(
        changepoint_prior_scale=changepoint_prior_scale,
        seasonality_mode=seasonality_mode,
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
        interval_width=0.95  # 95% prediction intervals
    )
    model.fit(df)
    return model

# model = fit_prophet(prophet_df, changepoint_prior_scale=0.1, seasonality_mode='multiplicative')
```

### Step 3: Generate Forecast

```python
def prophet_forecast(model, periods=365, freq='D'):
    """
    Generate forecast for specified future periods.
    freq: 'D'=daily, 'W'=weekly, 'M'=monthly, 'Q'=quarterly
    """
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    
    # Plot forecast components
    fig1 = model.plot(forecast)
    fig1.set_size_inches(14, 6)
    plt.title('Prophet Forecast')
    plt.show()
    
    fig2 = model.plot_components(forecast)
    fig2.set_size_inches(14, 10)
    plt.tight_layout()
    plt.show()
    
    return forecast

# forecast = prophet_forecast(model, periods=365, freq='D')
```

### Step 4: Inspect Detected Changepoints

```python
from prophet.plot import add_changepoints_to_plot

def inspect_changepoints(model, forecast, threshold=0.01):
    """
    Show where Prophet detected trend changepoints.
    threshold: minimum absolute change in trend slope to report.
    """
    fig = model.plot(forecast)
    a = add_changepoints_to_plot(fig.gca(), model, forecast)
    plt.title('Detected Changepoints')
    plt.show()
    
    # Print significant changepoints
    deltas = model.params['delta'].mean(axis=0)
    changepoints = model.changepoints
    sig = pd.Series(deltas, index=changepoints)
    sig = sig[abs(sig) > threshold].sort_values(key=abs, ascending=False)
    
    print("\nSignificant changepoints (trend slope changes):")
    for date, delta in sig.items():
        direction = "↑" if delta > 0 else "↓"
        print(f"  {date.date()}: {direction} slope change = {delta:.4f}")
    
    return sig

# sig_cp = inspect_changepoints(model, forecast)
```

### Step 5: Cross-Validation and Performance

```python
def prophet_cv(model, initial='365 days', period='90 days', horizon='180 days'):
    """
    Prophet built-in cross-validation.
    initial: training period for first fold
    period:  spacing between cutoff dates
    horizon: forecast horizon to evaluate
    """
    df_cv = cross_validation(
        model,
        initial=initial,
        period=period,
        horizon=horizon,
        parallel='processes'
    )
    
    metrics = performance_metrics(df_cv)
    print("\nCross-Validation Metrics:")
    print(metrics[['horizon', 'mse', 'rmse', 'mae', 'mape', 'coverage']].to_string(index=False))
    
    # Plot RMSE over horizon
    fig = plot_cross_validation_metric(df_cv, metric='rmse')
    plt.title('RMSE by Forecast Horizon')
    plt.show()
    
    return df_cv, metrics

# df_cv, metrics = prophet_cv(model, initial='2 years', period='6 months', horizon='1 year')
```

### Step 6: Adding Custom Regressors and Holidays

```python
def fit_prophet_with_regressors(df, extra_regressors=None, country_holidays='US'):
    """
    Prophet with country holidays and optional extra regressors.
    extra_regressors: list of column names in df to include as features
    """
    model = Prophet(
        changepoint_prior_scale=0.05,
        seasonality_mode='additive',
        yearly_seasonality=True,
        weekly_seasonality=True,
        interval_width=0.95
    )
    
    # Add country holidays
    if country_holidays:
        model.add_country_holidays(country_name=country_holidays)
    
    # Add extra regressors (must be present in future df too)
    if extra_regressors:
        for reg in extra_regressors:
            model.add_regressor(reg)
    
    model.fit(df)
    return model

# model = fit_prophet_with_regressors(
#     prophet_df,
#     extra_regressors=['promo_flag', 'price_index'],
#     country_holidays='US'
# )
```

## When to Use STL vs. Prophet

| Scenario | Recommendation |
|----------|---------------|
| Pure decomposition / seasonal adjustment | STL |
| Forecasting: stable seasonality + clear trend | STL-ARIMA |
| Forecasting: multiple seasonalities, holidays | Prophet |
| Changepoint detection in trend | Prophet (automatic) |
| Need confidence intervals with missing data | Prophet |
| Very long series (>10K points) | STL (Prophet can be slow) |
| Interpretable components for stakeholders | Prophet (component plots) |
