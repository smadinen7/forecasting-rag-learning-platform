---
title: "Evaluation and Governance for Break-Aware Forecasting Systems"
source: "Internal Training Materials - Risk & Compliance"
type: "Governance Framework"
relevance: "Operational Best Practices"
---

# Evaluation and Governance for Break-Aware Forecasting Systems

## Introduction

Deploying forecasting systems that detect and adapt to structural breaks introduces unique evaluation and governance challenges. Traditional metrics (MSE, MAE) are insufficient, and operational risks (model drift, false alarms, audit trails) require rigorous frameworks.

## Evaluation Metrics for Break-Aware Systems

### 1. Break-Adjusted Error Metrics

**Standard MSE/MAE** penalize all errors equally, ignoring that post-break errors are often unavoidable.

**Regime-Conditional RMSE:**
$$
\text{RMSE}_r = \sqrt{\frac{1}{|T_r|} \sum_{t \in T_r} (y_t - \hat{y}_t)^2}
$$

where $T_r$ is the set of time points in regime $r$.

**Why It Matters:** Allows separate evaluation of pre-break vs. post-break performance.

### 2. Detection Performance Metrics

**True Positive Rate (Recall):** Fraction of actual breaks correctly detected.

**False Positive Rate:** Fraction of false alarms (spurious break detections).

**Detection Lag:** Time elapsed between actual break and detection.

**Trade-off:** Aggressive detection (high recall) → more false positives → unnecessary re-estimation costs.

### 3. Forecast Robustness Metrics

**Maximum Absolute Deviation (MAD) Across Scenarios:**
$$
\text{MAD} = \max_{s \in S} |y_t - \hat{y}_t^{(s)}|
$$

where $S$ is a set of break scenarios (e.g., mild recession, severe recession, no break).

**Why It Matters:** Measures worst-case forecast error under model uncertainty.

**Coverage Probability:** Fraction of actuals falling within prediction intervals.
- Stable systems: 95% coverage for 95% intervals.
- Break-prone systems: Coverage often drops to 70–80% without adaptive methods.

### 4. Business Impact Metrics

**Decision Cost:** Expected financial loss from forecast errors.
- Example: Overforecasting demand → excess inventory costs.
- Example: Underforecasting revenue → missed growth opportunities.

**Regret:** Difference between decision made under forecast vs. optimal decision with perfect foresight.

## Governance Framework

### 1. Model Monitoring

**Continuous Diagnostics:**
- Plot residuals over time; flag persistent patterns.
- Track rolling RMSE; alert if degradation exceeds threshold.
- Monitor break detection signals (e.g., CUSUM statistic approaching critical value).

**Automated Alerts:**
- Trigger email/Slack notification when:
  - Break detected (with confidence score).
  - Forecast error exceeds 2× historical baseline.
  - Model re-estimation scheduled (e.g., post-break).

### 2. Model Versioning & Audit Trails

**Version Control:**
- Tag each model deployment with:
  - Training data range (e.g., "2018-01 to 2023-12").
  - Detected breaks (e.g., "Break at 2020-03").
  - Hyperparameters (e.g., "EWMA λ=0.94").
  - Provider/algorithm (e.g., "ARIMA(2,1,2) + Markov-switching").

**Audit Logs:**
- Record every forecast generated:
  - Timestamp, input features, model version, prediction, actual (when available), error.
- Enable forensic analysis: "Why did we forecast X when actual was Y?"

### 3. Stakeholder Communication

**Transparency:**
- Explain breaks to non-technical stakeholders (e.g., "Sales forecast revised due to detected market shift in Q2").
- Visualize regime probabilities (e.g., "70% chance we're in low-growth regime").

**Uncertainty Quantification:**
- Report prediction intervals, not just point forecasts.
- Communicate confidence: "High uncertainty due to recent break."

**Escalation Protocols:**
- Define thresholds for escalating forecast deviations to senior management.
- Example: If MAE > 10% for 3 consecutive months → trigger strategy review.

### 4. Ethical Considerations

**Bias Amplification:**
- Breaks can reflect systemic injustices (e.g., pandemic disproportionately affects low-income workers).
- Ensure forecasts don't encode or amplify discriminatory patterns.

**Accountability:**
- Assign clear ownership: Who decides when to override automated break detection?
- Document overrides with rationale (e.g., "Ignored false positive due to data glitch").

**Fairness in Resource Allocation:**
- If forecasts drive budgets (e.g., regional sales targets), ensure break adjustments don't systematically disadvantage certain groups.

### 5. Testing & Validation

**Backtesting:**
- Simulate break scenarios on historical data.
- Example: Artificially inject a level shift at 2019-06; verify detection and overlay performance.

**Stress Testing:**
- Test forecasts under extreme but plausible breaks (e.g., "What if inflation spikes to 10%?").

**Champion-Challenger Framework:**
- Always run a baseline model (e.g., simple ARIMA) alongside break-aware model.
- Compare performance; switch to challenger only if consistently better.

## Implementation Checklist

- [ ] Define regime-conditional RMSE and detection metrics.
- [ ] Set up automated monitoring dashboard (e.g., Streamlit, Tableau).
- [ ] Implement model versioning (e.g., Git tags + metadata YAML).
- [ ] Log all forecasts and break detections to database.
- [ ] Schedule monthly review meetings with stakeholders.
- [ ] Document escalation protocols in runbook.
- [ ] Conduct annual fairness audit of forecast-driven decisions.
- [ ] Maintain regression test suite for break detection algorithms.

## Case Study: Energy Demand Forecasting

**Context:** Utility company forecasts daily electricity demand.

**Challenge:** 2020 work-from-home shift caused structural break (residential demand up, commercial down).

**Governance Response:**
1. **Detection:** CUSUM flagged break in April 2020.
2. **Audit:** Logged break event; tagged all post-April forecasts with "COVID-regime" label.
3. **Communication:** Weekly reports to operations team showing regime probabilities.
4. **Re-estimation:** Retrained models on post-break data; archived pre-break models.
5. **Monitoring:** Set alert for reversal (return to office) by tracking commercial usage.
6. **Outcome:** Avoided $2M in overbuild costs; maintained 90%+ forecast accuracy.

## Key Takeaways

- Standard metrics (MSE) are necessary but insufficient; add regime-conditional and robustness metrics.
- Governance is not optional—breaks have financial, operational, and ethical implications.
- Automate monitoring and logging; humans review edge cases.
- Transparency builds trust; hide complexity but expose uncertainty.

---

**References:**
- Gneiting, T., & Katzfuss, M. (2014). "Probabilistic Forecasting." *Annual Review of Statistics and Its Application*.
- Pesaran, M. H., & Timmermann, A. (2007). "Selection of Estimation Window in the Presence of Breaks." *Journal of Econometrics*.
- Federal Reserve Board. (2020). "Supervisory Guidance on Model Risk Management." SR 11-7.
