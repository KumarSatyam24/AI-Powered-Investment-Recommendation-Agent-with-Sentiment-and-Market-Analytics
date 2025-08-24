# New APIs Integration Guide

## 🚀 Recently Added APIs

### 1. Alpha Vantage API
- **Purpose**: Enhanced stock data and technical indicators
- **Free Tier**: 25 requests per day
- **Key Features**:
  - Real-time stock quotes
  - Company fundamentals (P/E, EPS, market cap, etc.)
  - Technical indicators (SMA, EMA, RSI, MACD)
  - Better reliability than yfinance for production

### 2. FRED API (Federal Reserve Economic Data)
- **Purpose**: Macroeconomic indicators for market analysis
- **Free Tier**: Completely free, no rate limits
- **Key Features**:
  - Inflation rates (CPI)
  - Unemployment data
  - Federal funds rate
  - VIX (volatility index)
  - Consumer sentiment
  - Treasury rates
  - Economic growth indicators

### 3. MarketAux API
- **Purpose**: Financial news with sentiment analysis
- **Free Tier**: 200 requests per month
- **Key Features**:
  - Real-time financial news
  - Symbol-specific news filtering
  - Sentiment analysis
  - Market movers identification
  - Multi-source news aggregation

## 🔧 Setup Instructions

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get API Keys

#### Alpha Vantage
1. Visit: https://www.alphavantage.co/support/#api-key
2. Sign up with email
3. Copy your free API key

#### FRED (Federal Reserve)
1. Visit: https://fred.stlouisfed.org/docs/api/api_key.html
2. Create an account
3. Request API key (instant approval)

#### MarketAux
1. Visit: https://www.marketaux.com/
2. Sign up for free account
3. Get API key from dashboard

### Step 3: Update Environment Variables
Add these to your `.env` file:
```env
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
FRED_API_KEY=your_fred_api_key_here
MARKETAUX_API_KEY=your_marketaux_api_key_here
```

### Step 4: Test the Integration
```bash
cd investment_agent
python api_test.py
```

## 🎯 Usage Examples

### Enhanced Stock Data
```python
from backend.data_fetch import get_enhanced_stock_data

# Get comprehensive stock information
stock_data = get_enhanced_stock_data('AAPL')
print(f"Price: ${stock_data['price']}")
print(f"P/E Ratio: {stock_data['company_overview']['pe_ratio']}")
print(f"Technical SMA: {stock_data['technical_indicators']['sma_20']}")
```

### Market Analysis with Economic Data
```python
from backend.market_analysis import analyze_market

# Get comprehensive market analysis
analysis = analyze_market()
print(f"Market Condition: {analysis['condition']}")
print(f"Risk Score: {analysis['risk_score']}/10")
print(f"Recommendation: {analysis['recommendation']}")
```

### News Sentiment Analysis
```python
from backend.data_fetch import get_enhanced_news_sentiment

# Get sentiment for specific stock
sentiment = get_enhanced_news_sentiment('TSLA')
print(f"Overall Sentiment: {sentiment['overall_sentiment']}")
print(f"Articles Analyzed: {sentiment['total_articles']}")
```

## 📊 API Comparison

| Feature | yfinance | Alpha Vantage | NewsAPI | MarketAux | FRED |
|---------|----------|---------------|---------|-----------|------|
| Stock Data | ✅ | ✅+ | ❌ | ❌ | ❌ |
| Company Info | ✅ | ✅+ | ❌ | ❌ | ❌ |
| Technical Indicators | ❌ | ✅ | ❌ | ❌ | ❌ |
| Economic Data | ❌ | ❌ | ❌ | ❌ | ✅ |
| News | ❌ | ❌ | ✅ | ✅+ | ❌ |
| Sentiment Analysis | ❌ | ❌ | ❌ | ✅ | ❌ |
| Rate Limits | High | 25/day | 1000/day | 200/month | None |
| Reliability | Medium | High | High | High | Very High |

## 🔄 Fallback Strategy

The system implements intelligent fallbacks:

1. **Stock Data**: yfinance → Alpha Vantage → Mock data
2. **News**: NewsAPI → MarketAux → Mock headlines
3. **Economic Data**: FRED → Mock indicators

## 🎨 Dashboard Integration

The APIs are integrated into your Streamlit dashboard through:

- `get_enhanced_stock_data()` - Shows comprehensive stock info
- `get_market_conditions()` - Displays economic indicators
- `get_enhanced_news_sentiment()` - Provides news sentiment analysis
- `analyze_market()` - Gives market condition assessment

## ⚡ Performance Tips

1. **Caching**: Implement caching for FRED data (updates daily)
2. **Rate Limiting**: Monitor Alpha Vantage usage (25 calls/day)
3. **Batch Requests**: Group related API calls
4. **Error Handling**: Always have fallbacks for API failures

## 🚨 Common Issues

### API Key Not Working
- Check if key is correctly set in `.env`
- Verify key hasn't expired
- Check API provider's status page

### Rate Limit Exceeded
- Alpha Vantage: Wait for daily reset
- MarketAux: Upgrade plan or optimize calls
- FRED: No limits (shouldn't happen)

### Import Errors
- Make sure new dependencies are installed
- Check Python path includes backend folder
- Verify `__init__.py` files exist

## 📈 Next Steps

1. **Test all APIs** with your keys
2. **Update dashboard** to use enhanced functions
3. **Monitor usage** to stay within limits
4. **Optimize calls** based on user patterns
5. **Add more indicators** as needed

## 🔗 API Documentation

- **Alpha Vantage**: https://www.alphavantage.co/documentation/
- **FRED**: https://fred.stlouisfed.org/docs/api/
- **MarketAux**: https://www.marketaux.com/documentation

## 💡 Pro Tips

- Use FRED data for macro analysis (free and reliable)
- Alpha Vantage for detailed stock fundamentals
- MarketAux for sentiment-driven insights
- Combine all three for comprehensive analysis
