# Nowcasting and Mixed-Frequency Methods

## Overview

Nowcasting refers to the real-time estimation (or prediction) of the present value of a variable that is only available with a publication lag — most commonly GDP growth, inflation, or unemployment. The term blends "now" and "forecasting," emphasizing that the target period has already begun but the official data will not be released for weeks or months.

The challenge is that macroeconomic variables are released at different frequencies and with different lags. GDP is quarterly, released with a 1–2 month lag. But financial data (daily), survey indices (monthly), and employment statistics (monthly) are available in near real-time. Nowcasting methods extract information from these high-frequency and mixed-frequency indicators to form real-time estimates of the slower-moving variable.

**Key Reference:** Giannone, D., Reichlin, L., and Small, D. (2008). "Nowcasting: The real-time informational content of macroeconomic data." *Journal of Monetary Economics*, 55(4), 665–676.

## The Ragged-Edge Data Problem

A defining challenge in nowcasting is the "ragged edge" of the data matrix: at any given point in time, different variables have been updated to different dates. For example:
- GDP: last observation is Q4 of the previous year
- Monthly industrial production: data through 2 months ago
- Weekly jobless claims: data through last week

Standard time series models require a balanced (rectangular) data panel. Nowcasting models must handle missing observations at the end of each series gracefully, typically via state-space representations with the Kalman filter.

## Dynamic Factor Models

The leading nowcasting framework uses a Dynamic Factor Model (DFM), which assumes that a small number of unobserved common factors $f_t$ drive the comovements among a large panel of $N$ indicators $x_t$:

$$x_t = \Lambda f_t + \xi_t$$
$$f_t = A f_{t-1} + u_t$$

where $\Lambda$ is the factor loading matrix, $\xi_t$ is idiosyncratic noise, and $f_t$ follows a VAR(1). The factors represent the latent state of the economy.

The Kalman filter handles the ragged-edge problem elegantly: missing observations at the end of the panel are simply skipped in the update step (the measurement equation is not evaluated for missing entries). This allows the filter to extract factor estimates even from an incomplete data matrix.

**Estimation:** The EM algorithm (Expectation-Maximization) is the standard approach:
- E-step: Run Kalman smoother to obtain factor estimates given current parameters
- M-step: Update $\Lambda$, $A$, and covariance matrices using the smoothed factors

**Reference:** Stock, J.H. and Watson, M.W. (2002). "Macroeconomic forecasting using diffuse indexes." *Journal of Business and Economic Statistics*, 20(2), 147–162.

## MIDAS Regression

MIDAS (Mixed Data Sampling) regression, introduced by Ghysels, Santa-Clara, and Valkanov (2004), provides an alternative that directly regresses a low-frequency variable on leads/lags of high-frequency predictors without requiring a state-space framework.

The basic MIDAS regression of a quarterly variable $y_t^{(Q)}$ on a monthly predictor $x_{\tau}^{(M)}$ is:

$$y_t^{(Q)} = \beta_0 + \beta_1 B(L^{1/m}; \theta) x_{tm}^{(M)} + \varepsilon_t$$

where $B(L^{1/m}; \theta) = \sum_{k=0}^{K} b(k; \theta) L^{k/m}$ is a distributed lag polynomial with weights $b(k; \theta)$ that are parameterized as a smooth function of the lag index $k$, typically using the **Almon lag** or **Beta polynomial** weighting schemes.

**Almon lag weighting:** $b(k; \theta) = \exp(\theta_1 k + \theta_2 k^2) / \sum_j \exp(\theta_1 j + \theta_2 j^2)$

This ensures the weights sum to one and form a smooth, monotonically declining (or hump-shaped) profile, capturing the decaying relevance of older high-frequency observations.

**Advantage:** MIDAS avoids the need to aggregate high-frequency data before regression. It can directly exploit information from intra-quarter observations.

**Reference:** Ghysels, E., Santa-Clara, P., and Valkanov, R. (2004). "The MIDAS touch: Mixed data sampling regression models." Working Paper, UNC and UCLA.

## Bridge Equations

Bridge equations are a simpler alternative: aggregate high-frequency indicators to the quarterly frequency first (using averages or sums), then regress the quarterly target on the aggregated quarterly predictors. The bridge connects monthly or weekly data to the quarterly GDP release.

While less sophisticated than DFMs or MIDAS, bridge equations are computationally simple, easily interpretable, and often competitive in forecast accuracy for small indicator sets.

## Real-Time Data Revisions

A critical practical challenge is that macroeconomic data is revised — sometimes substantially — after initial release. GDP growth may be revised from 2.1% to 1.6% three months later. Genuine real-time evaluation of nowcasting models therefore requires access to **real-time vintage databases** (e.g., the Federal Reserve Bank of Philadelphia's Real-Time Data Set for Macroeconomists, ALFRED database) so that the model is evaluated on the data that was actually available at each point in time, not the final revised figures.

**Reference:** Croushore, D. and Stark, T. (2001). "A real-time data set for macroeconomists." *Journal of Econometrics*, 105(1), 111–130.

## COVID-19 and Structural Breaks in Nowcasting

The COVID-19 pandemic (2020) represented an extreme stress test for nowcasting models. GDP fell by ~10% in a single quarter — an outlier orders of magnitude larger than anything in the training data. Standard DFMs and MIDAS regressions failed because:

1. **Parameter instability:** Relationships between indicators and GDP broke down completely (e.g., employment indicators signaled a recession far larger than implied by historical factor loadings).
2. **Outlier contamination:** Including pandemic-era observations in estimation distorted factor loadings and model parameters for subsequent quarters.
3. **Regime shift:** The economy entered an entirely new regime with no historical precedent.

Adaptations included outlier-robust estimation (downweighting extreme observations), allowing time-varying factor loadings, using shorter estimation windows, and incorporating pandemic-specific indicators (mobility data, Google Trends) as additional nowcasting inputs.

**Reference:** Eraslan, S. and Götz, T. (2021). "An unconventional factor model for the COVID-19 pandemic." *Deutsche Bundesbank Discussion Paper*, No. 03/2021.

## Practical Nowcasting Systems

Major central banks operate institutional nowcasting systems:
- **New York Fed:** FRBNY nowcasting model based on Giannone, Reichlin, and Small (2008) DFM framework
- **ECB:** EuroCOIN composite indicator and related DFM models
- **Bank of England:** Uses bridge equations and DFMs for GDP growth nowcasts

These systems update in real-time as each data release arrives, showing how much each new data point revises the nowcast — called the **news** or **nowcast revision** decomposition.

## Key References

- Giannone, D., Reichlin, L., and Small, D. (2008). "Nowcasting: The real-time informational content of macroeconomic data." *Journal of Monetary Economics*, 55(4), 665–676.
- Stock, J.H. and Watson, M.W. (2002). "Macroeconomic forecasting using diffuse indexes." *Journal of Business and Economic Statistics*, 20(2), 147–162.
- Ghysels, E., Santa-Clara, P., and Valkanov, R. (2004). "The MIDAS touch: Mixed data sampling regression models." Working Paper.
- Banbura, M. and Modugno, M. (2014). "Maximum likelihood estimation of factor models on datasets with arbitrary pattern of missing data." *Journal of Applied Econometrics*, 29(1), 133–160.
- Croushore, D. and Stark, T. (2001). "A real-time data set for macroeconomists." *Journal of Econometrics*, 105(1), 111–130.
