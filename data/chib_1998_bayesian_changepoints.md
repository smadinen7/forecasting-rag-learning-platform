# Bayesian Estimation of Multiple Change-Point Models

## Reference
Chib, S. (1998). "Estimation and comparison of multiple change-point models." *Journal of Econometrics*, 86(2), 221–241.

## Overview

Chib (1998) provides the foundational Bayesian framework for estimating models with multiple change points. The paper's key contribution is reformulating the change-point problem as a hidden Markov model with an absorbing state structure, enabling efficient MCMC sampling via the forward-backward algorithm. It also provides tools for comparing models with different numbers of change points via Bayes factors, computed directly from MCMC output.

**Key Reference:** Chib, S. (1998). "Estimation and comparison of multiple change-point models." *Journal of Econometrics*, 86(2), 221–241.

## Model Formulation

Consider a time series $y_1, \ldots, y_T$ that undergoes $m-1$ change points at unknown dates $\tau_1 < \tau_2 < \cdots < \tau_{m-1}$, creating $m$ regimes. Within regime $j$ (observations $\tau_{j-1}+1$ to $\tau_j$), the data follow a model with parameter $\theta_j$:

$$y_t \sim f(y_t | \theta_j) \quad \text{for } t \in (\tau_{j-1}, \tau_j]$$

The key insight is to represent the regime membership via a latent state variable $s_t \in \{1, 2, \ldots, m\}$ with transition structure:

$$P(s_t = j | s_{t-1} = j) = p_{jj}, \quad P(s_t = j+1 | s_{t-1} = j) = 1 - p_{jj}$$
$$P(s_t = m | s_{t-1} = m) = 1$$

This is an **absorbing Markov chain**: the state can only move forward (from regime $j$ to $j+1$), never backward. This restriction distinguishes change-point models from standard Markov-switching models (which allow regime recurrence) and is what makes breaks "permanent" in the change-point sense.

## MCMC Sampling: The Forward-Backward Algorithm

Chib (1996) developed an efficient algorithm for sampling the state sequence $\mathbf{s} = (s_1, \ldots, s_T)$ from its full conditional distribution. For change-point models, this proceeds in two passes:

**Forward pass:** Compute filtered probabilities $\alpha_t(j) = P(s_t = j | y_1, \ldots, y_t)$ for $t = 1, \ldots, T$ and $j = 1, \ldots, m$ recursively:

$$\alpha_t(j) \propto f(y_t | \theta_j) \cdot \sum_{i \leq j} \alpha_{t-1}(i) \cdot P(s_t = j | s_{t-1} = i)$$

**Backward sampling:** Starting from $t = T$, sample $s_T$ from the smoothed distribution, then sample $s_{T-1} | s_T$, continuing backward. The absorbing structure means sampling is efficient because once $s_T = m$ is drawn, all subsequent (backward) samples can only be $\leq m$.

The complete Gibbs sampling scheme cycles through:
1. Sample $\mathbf{s} | \boldsymbol{\theta}, \mathbf{p}, \mathbf{y}$ — via forward-backward algorithm
2. Sample $\theta_j | \mathbf{s}, \mathbf{y}$ — standard posterior conditional for observations in regime $j$
3. Sample $p_{jj} | \mathbf{s}$ — Beta posterior (conjugate to geometric likelihood of staying in regime $j$)

## Priors

**Regime parameters:** Independent priors on each $\theta_j$, typically conjugate (Normal-InverseGamma for Gaussian data, Dirichlet for categorical data).

**Transition probabilities:** $p_{jj} \sim \text{Beta}(u_j, v_j)$ independently. The posterior is $\text{Beta}(u_j + n_{jj}, v_j + 1)$ where $n_{jj}$ is the number of periods spent in regime $j$.

**Minimum regime length:** To avoid degenerate solutions (one-observation regimes), a minimum segment length $l_{\min}$ can be imposed via the prior on transition probabilities.

## Model Comparison: How Many Change Points?

A central challenge in change-point analysis is determining the number of breaks $m-1$. Chib (1998) computes the **marginal likelihood** $p(\mathbf{y} | m)$ using the method of Chib (1995), which extracts it from the MCMC output without additional simulation:

$$\log p(\mathbf{y} | m) = \log p(\mathbf{y} | \hat{\boldsymbol{\theta}}, \hat{\mathbf{s}}, m) + \log p(\hat{\boldsymbol{\theta}}, \hat{\mathbf{s}} | m) - \log p(\hat{\boldsymbol{\theta}}, \hat{\mathbf{s}} | \mathbf{y}, m)$$

Each term on the right is available from MCMC output:
- Likelihood at posterior mode: straightforward
- Prior density at mode: known analytically
- Posterior density at mode: estimated from MCMC draws

The **Bayes factor** for comparing $m$ vs. $m'$ break models is:
$$\text{BF}_{m, m'} = \frac{p(\mathbf{y} | m)}{p(\mathbf{y} | m')}$$

$\text{BF} > 10$: strong evidence for $m$ breaks over $m'$ (Jeffreys' scale). This avoids the arbitrary threshold selection of information criteria and provides probabilistic model comparison.

## Practical Advantages Over Frequentist Approaches

| Feature | Frequentist (Bai-Perron) | Bayesian (Chib 1998) |
|---------|--------------------------|----------------------|
| Break date uncertainty | Point estimates only | Full posterior distribution |
| Model comparison | Sequential tests (pre-specified size) | Bayes factors (automatic) |
| Parameter uncertainty | Ignored in forecasting | Propagated via MCMC |
| Small post-break samples | OLS with wide CIs | Shrinkage via prior |
| Future break risk | Not modeled | Extendable (PPT 2006) |

## Extensions Built on Chib (1998)

**Pesaran, Pettenuzzo & Timmermann (2006):** Add hierarchical prior across regimes enabling cross-regime learning; extend to forecasting with future break uncertainty.

**Koop & Potter (2007):** "Estimation and forecasting in models with multiple breaks." Allow for unknown number of regimes with a prior on $m$ itself; develop computationally scalable alternatives.

**Giordani & Kohn (2008):** Efficient Bayesian estimation via particle filtering for high-dimensional change-point models.

**Barry & Hartigan (1993):** Earlier Bayesian product partition model for change points — Chib (1998) generalizes this to a wider class of models with richer parameter structure.

## Diagnosing Break Dates

From the MCMC output, the posterior distribution over break dates is:
$$P(\tau_k = t | \mathbf{y}) = \text{fraction of MCMC draws where } s_t \neq s_{t+1} \text{ at the } k\text{th transition}$$

A sharp spike in this distribution indicates a well-identified break date; a flat distribution indicates break date uncertainty. This probabilistic treatment is more informative than a single point estimate, especially for breaks at the ends of the sample where data are sparse.

## Key References

- Chib, S. (1998). "Estimation and comparison of multiple change-point models." *Journal of Econometrics*, 86(2), 221–241.
- Chib, S. (1996). "Calculating posterior distributions and modal estimates in Markov mixture models." *Journal of Econometrics*, 75(1), 79–97.
- Chib, S. (1995). "Marginal likelihood from the Gibbs output." *Journal of the American Statistical Association*, 90(432), 1313–1321.
- Barry, D. and Hartigan, J.A. (1993). "A Bayesian analysis for change point problems." *Journal of the American Statistical Association*, 88(421), 309–319.
- Koop, G. and Potter, S.M. (2007). "Estimation and forecasting in models with multiple breaks." *Review of Economic Studies*, 74(3), 763–789.
- Pesaran, M.H., Pettenuzzo, D., and Timmermann, A. (2006). "Forecasting time series subject to multiple structural breaks." *Review of Economic Studies*, 73(4), 1057–1084.
