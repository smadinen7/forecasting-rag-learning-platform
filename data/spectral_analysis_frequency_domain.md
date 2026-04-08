# Spectral Analysis and Frequency Domain Methods

## Overview

Spectral analysis examines time series in the frequency domain, decomposing the total variance of a series into contributions from oscillations at different frequencies. This reveals cyclical structure — seasonality, business cycles, or periodic patterns — that may not be apparent from the time domain representation.

**Key Reference:** Brillinger, D.R. (2001). *Time Series: Data Analysis and Theory* (expanded edition). SIAM.

## The Spectral Density

For a stationary time series with autocovariance function $\gamma_k = \text{Cov}(y_t, y_{t-k})$, the **spectral density** is:

$$f(\omega) = \frac{1}{2\pi} \sum_{k=-\infty}^{\infty} \gamma_k e^{-i\omega k} = \frac{1}{2\pi}\left[\gamma_0 + 2\sum_{k=1}^{\infty} \gamma_k \cos(\omega k)\right]$$

defined for $\omega \in [0, \pi]$ (frequencies in radians per unit time). The spectral density is the Fourier transform of the autocovariance function — an equivalent representation of the second-order structure of the series.

**Parseval's theorem** ensures that the variance decomposes across frequencies:
$$\gamma_0 = \text{Var}(y_t) = \int_{-\pi}^{\pi} f(\omega) d\omega$$

A peak in $f(\omega)$ at frequency $\omega_0$ indicates that the series contains a significant periodic component with period $\lambda = 2\pi/\omega_0$.

## The Periodogram

The empirical estimate of the spectral density is the **periodogram**:

$$I(\omega_j) = \frac{1}{2\pi T} \left|\sum_{t=1}^T y_t e^{-i\omega_j t}\right|^2$$

evaluated at the Fourier frequencies $\omega_j = 2\pi j / T$, $j = 0, 1, \ldots, \lfloor T/2 \rfloor$. The periodogram is the modulus squared of the discrete Fourier transform (DFT) of the data.

**Caveat:** The raw periodogram is an inconsistent estimator of the spectral density — it does not converge as $T \to \infty$ because each frequency estimate has Chi-squared(2) distributed variance regardless of sample size. Smoothed periodogram estimates (using lag windows or kernel smoothing) are needed for consistent estimation.

## Seasonal Frequency Identification

For monthly data ($s=12$), seasonal frequencies occur at $\omega_j = 2\pi j / 12$ for $j = 1, \ldots, 6$:
- Fundamental: $\omega = \pi/6$ (period 12 months, annual cycle)
- First harmonic: $\omega = \pi/3$ (period 6 months, semi-annual cycle)
- And so on up to $\omega = \pi$ (period 2 months)

Sharp peaks in the periodogram at these frequencies confirm deterministic or stochastic seasonality that should be modeled (via SARIMA, seasonal dummies, or STL decomposition).

## Bandpass Filters

**Bandpass filters** isolate oscillations within a specified frequency band by removing components outside that band.

### Hodrick-Prescott (HP) Filter

The HP filter (Hodrick & Prescott, 1997) separates a series into trend $\tau_t$ and cyclical component $c_t = y_t - \tau_t$ by solving:

$$\min_{\tau} \left[\sum_{t=1}^T (y_t - \tau_t)^2 + \lambda \sum_{t=2}^{T-1} (\Delta^2 \tau_t)^2\right]$$

The smoothing parameter $\lambda$ controls the trade-off between fit and smoothness. Standard values: $\lambda = 1600$ (quarterly), $\lambda = 14400$ (monthly), $\lambda = 100$ (annual).

**Limitation:** The HP filter has poor end-of-sample properties (the trend is distorted near the boundaries) and is criticized for potentially creating spurious cycles (Hamilton, 2018).

**Reference:** Hodrick, R.J. and Prescott, E.C. (1997). "Postwar U.S. business cycles: An empirical investigation." *Journal of Money, Credit and Banking*, 29(1), 1–16.

### Baxter-King (BK) Filter

The Baxter-King bandpass filter (1999) directly targets business cycle frequencies (periods of 6–32 quarters for quarterly data) using a symmetric moving average:

$$c_t = \sum_{k=-K}^{K} a_k y_{t-k}$$

where the weights $a_k$ are designed to pass oscillations in the target frequency band and eliminate all others. The filter is symmetric (avoiding phase shift) and requires $K$ observations to be lost at each end of the sample (typically $K=12$).

**Reference:** Baxter, M. and King, R.G. (1999). "Measuring business cycles: Approximate bandpass filters for economic time series." *Review of Economics and Statistics*, 81(4), 575–593.

## Wiener-Khintchine Theorem

The fundamental theorem connecting time domain and frequency domain:

$$\gamma_k = \int_{-\pi}^{\pi} e^{i\omega k} f(\omega) d\omega$$

This shows that the autocovariance function and spectral density are Fourier transform pairs — carrying identical information in different representations. The spectral density reveals which frequencies contribute most to serial correlation.

## Wavelet Analysis

Wavelets extend spectral analysis to non-stationary series by allowing time-varying spectral content. A wavelet transform decomposes the series into components localized in both time and frequency — useful when the dominant periodicity of a series changes over time (e.g., a business cycle whose duration shifts across economic regimes).

Unlike the Fourier transform, which uses sinusoidal basis functions of infinite duration, wavelets use localized oscillatory basis functions (Daubechies, Morlet, etc.) that can detect when specific frequencies are active.

## Spectral Analysis of Residuals

After fitting an ARIMA or structural model, plotting the periodogram of residuals reveals whether any periodic structure remains unexplained. Peaks at seasonal frequencies in the residual periodogram indicate that the model's seasonal specification is inadequate.

## Key References

- Brillinger, D.R. (2001). *Time Series: Data Analysis and Theory* (expanded ed.). SIAM.
- Hodrick, R.J. and Prescott, E.C. (1997). *Journal of Money, Credit and Banking*, 29(1), 1–16.
- Baxter, M. and King, R.G. (1999). *Review of Economics and Statistics*, 81(4), 575–593.
- Hamilton, J.D. (2018). "Why you should never use the Hodrick-Prescott filter." *Review of Economics and Statistics*, 100(5), 831–843.
- Harvey, A.C. (1989). *Forecasting, Structural Time Series Models and the Kalman Filter*. Cambridge University Press. Chapters 2–3.
