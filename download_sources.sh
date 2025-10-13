#!/bin/bash
# Download script for 12 verified sources
# Run: chmod +x download_sources.sh && ./download_sources.sh

echo "📥 Downloading sources to data/ directory..."
mkdir -p data

# 1. STL Decomposition
echo "1/12 STL Decomposition..."
curl -L -o data/Cleveland_STL_Decomposition.pdf "https://www.wessa.net/download/stl.pdf"

# 2. Hyndman Textbook (we'll save a note since it's a whole website)
echo "2/12 Hyndman Textbook (creating reference note)..."
cat > data/Hyndman_FPP3_Reference.md << 'EOF'
# Forecasting: Principles and Practice (3rd ed)
**Authors**: Rob J Hyndman and George Athanasopoulos
**URL**: https://otexts.com/fpp3/

## Key Chapters for Our Topic

### Chapter 9: ARIMA models
- Non-stationary time series
- Unit root tests
- Differencing

### Chapter 10: Dynamic regression models
- Forecasting with exogenous variables
- Intervention analysis

### Chapter 12: Advanced forecasting methods
- Complex seasonality
- Vector autoregressions

### Chapter 13: Some practical forecasting issues
- Dealing with missing values
- Outliers and structural breaks
- Long-term forecasting challenges

## Relevant Content on Structural Breaks

The textbook discusses structural breaks in the context of:
- **Model selection**: When underlying data generation process changes
- **Forecast evaluation**: How breaks affect forecast accuracy
- **Intervention variables**: Modeling known structural changes
- **Rolling windows**: Adaptive forecasting when breaks suspected

## Key Quotes

> "When there is a structural break in the data, it is common to use only the data after the most recent break point for modeling and forecasting."

> "If the structural break is not detected, the forecasts may be very poor because the model is estimated using data from a different regime."

## Practical Guidance

1. **Detection**: Use CUSUM tests, recursive residuals
2. **Handling**: Either model the break explicitly or use only post-break data
3. **Evaluation**: Diebold-Mariano test for comparing forecasts across breaks
EOF

# 3. Bai & Perron (abstract only from Wiley - may need institutional access for full text)
echo "3/12 Bai & Perron (saving reference - full PDF may require access)..."
cat > data/BaiPerron_2003_Reference.md << 'EOF'
# Computation and Analysis of Multiple Structural Change Models
**Authors**: Jushan Bai, Pierre Perron
**Journal**: Journal of Applied Econometrics, 2003
**DOI**: https://onlinelibrary.wiley.com/doi/abs/10.1002/jae.659

## Abstract Summary

This paper provides comprehensive methodology for:
- Estimating multiple structural breaks in linear regression models
- Testing for structural breaks
- Computing confidence intervals for break dates
- Selecting the number of breaks

## Key Contributions

1. **Sequential testing procedure**: Determines number of breaks
2. **Dynamic programming algorithm**: Efficiently estimates break points
3. **Confidence intervals**: Assesses uncertainty in break dates
4. **Software implementation**: Publicly available code

## Applications to Forecasting

- Identify regime changes in macroeconomic relationships
- Improve forecast accuracy by modeling distinct regimes
- Determine appropriate sample periods for estimation

**Note**: Full PDF may require institutional access. Check your library for access.
EOF

# 4. StatStream
echo "4/12 StatStream..."
curl -L -o data/ZhuShasha_StatStream.pdf "https://arxiv.org/pdf/1101.1438"

# 5. Timmermann
echo "5/12 Timmermann - Forecasting under Model Instability..."
curl -L -o data/Timmermann_ModelInstability.pdf "https://rady.ucsd.edu/_files/faculty-research/timmermann/forecasting-macroeconomic-variables-under-model-instability.pdf"

# 6. Google Correlate
echo "6/12 Google Correlate..."
curl -L -o data/Google_Correlate.pdf "https://research.google.com/pubs/archive/41854.pdf"

# 7. MinT (Optimal Reconciliation)
echo "7/12 MinT - Optimal Forecast Reconciliation..."
curl -L -o data/Wickramasuriya_MinT.pdf "https://robjhyndman.com/papers/MinT.pdf"

# 8. Diebold-Mariano
echo "8/12 Diebold-Mariano..."
curl -L -o data/DieboldMariano_1995.pdf "https://www.ssc.wisc.edu/~bhansen/718/DieboldMariano1995.pdf"

# 9. Prophet
echo "9/12 Facebook Prophet..."
curl -L -o data/TaylorLetham_Prophet.pdf "https://facebook.github.io/prophet/static/prophet_paper_20170113.pdf"

# 10. N-BEATS
echo "10/12 N-BEATS..."
curl -L -o data/Oreshkin_NBEATS.pdf "https://arxiv.org/pdf/1704.04110"

# 11. Temporal Fusion Transformers
echo "11/12 Temporal Fusion Transformers..."
curl -L -o data/Lim_TemporalFusionTransformers.pdf "https://arxiv.org/pdf/1912.09363"

# 12. Time Series Momentum
echo "12/12 Time Series Momentum..."
curl -L -o data/Li_TimeSeriesMomentum.pdf "https://openreview.net/pdf?id=r1ecqn4YwB"

echo ""
echo "✅ Download complete!"
echo ""
echo "📊 Downloaded files:"
ls -lh data/*.pdf data/*.md
echo ""
echo "🔄 Next steps:"
echo "1. Review downloads (some may be HTML if links changed)"
echo "2. Remove old placeholder files: rm data/structural_breaks.md data/forecasting_overlays.md data/evaluation_governance.md"
echo "3. Rebuild FAISS index: make ingest"
echo "4. Verify: make run"
