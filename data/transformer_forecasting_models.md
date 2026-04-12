# Transformer-Based Time Series Forecasting Models

## Overview

Since the success of the Transformer architecture in NLP (Vaswani et al., 2017), a wave of transformer-based models has been developed for time series forecasting. Key models include Informer (2021), PatchTST (2023), and iTransformer (2024). These models differ substantially in how they apply self-attention — to individual time steps, to patches of time steps, or to variate tokens — and have progressively improved over vanilla Transformers.

## The Core Challenge: Applying Attention to Time Series

The original Transformer uses self-attention over a sequence of tokens. For time series, the naive approach treats each time step as a token. This creates two problems:
1. **Quadratic complexity:** Self-attention is $O(L^2)$ in sequence length $L$, making long sequences expensive.
2. **Point-wise tokenization loses temporal structure:** A single time step (scalar) is a weak token with little semantic content.

Recent architectures address these problems differently.

## Informer (2021)

**Paper:** Zhou, H., Zhang, S., Peng, J., Zhang, S., Li, J., Xiong, H., and Zhang, W. (2021). "Informer: Beyond efficient transformer for long sequence time-series forecasting." *AAAI 2021*. Best Paper Award.

**Key innovation:** ProbSparse self-attention — reduces complexity from $O(L^2)$ to $O(L \log L)$ by identifying the "active" queries (those with high attention entropy) and only computing full attention for those.

**Architecture:**
- Encoder: Stacked ProbSparse attention + distilling (pooling) layers that halve sequence length
- Decoder: Generative decoding — predicts all future steps in one forward pass (no autoregressive loop), reducing inference time
- Handles sequences up to 48 hours (720 time steps) efficiently

**Limitation:** The speed-up from ProbSparse attention came at some cost to accuracy; later models showed that vanilla attention with better tokenization could outperform Informer.

## PatchTST (2023)

**Paper:** Nie, Y., Nguyen, N.H., Seyfi, P., and Kalagnanam, J. (2023). "A time series is worth 64 words: Long-term forecasting with transformers." *ICLR 2023*.

**Key innovations:**
1. **Patching:** Divides the time series into non-overlapping (or slightly overlapping) subseries patches of length $P$, reducing the sequence length from $L$ to $\lceil L/P \rceil$. Each patch is a richer token (carries local temporal context).
2. **Channel independence:** Each univariate channel is processed independently with shared Transformer weights. This avoids spurious cross-variate attention and acts as regularization.

**Why patches work:** A patch of 16 time steps encodes a local temporal pattern (e.g., a week of daily data). This is semantically richer than a single point, analogous to how word tokens are richer than individual characters in NLP.

**Result:** PatchTST significantly outperformed prior transformer models (Informer, Autoformer, FEDformer) on long-term forecasting benchmarks (ETT, Weather, Traffic, Electricity) and rivaled or exceeded simple linear baselines that had previously challenged transformers.

## iTransformer (2024)

**Paper:** Liu, Y., Hu, T., Zhang, H., Wu, H., Wang, S., Ma, L., and Long, M. (2024). "iTransformer: Inverted transformers are effective for time series forecasting." *ICLR 2024*.

**Key innovation — inverted attention:** Instead of applying attention across time steps (for a single variate), iTransformer applies attention across variates (for all time steps of each variate). Each variate's entire time series becomes one token.

- **Variate token:** The full historical sequence of variate $i$ is embedded as a single token $\mathbf{h}_i \in \mathbb{R}^d$
- **Attention over variates:** Self-attention learns which variates correlate with which others
- **Feed-forward network:** Learns the temporal patterns within each variate's representation

**Why this works:** For multivariate series, capturing cross-variate correlations (which iTransformer does via attention over variate tokens) is often more valuable than modeling within-variate temporal patterns alone (which point-wise attention over time steps captures).

**Result:** iTransformer achieved state-of-the-art on multiple multivariate benchmarks (ETT, Solar-Energy, PEMS), particularly for high-dimensional series where cross-variate dependencies are strong.

## Comparison of Architectures

| Model | Tokenization | Attention direction | Best for |
|-------|-------------|-------------------|---------|
| Vanilla Transformer | Point (per time step) | Time × Time | Short sequences |
| Informer | Point (per time step) | ProbSparse Time × Time | Long univariate sequences |
| PatchTST | Patch (subseries) | Patch × Patch (per variate) | Long univariate, channel-independent |
| iTransformer | Variate (full series) | Variate × Variate | High-dimensional multivariate |

## The Linear Model Debate

Zeng et al. (2023) showed that a simple linear model (DLinear) — which just uses a linear projection from lookback window to forecast horizon — outperformed many transformers on standard benchmarks. This sparked debate about whether attention is actually necessary for time series.

**Current consensus:** Transformers do outperform linear models when:
- Sequences are very long (where non-linear patterns matter)
- Multivariate dependencies are strong (iTransformer's strength)
- The dataset is large enough to train deep models

For short/medium series with limited data, simple baselines (ETS, ARIMA, linear) remain competitive.

**Reference:** Zeng, A., Chen, M., Zhang, L., and Xu, Q. (2023). "Are transformers effective for time series forecasting?" *AAAI 2023*.

## Practical Guidance

- **Small dataset (<10K samples):** Use ARIMA, ETS, or Prophet; deep models will overfit
- **Medium dataset, univariate, long horizon:** PatchTST or N-BEATS
- **Large dataset, multivariate, high-dimensional:** iTransformer
- **Need prediction intervals:** Use probabilistic models (DeepAR, TFT) rather than point-forecast transformers
- **Interpretability required:** Use TFT (attention weights identify important variables/lags)

## Key References

- Vaswani, A. et al. (2017). "Attention is all you need." *NeurIPS 2017*.
- Zhou, H. et al. (2021). "Informer: Beyond efficient transformer for long sequence time-series forecasting." *AAAI 2021*.
- Nie, Y. et al. (2023). "A time series is worth 64 words." *ICLR 2023*.
- Liu, Y. et al. (2024). "iTransformer: Inverted transformers are effective for time series forecasting." *ICLR 2024*.
- Zeng, A. et al. (2023). "Are transformers effective for time series forecasting?" *AAAI 2023*.
