# Markov Regime-Switching Models

## Overview

Markov regime-switching models, introduced by Hamilton (1989), allow the parameters of a time series model to shift discretely between a finite number of states or regimes. The regime itself is treated as an unobserved latent variable that follows a first-order Markov chain. This framework is particularly powerful for capturing the abrupt changes in dynamics that characterize financial cycles, business cycles, and economic crises.

**Key Reference:** Hamilton, J.D. (1989). "A new approach to the economic analysis of nonstationary time series and the business cycle." *Econometrica*, 57(2), 357–384.

## Model Structure

In the simplest two-state version, the observable variable $y_t$ follows:

$$y_t = \mu_{S_t} + \phi(y_{t-1} - \mu_{S_{t-1}}) + \varepsilon_t$$

where $S_t \in \{1, 2\}$ is the unobserved regime at time $t$, $\mu_{S_t}$ is the regime-dependent mean, and $\varepsilon_t \sim N(0, \sigma^2_{S_t})$. The regime-dependent variance allows each state to have its own volatility level.

The unobserved Markov chain governing $S_t$ is characterized by the transition probability matrix:

$$P = \begin{pmatrix} p_{11} & 1-p_{22} \\ 1-p_{11} & p_{22} \end{pmatrix}$$

where $p_{ij} = \Pr(S_t = j \mid S_{t-1} = i)$. The diagonal elements $p_{11}$ and $p_{22}$ represent the probability of remaining in each regime. High values (e.g., 0.9) indicate persistent regimes; low values indicate rapid switching.

## The Hamilton Filter

Estimation proceeds via the Hamilton filter, an algorithm analogous to the Kalman filter for hidden Markov models. The filter recursively computes:

1. **Prediction step:** Given the filtered probability $\Pr(S_{t-1} = i \mid \mathcal{F}_{t-1})$, compute the predicted regime probability using the transition matrix $P$.
2. **Update step:** Update regime probabilities using the likelihood of observing $y_t$ under each regime via Bayes' theorem.

Formally, the filtered probability is:
$$\xi_{t|t} = \frac{\xi_{t|t-1} \odot \eta_t}{\mathbf{1}^\top (\xi_{t|t-1} \odot \eta_t)}$$

where $\eta_t$ is the vector of conditional densities $f(y_t \mid S_t = j, \mathcal{F}_{t-1})$ and $\xi_{t|t-1} = P^\top \xi_{t-1|t-1}$.

The log-likelihood is constructed as:
$$\log L = \sum_{t=1}^T \log \left[\mathbf{1}^\top (\xi_{t|t-1} \odot \eta_t)\right]$$

Maximized via numerical optimization (BFGS or EM algorithm). The EM algorithm (Expectation-Maximization) is often preferred for numerical stability: the E-step computes smoothed regime probabilities using the entire sample (Kim smoother), and the M-step updates parameters given those probabilities.

**Key Reference:** Kim, C.-J. and Nelson, C.R. (1999). *State-Space Models with Regime Switching*. MIT Press.

## Smoothed vs. Filtered Probabilities

- **Filtered probabilities** $\Pr(S_t = j \mid y_1, \ldots, y_t)$: real-time estimates using only past and current data. Useful for online monitoring and real-time regime detection.
- **Smoothed probabilities** $\Pr(S_t = j \mid y_1, \ldots, y_T)$: retrospective estimates using the full sample. Used for historical analysis and model diagnostics.

The Kim (1994) smoother passes backward through the filtered output:
$$\xi_{t|T} = \xi_{t|t} \odot \left[P \frac{\xi_{t+1|T}}{\xi_{t+1|t}}\right]$$

**Reference:** Kim, C.-J. (1994). "Dynamic linear models with Markov-switching." *Journal of Econometrics*, 60(1-2), 1–22.

## Multi-State and MS-VAR Extensions

The two-state model generalizes naturally to $K$ regimes. For multivariate series, the Markov-Switching VAR (MS-VAR) model allows all VAR coefficients to switch simultaneously:

$$y_t = A_{0,S_t} + A_{1,S_t} y_{t-1} + \cdots + A_{p,S_t} y_{t-p} + \varepsilon_t, \quad \varepsilon_t \sim N(0, \Sigma_{S_t})$$

Common specifications allow different intercepts per regime (MS-I), different autoregressive parameters (MS-A), or different covariance matrices (MS-H) — or combinations thereof.

**Reference:** Krolzig, H.-M. (1997). *Markov-Switching Vector Autoregressions*. Springer-Verlag.

## Regime-Conditional Forecasting

Forecasting from regime-switching models involves averaging over future regime uncertainty. The $h$-step-ahead forecast is:

$$\hat{y}_{T+h} = \sum_{j=1}^K \Pr(S_{T+h} = j \mid \mathcal{F}_T) \cdot E[y_{T+h} \mid S_{T+h} = j, \mathcal{F}_T]$$

The transition probability matrix raised to the $h$-th power, $P^h$, gives the $h$-step regime transition probabilities. In the long run ($h \to \infty$), the regime probabilities converge to the ergodic (stationary) distribution of the Markov chain.

## Comparison to Threshold Models

Markov regime-switching models differ from threshold autoregressive (TAR) models in that:
- **MS models:** Regime determined by an unobserved latent variable; switches are probabilistic.
- **TAR models:** Regime determined by an observed threshold variable crossing a known boundary; switches are deterministic conditional on the threshold.

TAR models (Tong, 1990) are better suited when the switching mechanism is observable (e.g., interest rate exceeds a target level). MS models are preferred when regimes are driven by unobservable forces such as investor sentiment or latent business cycle phases.

## Applications

- **Business cycle dating:** Hamilton's original application identified US recessions as Regime 1 (low growth, high variance) and expansions as Regime 2 (high growth, low variance).
- **Financial regime detection:** Identifying bull vs. bear market regimes in equity returns or low vs. high volatility regimes in FX.
- **Macroeconomic forecasting:** Allowing monetary policy transmission coefficients to vary by regime.
- **Structural break robustness:** Regime-switching captures gradual or recurring shifts that pure structural break tests may miss.

## Software

- Python: `statsmodels.tsa.regime_switching.markov_regression.MarkovRegression`, `statsmodels.tsa.regime_switching.markov_autoregression.MarkovAutoregression`
- R: `MSwM` package, `depmixS4`, `msmtools`
- Stata: `mswitch` command

## Key References

- Hamilton, J.D. (1989). "A new approach to the economic analysis of nonstationary time series and the business cycle." *Econometrica*, 57(2), 357–384.
- Hamilton, J.D. (1990). "Analysis of time series subject to changes in regime." *Journal of Econometrics*, 45(1-2), 39–70.
- Hamilton, J.D. (1994). *Time Series Analysis*. Princeton University Press. Chapter 22.
- Kim, C.-J. and Nelson, C.R. (1999). *State-Space Models with Regime Switching*. MIT Press.
- Krolzig, H.-M. (1997). *Markov-Switching Vector Autoregressions*. Springer-Verlag.
