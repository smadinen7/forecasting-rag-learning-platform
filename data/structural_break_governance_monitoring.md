# Structural Break Governance and Monitoring

## Overview

Deploying break-detection systems in production requires more than statistical methodology. Robust governance frameworks ensure that detected breaks are acted on appropriately, that model behavior is auditable, and that stakeholders receive timely, accurate communication. This document covers the operational and governance dimensions of structural break monitoring.

## Sequential Monitoring vs. Retrospective Detection

There are two distinct operational modes for structural break systems:

**Retrospective detection** analyzes a completed time series to identify where breaks occurred historically. Methods like Bai-Perron (2003) and Chow tests operate retrospectively. These are used for model diagnostics, understanding historical data, and setting initial parameters.

**Sequential (prospective) monitoring** detects breaks in real time as new data arrives. This is operationally more challenging because the monitor must avoid both false alarms (flagging noise as a break) and delayed detection (missing genuine regime changes). The monitor has access only to data up to the current period.

**Reference:** Chu, C.-S.J., Stinchcombe, M., and White, H. (1996). "Monitoring structural change." *Econometrica*, 64(5), 1045–1065.

## CUSUM Control Charts

The CUSUM (Cumulative Sum) chart, developed by Page (1954), is the foundational sequential monitoring tool. It detects shifts in the mean of a process by accumulating deviations from a reference value:

$$C_t^+ = \max(0, C_{t-1}^+ + x_t - \mu_0 - k)$$
$$C_t^- = \min(0, C_{t-1}^- + x_t - \mu_0 + k)$$

where $\mu_0$ is the in-control mean, $k$ is the allowance (half the shift magnitude to detect), and $C_t^{\pm}$ are the upper and lower CUSUM statistics. An alarm is triggered when $C_t^+ > h$ or $C_t^- < -h$, where $h$ is the decision threshold calibrated to achieve a target in-control Average Run Length (ARL).

**CUSUM for regression residuals:** In forecasting contexts, CUSUM is applied to recursive residuals (one-step-ahead forecast errors from an expanding-window model). Persistent positive or negative residuals indicate the model has become miscalibrated — a signal of a structural break.

**Reference:** Page, E.S. (1954). "Continuous inspection schemes." *Biometrika*, 41(1/2), 100–115.

## Statistical Process Control for Model Monitoring

Beyond CUSUM, several drift-detection statistics are used in production ML/statistical systems:

**Population Stability Index (PSI):** Measures distributional shift between a reference period and the current window:
$$\text{PSI} = \sum_i (p_i^{\text{current}} - p_i^{\text{ref}}) \ln\left(\frac{p_i^{\text{current}}}{p_i^{\text{ref}}}\right)$$
PSI < 0.1: no significant shift; 0.1–0.25: moderate shift (investigate); > 0.25: major shift (retrain).

**KL Divergence:** Measures information loss from approximating current distribution $Q$ with reference distribution $P$:
$$D_{KL}(Q \| P) = \sum_i Q(i) \log\frac{Q(i)}{P(i)}$$

**Kolmogorov-Smirnov (KS) Test:** Non-parametric test comparing empirical CDFs of two samples. Used to flag shifts in the distribution of input features or model residuals.

## Alerting Thresholds and Escalation

A robust monitoring system has multiple alerting tiers:

1. **Warning level:** PSI between 0.1 and 0.25, or CUSUM statistic approaching $0.8h$. Trigger: increased monitoring cadence and human review.
2. **Alert level:** PSI > 0.25, CUSUM exceeds $h$, or $p$-value of formal break test falls below 0.05. Trigger: automatic notification to model owner; model output flagged as potentially unreliable.
3. **Critical level:** Multiple break signals simultaneously or residuals exceeding 5 standard deviations. Trigger: model suspended pending investigation; fallback model activated.

All alerts must be logged with timestamp, triggering statistic, data period affected, and the identity of the reviewer who resolved the alert.

## Retraining Triggers and Governance

Not every detected break justifies immediate retraining. A governance framework should define explicit retraining triggers:

- **Automatic retraining:** When residual bias exceeds a threshold for $N$ consecutive periods (e.g., RMSE increases >20% vs. baseline for 3 months).
- **Human-in-the-loop:** When a break is detected but its nature is ambiguous (one-time shock vs. permanent regime change). A domain expert should assess whether the break reflects a genuine shift or a data artifact.
- **Scheduled retraining:** Periodic retraining on a rolling window regardless of break detection, as a preventive measure.

**Version control:** Each model version must be tagged with the training data range, hyperparameters, and evaluation metrics. When a break triggers retraining, the new model version is deployed alongside (not replacing) the old version for a shadow period to validate its behavior.

## Audit Trails

Regulatory and internal governance requirements demand full auditability of model decisions:

- **Decision logs:** Each forecast or model output must be traceable to the specific model version, training data vintage, and input features used.
- **Break detection logs:** All triggered alerts, with the statistic value, threshold, and the reviewer's disposition (false alarm / confirmed break / uncertain).
- **Model change records:** Timestamps and justifications for model updates, parameter changes, or retraining events.
- **Backtesting records:** Regular backtesting results comparing model performance to a benchmark, with results archived for regulatory review.

Audit trails should be immutable (append-only logs) and retained for the regulatory retention period (typically 7 years in financial services).

## Stakeholder Communication

When a structural break is confirmed, communication protocols must address different audiences:

**Technical stakeholders (risk management, quantitative analysts):**
- Detailed statistical evidence of the break (break date, confidence interval, affected parameters)
- Impact on model outputs (magnitude of forecast revision)
- Proposed remediation plan with timeline

**Non-technical stakeholders (senior management, clients):**
- Plain-language description of what changed (e.g., "the relationship between leading indicators and GDP shifted during the pandemic, causing our forecast model to be recalibrated")
- Business impact assessment
- Expected timeline to restoration of normal model reliability

**Transparency requirements:** In regulated environments, material model changes must be disclosed to regulators and, in some cases, clients. Transparency does not require revealing proprietary model details but does require disclosing that a significant model change was made and why.

## Accountability Structures

Clear ownership is essential. Each model should have:
- **Model owner:** Responsible for monitoring, break detection, and retraining decisions
- **Model validator:** Independent reviewer who validates the detection methodology and approves retraining
- **Senior sponsor:** Accountable at the business or risk committee level for model performance and governance compliance

Governance policies should specify the escalation path when model owners and validators disagree, and the documentation required to override a validator's assessment.

## Key References

- Page, E.S. (1954). "Continuous inspection schemes." *Biometrika*, 41(1/2), 100–115.
- Chu, C.-S.J., Stinchcombe, M., and White, H. (1996). "Monitoring structural change." *Econometrica*, 64(5), 1045–1065.
- Bai, J. and Perron, P. (2003). "Computation and analysis of multiple structural change models." *Journal of Applied Econometrics*, 18(1), 1–22.
- Basel Committee on Banking Supervision (2011). "Supervisory guidance for assessing banks' financial instrument fair value practices." *Bank for International Settlements*.
- SR 11-7: Guidance on Model Risk Management. *Federal Reserve and OCC*, 2011.
