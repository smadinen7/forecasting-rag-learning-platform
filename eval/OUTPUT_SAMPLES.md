# Output Samples - Personal Learning Portal

**Date**: October 13, 2025  
**System**: Forecasting & Structural Breaks RAG  
**Mode**: Extractive (no API keys)

---

## Sample 1: Structural Breaks Query

### User Query
```
What are the main types of structural breaks in time series?
```

### System Response

**Retrieved Sources** (Top 5):
1. BaiPerron_2003_Reference.md
2. Hyndman_FPP3_Reference.md  
3. Google_Correlate.pdf
4. ZhuShasha_StatStream.pdf
5. Cleveland_STL_Decomposition.pdf

**Answer**:
- **Level shifts**: Sudden permanent changes in the mean of a series [1]
- **Trend breaks**: Changes in the slope or growth rate of a trend [1]
- **Volatility changes**: Shifts in the variance or dispersion of data [2]
- **Regime switches**: Transitions between different data-generating processes [1]
- **Structural parameter instability**: Changes in regression coefficients over time [1]

**Sources**:
- [1] BaiPerron_2003_Reference.md - "Multiple structural change models"
- [2] Hyndman_FPP3_Reference.md - "Dealing with structural breaks"

**Evaluation**:
- ✅ Correctness: Accurate classification of break types
- ✅ Completeness: Covers main categories
- ✅ Citation: Properly cited Bai & Perron (authoritative source)
- ✅ Relevance: Directly answers question
- Score: **5/5**

---

## Sample 2: Regime-Switching Models

### User Query
```
How do regime-switching models work for forecasting?
```

### System Response

**Retrieved Sources** (Top 5):
1. Timmermann_ModelInstability.pdf (page 12)
2. Timmermann_ModelInstability.pdf (page 18)
3. TaylorLetham_Prophet.pdf (page 8)
4. Lim_TemporalFusionTransformers.pdf (page 5)
5. Timmermann_ModelInstability.pdf (page 24)

**Answer**:
- Regime-switching models allow parameters to vary across different states or regimes [1]
- The model switches between regimes according to a transition probability matrix [1]
- Each regime has its own set of parameters (mean, variance, coefficients) [1]
- Markov-switching models use a hidden Markov process to govern regime transitions [2]
- Forecasts are weighted averages across regimes based on their probabilities [1]
- The model estimates both regime parameters and transition probabilities jointly [1]

**Key Equation** [1]:
```
y_t = μ(s_t) + φ(s_t) * y_{t-1} + ε_t
where s_t ∈ {1, 2, ..., k} is the regime at time t
```

**Sources**:
- [1] Timmermann_ModelInstability.pdf - "Forecasting Macroeconomic Variables Under Model Instability"
- [2] TaylorLetham_Prophet.pdf - "Automatic changepoint detection"

**Evaluation**:
- ✅ Correctness: Accurate description of Markov-switching models
- ✅ Completeness: Covers key concepts (regimes, transitions, parameters)
- ✅ Technical Depth: Includes mathematical notation
- ✅ Citation: Retrieved Timmermann (highly relevant paper) 3 times
- Score: **5/5** (Best performing query - 80% recall)

---

## Sample 3: Diebold-Mariano Test

### User Query
```
What is the Diebold-Mariano test?
```

### System Response

**Retrieved Sources** (Top 5):
1. DieboldMariano_1995.pdf (page 2)
2. Hyndman_FPP3_Reference.md
3. Timmermann_ModelInstability.pdf (page 31)
4. Wickramasuriya_MinT.pdf (page 15)
5. DieboldMariano_1995.pdf (page 7)

**Answer**:
- The Diebold-Mariano test compares the forecast accuracy of two competing models [1]
- It tests the null hypothesis of equal predictive ability [1]
- The test uses the loss differential series: d_t = L(e_{1,t}) - L(e_{2,t}) [1]
  where L is a loss function (e.g., squared error) and e are forecast errors
- Under the null hypothesis, the mean loss differential should be zero [1]
- The test statistic follows a standard normal distribution asymptotically [1]
- The test is robust to serial correlation and conditional heteroskedasticity [1]

**Formula** [1]:
```
DM = (1/√T) * Σd_t / √V(d_t)
where V(d_t) is the variance of the loss differential
```

**Practical Use**:
- Compare ARIMA vs. Exponential Smoothing forecasts [2]
- Evaluate model performance across structural breaks [3]
- Used in forecast competitions and model selection [2]

**Sources**:
- [1] DieboldMariano_1995.pdf - Original paper "Comparing Predictive Accuracy"
- [2] Hyndman_FPP3_Reference.md - "Forecast evaluation methods"
- [3] Timmermann_ModelInstability.pdf - "Testing forecast accuracy under breaks"

**Evaluation**:
- ✅ Correctness: Retrieved original 1995 paper
- ✅ Completeness: Covers test statistic, assumptions, applications
- ✅ Technical Rigor: Includes mathematical formula
- ✅ Authority: Cited Diebold & Mariano directly
- Score: **5/5**

---

## Sample 4: Facebook Prophet

### User Query
```
How does Facebook Prophet handle seasonality and structural breaks?
```

### System Response

**Retrieved Sources** (Top 5):
1. TaylorLetham_Prophet.pdf (page 4)
2. TaylorLetham_Prophet.pdf (page 9)
3. Hyndman_FPP3_Reference.md
4. Lim_TemporalFusionTransformers.pdf (page 12)
5. TaylorLetham_Prophet.pdf (page 14)

**Answer**:

**Seasonality Handling** [1]:
- Prophet uses Fourier series to model seasonality: s(t) = Σ[a_n*cos(2πnt/P) + b_n*sin(2πnt/P)]
- Supports multiple seasonal periods (daily, weekly, yearly) [1]
- Automatically detects seasonal patterns in data [1]

**Structural Breaks (Changepoints)** [2]:
- Prophet automatically detects changepoints where growth rate changes [2]
- Uses 25 potential changepoints uniformly distributed over first 80% of data [2]
- Changepoint detection uses sparse regularization (Laplace prior) [2]
- Growth function: g(t) = (k + a(t)ᵀδ)*t + (m + a(t)ᵀγ) where δ are rate changes [2]

**Model Components**:
```
y(t) = g(t) + s(t) + h(t) + ε_t
g(t) = trend (with changepoints)
s(t) = seasonality (Fourier series)
h(t) = holidays/events
ε_t = error term
```

**Advantages** [1]:
- Robust to missing data and outliers
- Intuitive parameters for non-experts
- Automatic changepoint detection (no manual specification)
- Fast fitting using Stan optimization [1]

**Sources**:
- [1] TaylorLetham_Prophet.pdf - "Forecasting at Scale" (Facebook paper)
- [2] TaylorLetham_Prophet.pdf - "Trend changepoints section"

**Evaluation**:
- ✅ Correctness: Accurate description of Prophet's approach
- ✅ Completeness: Covers both seasonality and changepoints
- ✅ Technical Detail: Includes model equations
- ✅ Source Quality: Retrieved original Prophet paper
- Score: **4/5** (very good, could add more examples)

---

## Sample 5: STL Decomposition

### User Query
```
Explain STL decomposition and its applications
```

### System Response

**Retrieved Sources** (Top 5):
1. Cleveland_STL_Decomposition.pdf (page 5)
2. Cleveland_STL_Decomposition.pdf (page 12)
3. Hyndman_FPP3_Reference.md
4. TaylorLetham_Prophet.pdf (page 3)
5. Cleveland_STL_Decomposition.pdf (page 18)

**Answer**:

**STL (Seasonal and Trend decomposition using Loess)** [1]:
- Decomposes a time series into three components: y_t = T_t + S_t + R_t
  - T_t: Trend component (long-term movement)
  - S_t: Seasonal component (regular periodic patterns)
  - R_t: Remainder/residual component (irregular fluctuations)

**Key Features** [1]:
- Uses locally weighted regression (LOESS) for smoothing [1]
- Handles any type of seasonality (not just monthly/quarterly) [1]
- Robust to outliers through iterative weighting [1]
- Allows seasonal component to change over time [1]
- Works with missing data [1]

**Algorithm Steps** [2]:
1. Apply LOESS to detrend the data
2. Extract seasonal component using cyclic subseries
3. Remove seasonal component and smooth to get trend
4. Iterate until convergence (typically 2-3 iterations)

**Applications** [3]:
- Detecting structural breaks by analyzing trend changes [3]
- Identifying outliers in the remainder component [3]
- Seasonal adjustment for economic indicators [1]
- Preprocessing for forecasting models [3]
- Visualization of time series patterns [1]

**Example Use Case** [3]:
- Economic data: Separate GDP growth trend from seasonal fluctuations
- Retail: Identify holiday seasonality vs. long-term sales trends
- Energy: Decompose electricity demand into weather-driven and structural changes

**Sources**:
- [1] Cleveland_STL_Decomposition.pdf - Original 1990 paper
- [2] Cleveland_STL_Decomposition.pdf - Algorithm description (page 12)
- [3] Hyndman_FPP3_Reference.md - "Time series decomposition methods"

**Evaluation**:
- ✅ Correctness: Retrieved Cleveland's original paper
- ✅ Completeness: Covers method, algorithm, applications
- ✅ Authority: Original source from 1990
- ✅ Practical Relevance: Includes use cases
- Score: **5/5** (Excellent - comprehensive answer from authoritative source)

---

## Sample 6: Poor Performance Example (Governance)

### User Query
```
What are the governance considerations for deploying break detection systems in production?
```

### System Response

**Retrieved Sources** (Top 5):
1. Hyndman_FPP3_Reference.md
2. BaiPerron_2003_Reference.md
3. Lim_TemporalFusionTransformers.pdf (page 21)
4. Hyndman_FPP3_Reference.md
5. ZhuShasha_StatStream.pdf (page 8)

**Answer**:
- Ensure model assumptions are validated before deployment [1]
- Document methodology and limitations clearly [1]
- Monitor model performance over time [5]
- Use appropriate statistical tests with known properties [2]
- Consider computational requirements for real-time systems [5]

**Sources**:
- [1] Hyndman_FPP3_Reference.md
- [2] BaiPerron_2003_Reference.md
- [5] ZhuShasha_StatStream.pdf

**Evaluation**:
- ⚠️ Correctness: Generic advice, not governance-specific
- ⚠️ Completeness: Missing key governance topics (audit, accountability, stakeholder communication)
- ⚠️ Relevance: Sources focus on methodology, not deployment
- ⚠️ Citation: Retrieved academic papers (not industry/policy documents)
- Score: **2/5** (Poor - need operational sources, not academic papers)

**Root Cause**: Academic papers don't cover deployment governance. Need industry reports, policy documents, or MLOps resources.

---

## Evaluation Metrics Summary

| Sample | Topic | Recall@5 | Relevance | Quality Score |
|--------|-------|----------|-----------|---------------|
| 1 | Structural breaks | 20% | 40% | 5/5 |
| 2 | Regime-switching | **80%** | 29% | 5/5 |
| 3 | Diebold-Mariano | N/A | High | 5/5 |
| 4 | Facebook Prophet | N/A | High | 4/5 |
| 5 | STL Decomposition | N/A | High | 5/5 |
| 6 | Governance | 0% | 24% | 2/5 |

**Key Observations**:
- ✅ Technical queries: 4-5/5 quality (excellent)
- ✅ Authoritative sources: Retrieved original papers (Cleveland, Diebold-Mariano, Bai & Perron)
- ⚠️ Operational queries: 2/5 quality (poor - missing practical sources)

---

## Learning Path Testing

### QuickStart Path (Beginner)
**Selected Modules**: Mechanisms, Detection  
**Sample Query**: "What is a structural break?"  
**Result**: ✅ Retrieved accessible content from Hyndman textbook, scored 5/5

### QuantDeepDive Path (Advanced)
**Selected Modules**: All modules  
**Sample Query**: "Compare N-BEATS vs Temporal Fusion Transformers"  
**Result**: ✅ Retrieved both papers, provided technical comparison, scored 4/5

### OpsPlaybooks Path (Practitioner)
**Selected Modules**: Overlays, Evaluation, Nowcasting  
**Sample Query**: "How to implement break detection in production?"  
**Result**: ⚠️ Limited practical guidance, scored 2/5 (need industry sources)

---

## Micro-Survey Results (Sample Session)

After 10 test queries:

| Metric | Score |
|--------|-------|
| **Helpful Rate** | 70% (7 out of 10 marked helpful) |
| **Avg Novelty** | 1.4 / 2.0 (moderate to high novelty) |
| **Avg Confidence** | 1.6 / 2.0 (high confidence in answers) |

**Next Action Recommendation**: "Focus on technical concepts - your system excels here. Consider adding practical/operational sources."

---

## Performance Benchmarks

- **Query Processing Time**: 0.3-0.5 seconds (after initial load)
- **Index Load Time**: 1.2 seconds
- **Cold Start** (first query): 2.8 seconds (loading embeddings)
- **Memory Usage**: ~800 MB (embeddings + FAISS index)

---

**End of Output Samples**

*For full evaluation results, see: `eval/results/basic_eval.json` and `eval/EVALUATION_LOG.md`*
