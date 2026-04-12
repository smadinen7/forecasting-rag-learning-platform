# Python Code: GARCH Volatility Models

## Overview
Fitting GARCH models for volatility forecasting and Value-at-Risk (VaR) estimation using the `arch` library.

## Dependencies
```python
pip install arch pandas numpy matplotlib scipy
```

## Step 1: Prepare Return Series

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arch import arch_model

# GARCH models are fitted on returns (stationary), not prices
# If you have price data, compute log returns:
# returns = np.log(prices / prices.shift(1)).dropna() * 100  # scale by 100

# Check for volatility clustering (ARCH effects)
from statsmodels.stats.diagnostic import het_arch

def check_arch_effects(returns, lags=12):
    """Test for ARCH effects in return series (H0: no ARCH effects)."""
    lm_stat, lm_pvalue, f_stat, f_pvalue = het_arch(returns, nlags=lags)
    print(f"ARCH LM Test (lags={lags}): stat={lm_stat:.4f}, p-value={lm_pvalue:.4f}")
    if lm_pvalue < 0.05:
        print("→ ARCH effects present: GARCH model is appropriate")
    else:
        print("→ No significant ARCH effects detected")

# check_arch_effects(returns)
```

## Step 2: Fit GARCH(1,1)

```python
def fit_garch(returns, p=1, q=1, dist='normal'):
    """
    Fit GARCH(p,q) model.
    dist: 'normal', 't' (Student-t), 'skewt' (skewed-t), 'ged'
    """
    model = arch_model(
        returns,
        vol='Garch',   # GARCH volatility process
        p=p, q=q,
        dist=dist,
        mean='Constant'
    )
    result = model.fit(update_freq=5, disp='off')
    print(result.summary())
    return result

# result = fit_garch(returns, p=1, q=1, dist='t')  # Student-t for fat tails
```

## Step 3: Fit Asymmetric GARCH Models

```python
def fit_egarch(returns, p=1, q=1):
    """EGARCH — captures leverage effect (log variance, no positivity constraint)."""
    model = arch_model(returns, vol='EGARCH', p=p, q=q, dist='t')
    result = model.fit(disp='off')
    print(result.summary())
    print("\nLeverage effect (gamma < 0 means negative shocks increase vol more):")
    print(result.params.filter(like='gamma'))
    return result

def fit_gjr_garch(returns, p=1, o=1, q=1):
    """GJR-GARCH — asymmetric GARCH with indicator for negative shocks."""
    model = arch_model(returns, vol='Garch', p=p, o=o, q=q, dist='t')
    result = model.fit(disp='off')
    print(result.summary())
    return result

# result_egarch = fit_egarch(returns)
# result_gjr = fit_gjr_garch(returns)
```

## Step 4: Diagnostics

```python
def garch_diagnostics(result):
    """Check standardized residuals for remaining ARCH effects."""
    std_resid = result.resid / result.conditional_volatility
    
    # Plot
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    result.conditional_volatility.plot(ax=axes[0], title='Conditional Volatility (σ_t)')
    axes[0].set_ylabel('Volatility')
    
    std_resid.plot(ax=axes[1], title='Standardized Residuals')
    axes[1].axhline(0, color='red', linestyle='--')
    
    # Histogram of standardized residuals
    axes[2].hist(std_resid, bins=50, density=True, label='Std Residuals')
    axes[2].set_title('Distribution of Standardized Residuals')
    
    plt.tight_layout()
    plt.show()
    
    # ARCH LM test on standardized residuals (het_arch squares internally)
    print("\nARCH test on standardized residuals:")
    check_arch_effects(std_resid, lags=10)
    
    # Ljung-Box on standardized residuals
    from statsmodels.stats.diagnostic import acorr_ljungbox
    lb = acorr_ljungbox(std_resid, lags=[10, 20], return_df=True)
    print("\nLjung-Box on standardized residuals:")
    print(lb)

# garch_diagnostics(result)
```

## Step 5: Volatility Forecast

```python
def garch_forecast(result, horizon=10):
    """
    Generate h-step-ahead volatility forecasts.
    Returns annualized volatility forecasts (assuming daily data).
    """
    forecasts = result.forecast(horizon=horizon, reindex=False)
    
    # forecasts.variance contains h-step-ahead conditional variance
    # Convert to annualized volatility (daily → annual: multiply by sqrt(252))
    vol_forecast = np.sqrt(forecasts.variance.iloc[-1]) * np.sqrt(252)
    
    print(f"\n{horizon}-step-ahead annualized volatility forecast:")
    print(vol_forecast.rename('Ann. Vol (%)'))
    
    return forecasts

# forecasts = garch_forecast(result, horizon=22)  # 22 trading days = 1 month
```

## Step 6: Value-at-Risk (VaR) Estimation

```python
from scipy import stats

def compute_var(result, confidence_level=0.99):
    """
    Compute 1-day Value-at-Risk using GARCH conditional volatility.
    confidence_level: e.g., 0.99 for 99% VaR
    """
    alpha = 1 - confidence_level
    sigma_t = result.conditional_volatility  # time-varying volatility
    mu = result.params.get('mu', 0)          # conditional mean
    
    # For normal distribution
    z = stats.norm.ppf(alpha)
    VaR_normal = mu + z * sigma_t
    
    # For Student-t distribution (if fitted with dist='t')
    if hasattr(result, 'params') and 'nu' in result.params:
        nu = result.params['nu']
        z_t = stats.t.ppf(alpha, df=nu)
        VaR_t = mu + z_t * sigma_t * np.sqrt((nu - 2) / nu)
        
        print(f"\n1-day {int(confidence_level*100)}% VaR (Student-t, ν={nu:.2f}):")
        print(f"  Latest VaR: {VaR_t.iloc[-1]:.4f} (i.e., {abs(VaR_t.iloc[-1]):.2f}% loss with 1% probability)")
        return VaR_t
    
    print(f"\n1-day {int(confidence_level*100)}% VaR (Normal):")
    print(f"  Latest VaR: {VaR_normal.iloc[-1]:.4f}")
    return VaR_normal

# var = compute_var(result, confidence_level=0.99)
```

## Step 7: VaR Backtesting

```python
def backtest_var(returns, var_series, confidence_level=0.99):
    """
    Backtest VaR: count violations (actual loss exceeds VaR).
    Expected violation rate = 1 - confidence_level.
    """
    violations = returns < var_series
    violation_rate = violations.mean()
    expected_rate = 1 - confidence_level
    
    print(f"Expected violation rate: {expected_rate:.2%}")
    print(f"Actual violation rate:   {violation_rate:.2%}")
    print(f"Number of violations:    {violations.sum()} out of {len(returns)}")
    
    if violation_rate < expected_rate * 0.5:
        print("⚠ VaR may be too conservative (over-estimates risk)")
    elif violation_rate > expected_rate * 1.5:
        print("⚠ VaR underestimates risk — model needs recalibration")
    else:
        print("✓ VaR backtesting passed")
    
    return violation_rate

# backtest_var(returns, var)
```

## Model Comparison: AIC/BIC

```python
def compare_garch_models(returns):
    """Compare GARCH, EGARCH, GJR-GARCH by AIC/BIC."""
    models = {
        'GARCH(1,1)-Normal': arch_model(returns, vol='Garch', p=1, q=1, dist='normal'),
        'GARCH(1,1)-t':      arch_model(returns, vol='Garch', p=1, q=1, dist='t'),
        'EGARCH(1,1)-t':     arch_model(returns, vol='EGARCH', p=1, q=1, dist='t'),
        'GJR-GARCH(1,1)-t':  arch_model(returns, vol='Garch', p=1, o=1, q=1, dist='t'),
    }
    
    results = {}
    for name, model in models.items():
        try:
            fit = model.fit(disp='off')
            results[name] = {'AIC': fit.aic, 'BIC': fit.bic, 'LogLik': fit.loglikelihood}
        except Exception as e:
            results[name] = {'AIC': np.nan, 'BIC': np.nan, 'LogLik': np.nan}
    
    df = pd.DataFrame(results).T.sort_values('AIC')
    print("\nModel Comparison (lower AIC/BIC is better):")
    print(df.round(2))
    return df

# compare_garch_models(returns)
```

## Quick Start: Full Pipeline

```python
# --- Minimal working example ---
import pandas as pd
import numpy as np
from arch import arch_model

# Simulate daily returns
np.random.seed(42)
returns = pd.Series(np.random.normal(0, 1, 1000) * np.exp(0.1 * np.cumsum(np.random.randn(1000))))

# Fit GARCH(1,1) with Student-t innovations
model = arch_model(returns, vol='Garch', p=1, q=1, dist='t')
result = model.fit(disp='off')

# 10-day volatility forecast
forecast = result.forecast(horizon=10, reindex=False)
print("10-day conditional variance forecast:")
print(forecast.variance.iloc[-1])

# Persistence: alpha + beta (close to 1 = high persistence)
alpha = result.params['alpha[1]']
beta  = result.params['beta[1]']
print(f"\nVolatility persistence (alpha+beta): {alpha+beta:.4f}")
```

## When to Use Which GARCH Model

| Situation | Model |
|-----------|-------|
| Symmetric volatility, large sample | GARCH(1,1) |
| Fat-tailed returns | GARCH(1,1) with Student-t dist |
| Leverage effect suspected (equity) | GJR-GARCH or EGARCH |
| Need log-variance (no constraints) | EGARCH |
| Long memory in volatility | FIGARCH |
| High-frequency data | HAR-RV on realized volatility |
