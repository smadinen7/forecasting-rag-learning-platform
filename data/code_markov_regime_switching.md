# Python Code: Markov Regime Switching Models

## Overview
Fitting Markov regime-switching models using `statsmodels`. Covers 2-state switching mean, switching AR, filtered/smoothed probabilities, and regime-conditional forecasting.

## Dependencies
```python
pip install statsmodels pandas numpy matplotlib
```

## Step 1: Fit a 2-State Switching Mean Model

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
from statsmodels.tsa.regime_switching.markov_autoregression import MarkovAutoregression

def fit_markov_mean(series, k_regimes=2):
    """
    Fit Markov switching model with regime-dependent means.
    H_t: switching heteroskedasticity (each regime has its own variance).
    """
    model = MarkovRegression(
        series,
        k_regimes=k_regimes,
        trend='c',          # constant mean per regime
        switching_variance=True  # allow different variance per regime
    )
    result = model.fit(search_reps=10, search_scale=0.2)
    print(result.summary())
    return result

# result = fit_markov_mean(df['value'], k_regimes=2)
```

## Step 2: Fit a 2-State Switching AR Model (MS-AR)

```python
def fit_markov_ar(series, k_regimes=2, order=1):
    """
    Fit Markov switching AR(order) model.
    switching_ar: AR coefficients switch across regimes.
    switching_variance: variances switch across regimes.
    """
    model = MarkovAutoregression(
        series,
        k_regimes=k_regimes,
        order=order,
        trend='c',
        switching_ar=True,        # AR coefficients differ by regime
        switching_variance=True   # variance differs by regime
    )
    result = model.fit(search_reps=10)
    print(result.summary())
    return result

# result = fit_markov_ar(df['value'], k_regimes=2, order=1)
```

## Step 3: Extract and Plot Regime Probabilities

```python
def plot_regime_probabilities(result, series, regime_labels=None):
    """
    Plot filtered and smoothed regime probabilities alongside the series.
    """
    k_regimes = result.k_regimes
    if regime_labels is None:
        regime_labels = [f'Regime {i+1}' for i in range(k_regimes)]
    
    fig, axes = plt.subplots(k_regimes + 1, 1, figsize=(14, 4 * (k_regimes + 1)))
    
    # Plot series
    axes[0].plot(series, color='black', linewidth=0.8)
    axes[0].set_title('Time Series')
    axes[0].set_ylabel('Value')
    
    # Shade by most likely regime
    smoothed = result.smoothed_marginal_probabilities
    most_likely = smoothed.values.argmax(axis=1)
    colors = ['lightblue', 'lightyellow', 'lightgreen', 'lightsalmon']
    for regime in range(k_regimes):
        mask = most_likely == regime
        axes[0].fill_between(
            series.index,
            series.min(), series.max(),
            where=mask,
            alpha=0.3, color=colors[regime % len(colors)],
            label=regime_labels[regime]
        )
    axes[0].legend(loc='upper right')
    
    # Plot smoothed regime probabilities
    for i in range(k_regimes):
        prob_col = smoothed.iloc[:, i]
        axes[i + 1].plot(prob_col, label=f'P({regime_labels[i]})', color=colors[i % len(colors)])
        axes[i + 1].fill_between(prob_col.index, 0, prob_col, alpha=0.4, color=colors[i % len(colors)])
        axes[i + 1].set_ylim(0, 1)
        axes[i + 1].set_title(f'Smoothed P({regime_labels[i]})')
        axes[i + 1].set_ylabel('Probability')
    
    plt.tight_layout()
    plt.show()

# plot_regime_probabilities(result, df['value'], regime_labels=['Contraction', 'Expansion'])
```

## Step 4: Inspect Transition Probabilities

```python
def print_transition_matrix(result, regime_labels=None):
    """
    Print the estimated transition probability matrix.
    P[i,j] = probability of moving from regime i to regime j.
    """
    k = result.k_regimes
    if regime_labels is None:
        regime_labels = [f'Regime {i+1}' for i in range(k)]
    
    # Transition matrix is stored in result.params
    # Get it from the regime-switching summary
    print("\nTransition Probability Matrix:")
    print(f"{'':15s}", end="")
    for j in regime_labels:
        print(f"→ {j:12s}", end="")
    print()
    
    for i, from_regime in enumerate(regime_labels):
        print(f"From {from_regime:10s}", end="")
        for j in range(k):
            # Each regime's stay probability
            param_name = f'p[{i}->{j}]'
            try:
                prob = result.transition_matrix[i, j]
                print(f"  {prob:.4f}      ", end="")
            except Exception:
                print(f"  N/A          ", end="")
        print()
    
    # Expected duration in each regime
    print("\nExpected duration in each regime:")
    try:
        P = result.transition_matrix
        for i, regime in enumerate(regime_labels):
            duration = 1 / (1 - P[i, i])
            print(f"  {regime}: {duration:.1f} periods")
    except Exception:
        pass

# print_transition_matrix(result, ['Bear Market', 'Bull Market'])
```

## Step 5: Extract Regime-Specific Parameters

```python
def regime_summary(result, regime_labels=None):
    """Print regime-specific means and variances."""
    k = result.k_regimes
    if regime_labels is None:
        regime_labels = [f'Regime {i+1}' for i in range(k)]
    
    print("\nRegime-Specific Parameters:")
    params = result.params
    
    for i in range(k):
        print(f"\n{regime_labels[i]}:")
        # Means (const[0], const[1] in params)
        try:
            mean = params[f'const[{i}]']
            print(f"  Mean:     {mean:.4f}")
        except KeyError:
            pass
        # Variances
        try:
            sigma2 = params.get(f'sigma2[{i}]', params.get('sigma2', np.nan))
            print(f"  Std Dev:  {np.sqrt(float(sigma2)):.4f}")
        except Exception:
            pass

# regime_summary(result, ['Low Volatility', 'High Volatility'])
```

## Step 6: Determine Current Regime

```python
def current_regime(result, regime_labels=None, threshold=0.7):
    """
    Report the most likely current regime based on filtered probabilities.
    threshold: probability above which we classify a regime as 'certain'.
    """
    k = result.k_regimes
    if regime_labels is None:
        regime_labels = [f'Regime {i+1}' for i in range(k)]
    
    # Filtered (not smoothed) probabilities — use only past data
    filtered = result.filtered_marginal_probabilities
    latest = filtered.iloc[-1]
    most_likely_idx = latest.values.argmax()
    prob = latest.values[most_likely_idx]
    
    print(f"\nCurrent regime probabilities (filtered):")
    for i, label in enumerate(regime_labels):
        bar = '█' * int(filtered.iloc[-1, i] * 20)
        print(f"  {label:20s}: {filtered.iloc[-1, i]:.3f} {bar}")
    
    if prob >= threshold:
        print(f"\n→ Most likely regime: {regime_labels[most_likely_idx]} ({prob:.1%} probability)")
    else:
        print(f"\n→ Uncertain — highest probability {prob:.1%} below threshold {threshold:.0%}")
    
    return most_likely_idx, prob

# current_regime(result, ['Recession', 'Expansion'])
```

## Full Working Example

```python
import numpy as np
import pandas as pd
from statsmodels.tsa.regime_switching.markov_autoregression import MarkovAutoregression

# Simulate a 2-regime AR(1) process
np.random.seed(42)
T = 500
regime = np.zeros(T, dtype=int)
y = np.zeros(T)

# Transition probabilities
P = np.array([[0.95, 0.05],  # from regime 0: stay with prob 0.95
              [0.10, 0.90]]) # from regime 1: stay with prob 0.90

# Regime parameters
mu    = [0.2, -0.5]    # means
phi   = [0.5,  0.3]    # AR(1) coefficients
sigma = [0.5,  1.5]    # std devs

y[0] = mu[0]
for t in range(1, T):
    # Markov transition
    regime[t] = np.random.choice(2, p=P[regime[t-1]])
    y[t] = mu[regime[t]] + phi[regime[t]] * y[t-1] + sigma[regime[t]] * np.random.randn()

series = pd.Series(y)

# Fit model
model = MarkovAutoregression(series, k_regimes=2, order=1,
                              switching_ar=True, switching_variance=True)
result = model.fit(search_reps=5)
print(result.summary())

# Filtered probabilities
smoothed = result.smoothed_marginal_probabilities
print("\nTrue regime (first 10):", regime[:10])
print("P(Regime 0) (first 10):", smoothed.iloc[:10, 0].round(3).values)
```
