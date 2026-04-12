# Python Code: Structural Break Detection

## Overview
Detecting structural breaks using `ruptures` (PELT, Binary Segmentation), `statsmodels` (Chow test, CUSUM), and the Bai-Perron framework.

## Dependencies
```python
pip install ruptures statsmodels pandas numpy matplotlib scipy
```

## Method 1: PELT with ruptures (Recommended for Multiple Breaks)

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ruptures as rpt

def detect_breaks_pelt(series, model="rbf", penalty=10, min_size=5):
    """
    Detect change points using PELT algorithm.
    
    model: cost function
        "l2"     — detects mean shifts (L2 norm)
        "normal" — detects mean + variance shifts (normal likelihood)
        "rbf"    — non-parametric kernel, detects any distributional shift
        "ar"     — detects changes in AR coefficients
    penalty: controls number of breaks (higher → fewer breaks)
    min_size: minimum segment length in observations
    """
    signal = series.values if isinstance(series, pd.Series) else series
    
    algo = rpt.Pelt(model=model, min_size=min_size, jump=1).fit(signal)
    breakpoints = algo.predict(pen=penalty)
    
    # Convert indices to dates if series has DatetimeIndex
    if isinstance(series, pd.Series) and isinstance(series.index, pd.DatetimeIndex):
        break_dates = [series.index[bp - 1] for bp in breakpoints[:-1]]
        print(f"Detected {len(break_dates)} break(s) at: {break_dates}")
    else:
        print(f"Detected {len(breakpoints)-1} break(s) at indices: {breakpoints[:-1]}")
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(series.values if isinstance(series, pd.Series) else series, label='Series')
    for bp in breakpoints[:-1]:
        ax.axvline(bp, color='red', linestyle='--', label='Break')
    ax.set_title(f'PELT Break Detection (model={model}, penalty={penalty})')
    ax.legend()
    plt.show()
    
    return breakpoints

# Example
# breaks = detect_breaks_pelt(df['value'], model='normal', penalty=15)
```

## Tuning the Penalty (Elbow Method)

```python
def select_penalty_elbow(series, model="rbf", min_size=5, n_bkps_max=10):
    """
    Plot cost vs. number of breakpoints to identify the elbow.
    The elbow is where adding more breaks gives diminishing cost reduction.
    """
    signal = series.values if isinstance(series, pd.Series) else series
    algo = rpt.Pelt(model=model, min_size=min_size).fit(signal)
    
    costs = []
    for n in range(1, n_bkps_max + 1):
        bkps = rpt.Binseg(model=model).fit_predict(signal, n_bkps=n)
        cost = rpt.costs.cost_factory(model=model)(signal)
        # Use Binseg to compute cost at each n
        costs.append((n, sum(cost(signal[s:e]) for s, e in
                             rpt.utils.pairwise([0] + bkps))))
    
    ns, cs = zip(*costs)
    plt.figure(figsize=(8, 4))
    plt.plot(ns, cs, 'o-')
    plt.xlabel('Number of breakpoints')
    plt.ylabel('Total cost')
    plt.title('Elbow method for penalty selection')
    plt.grid(True)
    plt.show()

# select_penalty_elbow(df['value'])
```

## Method 2: Chow Test (Single Known Break)

```python
from scipy import stats

def chow_test(series, break_date):
    """
    Chow test for parameter stability at a known break point.
    Tests H0: no structural break at break_date.
    
    series: pd.Series with DatetimeIndex
    break_date: date to test (string or Timestamp)
    """
    break_date = pd.Timestamp(break_date)
    y1 = series[series.index <= break_date].values
    y2 = series[series.index > break_date].values
    y  = series.values
    n1, n2, n = len(y1), len(y2), len(y)
    
    # RSS for full and split samples (simple mean model)
    rss_full = np.sum((y  - y.mean()) ** 2)
    rss1     = np.sum((y1 - y1.mean()) ** 2)
    rss2     = np.sum((y2 - y2.mean()) ** 2)
    rss_split = rss1 + rss2
    
    k = 2  # number of parameters (mean + variance)
    F = ((rss_full - rss_split) / k) / (rss_split / (n - 2*k))
    p_value = 1 - stats.f.cdf(F, dfn=k, dfd=n - 2*k)
    
    print(f"Chow Test at {break_date.date()}:")
    print(f"  F-statistic: {F:.4f}")
    print(f"  p-value:     {p_value:.4f}")
    print(f"  Result: {'Break detected (reject H0)' if p_value < 0.05 else 'No break (fail to reject H0)'}")
    return F, p_value

# chow_test(df['value'], '2020-03-01')
```

## Method 3: CUSUM Test (Recursive)

```python
from statsmodels.stats.diagnostic import breaks_cusumolsresid
from statsmodels.regression.linear_model import OLS
import statsmodels.api as sm

def cusum_test(series):
    """
    CUSUM test on OLS residuals from a simple trend regression.
    Tests for parameter instability over time.
    H0: parameters are stable.
    """
    # Fit simple linear trend
    t = np.arange(len(series))
    X = sm.add_constant(t)
    model = OLS(series.values, X).fit()
    
    # CUSUM of recursive residuals
    from statsmodels.stats.diagnostic import recursive_olsresiduals
    rresid, rresid_standardized, rcusum, rcusum_ci = recursive_olsresiduals(model)
    
    # Plot
    plt.figure(figsize=(12, 4))
    plt.plot(rcusum, label='CUSUM')
    plt.plot(rcusum_ci[:, 0], 'r--', label='5% Bounds')
    plt.plot(rcusum_ci[:, 1], 'r--')
    plt.axhline(0, color='black', linewidth=0.5)
    plt.title('CUSUM Test for Parameter Stability')
    plt.legend()
    plt.show()
    
    # Test result
    stat, pvalue = breaks_cusumolsresid(model.resid)
    print(f"CUSUM test statistic: {stat:.4f}, p-value: {pvalue:.4f}")
    print(f"Result: {'Instability detected' if pvalue < 0.05 else 'No instability detected'}")
    return stat, pvalue

# cusum_test(df['value'])
```

## Method 4: Bai-Perron Multiple Break Test (statsmodels)

```python
from statsmodels.tsa.breakpoint_test import breakpoint_est

def bai_perron_breaks(series, max_breaks=5):
    """
    Bai-Perron test for multiple structural breaks.
    Estimates the number and dates of breaks jointly.
    """
    from statsmodels.regression.linear_model import OLS
    import statsmodels.api as sm
    
    t = np.arange(len(series))
    X = sm.add_constant(t)
    
    # Fit with statsmodels Bai-Perron (available via breakpoint tests)
    model = OLS(series.values, X)
    result = model.fit()
    
    # Use ruptures as an approximation to Bai-Perron
    print("Using PELT (approximate Bai-Perron) to detect up to", max_breaks, "breaks...")
    signal = series.values.reshape(-1, 1)
    algo = rpt.Pelt(model="normal", min_size=max(5, len(series)//20)).fit(signal)
    
    # Try different numbers of breaks and report BIC
    best_bic = np.inf
    best_n = 0
    n = len(series)
    for k in range(1, max_breaks + 1):
        bkps = rpt.Binseg(model="normal").fit_predict(signal, n_bkps=k)
        # Approximate BIC: cost + k * log(n)
        algo_bs = rpt.Binseg(model="normal").fit(signal)
        cost_fn = rpt.costs.CostNormal().fit(signal)
        total_cost = sum(cost_fn.error(s, e) for s, e in
                         zip([0] + bkps[:-1], bkps))
        bic = total_cost + k * np.log(n)
        if bic < best_bic:
            best_bic = bic
            best_n = k
    
    print(f"Optimal number of breaks: {best_n}")
    final_bkps = rpt.Binseg(model="normal").fit_predict(signal, n_bkps=best_n)
    
    if isinstance(series, pd.Series) and isinstance(series.index, pd.DatetimeIndex):
        break_dates = [series.index[bp - 1] for bp in final_bkps[:-1]]
        print(f"Break dates: {break_dates}")
    
    return final_bkps

# bai_perron_breaks(df['value'], max_breaks=5)
```

## Method 5: Segment-Specific Statistics

```python
def segment_stats(series, breakpoints):
    """
    Compute mean, std, and trend for each segment defined by breakpoints.
    breakpoints: list of integer indices (from ruptures output)
    """
    boundaries = [0] + breakpoints
    rows = []
    
    for i in range(len(boundaries) - 1):
        start, end = boundaries[i], boundaries[i+1]
        segment = series.iloc[start:end] if isinstance(series, pd.Series) else series[start:end]
        
        t = np.arange(len(segment))
        slope = np.polyfit(t, segment, 1)[0] if len(segment) > 1 else 0
        
        row = {
            'Segment': i + 1,
            'Start': series.index[start] if isinstance(series, pd.Series) else start,
            'End': series.index[end-1] if isinstance(series, pd.Series) else end-1,
            'N': len(segment),
            'Mean': segment.mean(),
            'Std': segment.std(),
            'Trend (slope)': slope
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    print("\nSegment Statistics:")
    print(df.to_string(index=False))
    return df

# breaks = detect_breaks_pelt(df['value'], penalty=15)
# segment_stats(df['value'], breaks)
```

## Recommended Workflow

```
1. Plot the series — visually identify obvious breaks
2. Run CUSUM test — detect instability without specifying break location
3. Run PELT with model="normal" — get candidate break dates
4. Validate with Chow test at each candidate date
5. Compute segment statistics — confirm break is meaningful (level shift? variance shift? trend change?)
6. Adjust forecasting model: fit separate models per segment, or use Prophet with changepoints
```
