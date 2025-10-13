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
