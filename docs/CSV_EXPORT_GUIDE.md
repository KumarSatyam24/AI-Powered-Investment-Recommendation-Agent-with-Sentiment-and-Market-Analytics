# Stock Data CSV Export System

## 📊 Overview

The Stock Data CSV Export System generates comprehensive datasets for machine learning and predictive modeling. It combines stock price data, technical indicators, sentiment analysis scores, fundamental data, and market context into structured CSV files ready for ML algorithms.

## 🎯 Features

### Data Sources Integrated
- **Stock Price Data**: Current prices, volume, OHLC data
- **Technical Indicators**: SMA, RSI, price momentum, volatility measures  
- **Sentiment Analysis**: News sentiment, social media sentiment, confidence scores
- **Fundamental Data**: P/E ratio, market cap, beta, dividend yield
- **Market Context**: VIX levels, economic indicators, market conditions
- **Derived Features**: Risk scores, valuation categories, sentiment momentum

### Output Formats
- **Individual Stock CSV**: Comprehensive data for single stock analysis
- **Multi-Stock CSV**: Combined dataset for comparative analysis  
- **Metadata JSON**: Column descriptions and data source information
- **Time Series Ready**: Timestamp columns for sequential modeling

## 🚀 Quick Start

### 1. Basic Usage

```bash
# Generate CSV for single stock
python generate_csv_data.py AAPL

# Multiple stocks
python generate_csv_data.py AAPL MSFT GOOGL

# Extended timeframe
python generate_csv_data.py AAPL --days 90
```

### 2. Python API Usage

```python
from src.data_export.stock_data_exporter import StockDataExporter

# Initialize exporter
exporter = StockDataExporter()

# Export single stock data
csv_file = exporter.export_stock_data('AAPL', days=30, 
                                     include_news=True, 
                                     include_technical=True)

# Export multiple stocks
tickers = ['AAPL', 'MSFT', 'GOOGL']
csv_files = exporter.export_multiple_stocks(tickers, days=30)
```

### 3. Demo Example

```bash
# Run comprehensive demo
python demo_csv_export.py
```

## 📋 Command Line Options

### Basic Commands

| Command | Description |
|---------|-------------|
| `python generate_csv_data.py AAPL` | Export AAPL data |
| `python generate_csv_data.py AAPL MSFT` | Export multiple stocks |
| `python generate_csv_data.py --sector tech` | Export tech sector stocks |
| `python generate_csv_data.py --samples` | Create sample datasets |

### Advanced Options

| Option | Description |
|--------|-------------|
| `--days N` | Number of days of historical data (default: 30) |
| `--no-news` | Exclude news sentiment data |
| `--no-technical` | Exclude technical indicators |
| `--batch file.txt` | Process tickers from file |
| `--examples` | Show usage examples |
| `--ml-guide` | Show ML modeling guide |

### Sector Options

| Sector | Stocks Included |
|--------|-----------------|
| `tech` | AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, NFLX |
| `finance` | JPM, BAC, WFC, GS, MS, C, AXP, BLK |
| `healthcare` | JNJ, PFE, UNH, ABBV, MRK, TMO, ABT, LLY |
| `energy` | XOM, CVX, COP, EOG, SLB, MPC, PSX, VLO |
| `consumer` | PG, KO, PEP, WMT, HD, MCD, NKE, SBUX |

## 📊 Dataset Structure

### Core Data Columns

#### Price & Volume Data
- `current_price`: Current stock price
- `change`: Price change from previous close  
- `change_percent`: Percentage change
- `volume`: Trading volume
- `high`, `low`: Daily price range
- `previous_close`: Previous closing price

#### Technical Indicators
- `sma_20`: 20-day Simple Moving Average
- `sma_50`: 50-day Simple Moving Average  
- `rsi_14`: 14-day Relative Strength Index
- `price_vs_sma20`: Price position vs 20-day SMA
- `price_momentum`: Price momentum indicator

#### Sentiment Analysis
- `combined_sentiment_score`: Unified sentiment (-1 to +1)
- `sentiment_label`: Categorical sentiment (Positive/Negative/Neutral)
- `confidence_score`: Sentiment confidence (0-100)
- `news_sentiment_score`: News-specific sentiment
- `reddit_sentiment_score`: Reddit sentiment
- `twitter_sentiment_score`: Twitter sentiment

#### Fundamental Data
- `market_cap`: Market capitalization
- `pe_ratio`: Price-to-earnings ratio
- `beta`: Stock beta (volatility vs market)
- `dividend_yield`: Annual dividend yield
- `eps`: Earnings per share
- `52_week_high`, `52_week_low`: 52-week price range

#### Market Context
- `vix_level`: VIX volatility index
- `market_condition`: Overall market sentiment
- `unemployment_rate`: Economic indicator
- `inflation_rate`: Inflation rate
- `federal_funds_rate`: Fed interest rate

#### Derived Features (ML-Ready)
- `risk_score`: Calculated risk score (0-10)
- `sentiment_momentum`: Average sentiment across sources
- `intraday_volatility`: Daily price volatility
- `valuation_category`: Valuation assessment
- `market_fear_level`: Market fear categorization

### Time Series Structure
- `timestamp`: ISO format timestamp
- `date`: Date in YYYY-MM-DD format
- `ticker`: Stock symbol identifier

## 🤖 Machine Learning Guide

### Suggested Target Variables

#### Classification Tasks
- `sentiment_label`: Predict sentiment category
- `market_condition`: Predict market direction
- `valuation_category`: Predict valuation level

#### Regression Tasks  
- `price_momentum`: Predict price movement
- `future_returns`: Predict future returns (calculated)
- `risk_score`: Predict risk level
- `rsi_14`: Predict technical indicator

### Feature Engineering Examples

```python
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('AAPL_comprehensive_data_YYYYMMDD.csv')

# Create additional features
df['sentiment_volatility'] = df['combined_sentiment_score'].rolling(5).std()
df['price_rsi_divergence'] = df['current_price'] - df['rsi_14'] * df['current_price'] / 50
df['volume_momentum'] = df['volume'].pct_change()

# Create target variable (next day return)
df['next_day_return'] = df['current_price'].shift(-1) / df['current_price'] - 1

# Feature selection
feature_columns = [
    'rsi_14', 'combined_sentiment_score', 'volume', 'sma_20',
    'market_cap', 'vix_level', 'pe_ratio', 'sentiment_volatility'
]
```

### Model Examples

#### 1. Price Movement Prediction (Random Forest)
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Prepare data
features = ['rsi_14', 'combined_sentiment_score', 'volume', 'vix_level']
X = df[features].fillna(df[features].mean())
y = df['price_momentum'].fillna(0)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'MSE: {mse:.4f}')
print(f'R²: {r2:.4f}')

# Feature importance
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
```

#### 2. Sentiment Classification (XGBoost)
```python
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

# Prepare data for classification
le = LabelEncoder()
y_class = le.fit_transform(df['sentiment_label'])

X_train, X_test, y_train, y_test = train_test_split(X, y_class, test_size=0.2, random_state=42)

# Train XGBoost
xgb_model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)

xgb_model.fit(X_train, y_train)

# Evaluate
y_pred_class = xgb_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred_class)
print(f'Accuracy: {accuracy:.4f}')
print(classification_report(y_test, y_pred_class, target_names=le.classes_))
```

#### 3. Time Series Forecasting (LSTM)
```python
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler

# Prepare time series data
scaler = MinMaxScaler()
price_scaled = scaler.fit_transform(df[['current_price']].values)

# Create sequences
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:(i + seq_length)])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

seq_length = 10
X, y = create_sequences(price_scaled, seq_length)

# Split data
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Build LSTM model
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(seq_length, 1)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(1)
])

model.compile(optimizer='adam', loss='mse')
model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=0)

# Predict
y_pred_lstm = model.predict(X_test)
y_pred_lstm = scaler.inverse_transform(y_pred_lstm)
y_test_lstm = scaler.inverse_transform(y_test)
```

## 📁 File Organization

### Output Structure
```
data_exports/
├── AAPL_comprehensive_data_20240915_143022.csv
├── AAPL_comprehensive_data_20240915_143022_metadata.json
├── MSFT_comprehensive_data_20240915_143045.csv  
├── MSFT_comprehensive_data_20240915_143045_metadata.json
└── combined_stocks_data_20240915_143100.csv
```

### Metadata Contents
```json
{
  "dataset_info": {
    "ticker": "AAPL",
    "generation_date": "2024-09-15T14:30:22",
    "total_records": 156,
    "total_columns": 42,
    "csv_filename": "AAPL_comprehensive_data_20240915_143022.csv"
  },
  "data_sources": {
    "stock_prices": "Alpha Vantage API",
    "sentiment_analysis": "Unified Sentiment Analyzer", 
    "market_data": "FRED API",
    "news_data": "MarketAux API"
  },
  "column_descriptions": {...},
  "model_suggestions": {...}
}
```

## ⚙️ Configuration

### Environment Setup
1. Install required packages:
```bash
pip install pandas numpy scikit-learn xgboost tensorflow
```

2. Set up API keys in `.env`:
```env
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FRED_API_KEY=your_fred_key
MARKETAUX_API_KEY=your_marketaux_key
```

### Customization Options

#### Custom Data Sources
Extend the `StockDataExporter` class to add new data sources:

```python
class CustomStockDataExporter(StockDataExporter):
    def _get_custom_data(self, ticker: str) -> Dict[str, Any]:
        # Add your custom data source
        return {"custom_indicator": calculate_custom_metric(ticker)}
    
    def _combine_all_data(self, ticker: str, *args) -> List[Dict[str, Any]]:
        # Override to include custom data
        data = super()._combine_all_data(ticker, *args)
        custom_data = self._get_custom_data(ticker)
        for record in data:
            record.update(custom_data)
        return data
```

#### Custom Features
Add derived features in the `_calculate_derived_features` method:

```python
def _calculate_derived_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
    derived = super()._calculate_derived_features(data)
    
    # Add custom feature
    if data.get('volume') and data.get('current_price'):
        derived['dollar_volume'] = data['volume'] * data['current_price']
    
    return derived
```

## 🔧 Troubleshooting

### Common Issues

#### Import Errors
```bash
# If you get import errors, add project to Python path:
export PYTHONPATH="${PYTHONPATH}:/path/to/your/project"
```

#### API Rate Limits
- The system includes rate limiting for API calls
- Free tier APIs have daily/monthly limits
- Consider using demo mode for testing: `python demo_csv_export.py`

#### Missing Dependencies
```bash
# Install optional dependencies:
pip install psutil  # For system monitoring
pip install yfinance  # Alternative data source
```

#### Memory Issues with Large Datasets
- Reduce the number of days: `--days 15`
- Process stocks individually rather than in batches
- Exclude news data: `--no-news`

### Performance Tips

1. **Batch Processing**: Use `export_multiple_stocks()` for efficiency
2. **Selective Features**: Use `--no-news` or `--no-technical` to reduce data size
3. **Caching**: The system caches API responses where possible
4. **Parallel Processing**: Multiple stocks are processed concurrently

## 📈 Example Workflows

### Workflow 1: Single Stock Deep Analysis
```bash
# 1. Generate comprehensive data
python generate_csv_data.py AAPL --days 90

# 2. Analyze the data
python -c "
import pandas as pd
df = pd.read_csv('data_exports/AAPL_*.csv')
print(df.describe())
print(df.corr()['current_price'].sort_values())
"

# 3. Build prediction model (see ML examples above)
```

### Workflow 2: Sector Comparison Analysis
```bash
# 1. Generate sector data
python generate_csv_data.py --sector tech --days 60

# 2. Combined analysis
python -c "
import pandas as pd
df = pd.read_csv('data_exports/combined_*.csv')
sector_performance = df.groupby('ticker')['price_momentum'].mean()
print(sector_performance.sort_values(ascending=False))
"
```

### Workflow 3: Sentiment-Based Trading Strategy
```bash
# 1. Generate data with focus on sentiment
python generate_csv_data.py AAPL TSLA NVDA --days 30

# 2. Sentiment analysis
python -c "
import pandas as pd
import glob

files = glob.glob('data_exports/*_comprehensive_*.csv')
for file in files:
    df = pd.read_csv(file)
    ticker = df['ticker'].iloc[0]
    avg_sentiment = df['combined_sentiment_score'].mean()
    print(f'{ticker}: Avg Sentiment = {avg_sentiment:.3f}')
"
```

## 🎯 Use Cases

### Academic Research
- Study correlation between sentiment and stock performance
- Analyze impact of market conditions on individual stocks
- Research technical indicator effectiveness

### Trading Strategy Development
- Develop sentiment-based trading signals
- Create risk-adjusted portfolio recommendations  
- Build market timing models

### Financial Analysis
- Compare stocks across multiple dimensions
- Identify undervalued opportunities
- Risk assessment and portfolio optimization

### Machine Learning Projects
- Price prediction algorithms
- Sentiment classification models
- Market regime detection
- Anomaly detection in trading patterns

## 📚 Additional Resources

### Related Documentation
- [API Integration Guide](docs/API_INTEGRATION_GUIDE.md)
- [Project Documentation](docs/PROJECT_DOCUMENTATION.md)  
- [Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)

### External Resources
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [TensorFlow Tutorials](https://www.tensorflow.org/tutorials)

---

*For support or questions about the CSV export system, please refer to the project documentation or create an issue in the repository.*
