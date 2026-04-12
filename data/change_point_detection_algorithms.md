# Change Point Detection Algorithms

## Overview

Change point detection identifies time points where the statistical properties of a time series shift — a change in mean, variance, trend, or distributional shape. Unlike structural break tests (which test for a break at a known or unknown date), change point detection algorithms automatically segment a series into homogeneous regions. Key algorithms include PELT (exact, offline), Binary Segmentation (approximate, offline), and BOCPD (online, probabilistic).

**Key Reference:** Killick, R., Fearnhead, P., and Eckley, I.A. (2012). "Optimal detection of changepoints with a linear computational cost." *Journal of the American Statistical Association*, 107(500), 1590–1598.

## Problem Formulation

Given a time series $y_1, \ldots, y_T$, find change point locations $\tau_1 < \tau_2 < \cdots < \tau_K$ that partition the series into $K+1$ homogeneous segments. Within each segment $(\tau_{j-1}, \tau_j]$, the data follows a common distribution with parameters $\theta_j$.

The optimal segmentation minimizes the total cost plus a penalty for model complexity:
$$\min_{K, \tau_1,\ldots,\tau_K} \left[\sum_{j=1}^{K+1} \mathcal{C}(y_{\tau_{j-1}+1:\tau_j}) + K \cdot \beta\right]$$

where $\mathcal{C}(\cdot)$ is a segment cost function (often negative log-likelihood) and $\beta$ is the penalty per change point. Common penalties:
- **BIC:** $\beta = p \ln T$ (where $p$ is the number of free parameters per segment)
- **AIC:** $\beta = 2p$
- **Linear:** $\beta$ chosen by the user via cross-validation

## Binary Segmentation

The oldest and simplest change point algorithm (Scott & Knott, 1974):
1. Fit a test statistic (e.g., CUSUM or likelihood ratio) to the full series; find the single most likely change point $\hat{\tau}_1$
2. Split the series at $\hat{\tau}_1$ into two sub-series
3. Recursively apply the procedure to each sub-series until no significant change points remain

**Complexity:** $O(T \log T)$ — fast, but greedy. Binary segmentation is inconsistent: if the first split is placed incorrectly, subsequent splits in sub-series are affected. It may miss change points that are only detectable jointly.

## PELT (Penalized Cost, Exact)

PELT (Pruned Exact Linear Time) solves the global penalized cost problem exactly using dynamic programming with a pruning step that eliminates candidate change points that cannot be optimal.

**Dynamic programming:** Define $F(t)$ as the optimal total cost for the series $y_{1:t}$:
$$F(t) = \min_{s < t} [F(s) + \mathcal{C}(y_{s+1:t}) + \beta]$$

**PELT pruning rule:** A candidate $s$ is pruned from future consideration if:
$$F(s) + \mathcal{C}(y_{s+1:t}) + \beta \geq F(t)$$

i.e., segmenting at $s$ already costs more than the current best — it can never improve the optimum at any future time point.

**Complexity:** $O(T)$ on average (linear) when the number of change points grows linearly with $T$, making PELT practical for long series.

**Reference:** Killick, R. et al. (2012). JASA 107(500).

## Window-Based Segmentation

For non-stationary series where the full-sample cost is ill-defined, **sliding window** methods compare statistical properties in adjacent windows:
$$d(t) = \text{divergence}(y_{t-w:t}, y_{t:t+w})$$

A change point is flagged when $d(t)$ exceeds a threshold. The divergence can be KL divergence, Earth Mover's Distance, or a two-sample test statistic. This is computationally simple but less statistically principled than PELT.

## BOCPD (Bayesian Online Change Point Detection)

Adams and MacKay (2007) formulated online change point detection as exact Bayesian inference. The key quantity is the **run length** $r_t$ — the number of time steps since the last change point.

At each step $t$:
1. Compute the predictive distribution of $y_t$ under each possible run length value $r$
2. Update the posterior over run lengths using Bayes' theorem
3. A sharp spike in the posterior for $r_t = 0$ signals a change point

The hazard function $H(r)$ specifies the prior probability of a change point at each step. Typically $H(r) = 1/\lambda$ (geometric, constant rate), implying an expected run length of $\lambda$.

**Advantages over offline methods:**
- Fully online: processes one observation at a time
- Provides uncertainty over change point location
- No need to specify total number of change points

**Reference:** Adams, R.P. and MacKay, D.J.C. (2007). "Bayesian online changepoint detection." *arXiv:0710.3742*.

## The `ruptures` Library (Python)

The `ruptures` library (Truong et al., 2020) implements the main offline change point detection algorithms in Python:

```python
import ruptures as rpt

# PELT with RBF cost (detects changes in mean and variance)
model = rpt.Pelt(model="rbf", min_size=3, jump=1).fit(signal)
breakpoints = model.predict(pen=10)  # pen controls number of change points

# Binary segmentation with normal cost
model = rpt.Binseg(model="normal").fit(signal)
breakpoints = model.predict(n_bkps=3)  # specify number of change points

# Window-based
model = rpt.Window(width=20, model="l2").fit(signal)
breakpoints = model.predict(n_bkps=3)
```

**Cost functions in ruptures:**
- `"l2"`: minimizes within-segment variance (detects mean shifts)
- `"normal"`: maximizes normal log-likelihood (detects mean + variance shifts)
- `"rbf"`: kernel-based (non-parametric, detects any distributional shift)
- `"ar"`: autoregressive (detects changes in AR coefficients)

**Penalty selection:** Use `model.predict(pen=beta)` to let the algorithm determine the number of change points, or `model.predict(n_bkps=K)` to specify $K$ breaks. Cross-validation via `ruptures.KernelCPD` or the elbow method on the cost curve can guide penalty selection.

**Reference:** Truong, C., Oudre, L., and Vayatis, N. (2020). "Selective review of offline change point detection methods." *Signal Processing*, 167.

## Choosing a Change Point Algorithm

| Scenario | Recommended Algorithm |
|----------|----------------------|
| Offline, any number of breaks, large T | PELT (exact, linear time) |
| Offline, approximate, very large T | Binary Segmentation |
| Online, need real-time detection | BOCPD |
| Non-parametric, unknown distribution | ruptures with `rbf` cost |
| Change in AR structure | ruptures with `ar` cost |
| Formal hypothesis testing (single break) | Chow test, Bai-Perron |

## Key References

- Killick, R., Fearnhead, P., and Eckley, I.A. (2012). *JASA*, 107(500), 1590–1598.
- Adams, R.P. and MacKay, D.J.C. (2007). "Bayesian online changepoint detection." *arXiv:0710.3742*.
- Truong, C., Oudre, L., and Vayatis, N. (2020). "Selective review of offline change point detection methods." *Signal Processing*, 167.
- Bai, J. and Perron, P. (2003). "Computation and analysis of multiple structural change models." *Journal of Applied Econometrics*, 18(1), 1–22.
