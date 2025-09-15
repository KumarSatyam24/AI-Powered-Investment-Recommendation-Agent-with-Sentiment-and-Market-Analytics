# Comprehensive API Integration Guide

This guide provides a complete overview of all APIs integrated into the AI-Powered Investment Recommendation System. It covers setup, usage, fallback strategies, and performance tips for the 6 primary data sources.

## 🚀 Integrated APIs

### 1. Alpha Vantage API
- **Purpose**: Core stock data, company fundamentals, and technical indicators.
- **Free Tier**: 25 requests per day.
- **Key Features**:
  - Real-time and historical stock prices.
  - Company fundamentals (P/E, EPS, Market Cap).
  - Technical indicators (SMA, EMA, RSI, MACD).

### 2. FRED API (Federal Reserve Economic Data)
- **Purpose**: Macroeconomic indicators for market analysis.
- **Free Tier**: No rate limits.
- **Key Features**:
  - Inflation rates (CPI) for YoY calculation.
  - Unemployment data, Federal Funds Rate, GDP.
  - VIX (Volatility Index) and Treasury rates.

### 3. NewsAPI
- **Purpose**: Primary source for real-time financial news.
- **Free Tier**: 100 requests per day.
- **Key Features**:
  - Global news from over 70,000 sources.
  - Symbol-specific and general market news.
  - Used as the primary news source in the sentiment engine.

### 4. MarketAux API
- **Purpose**: Secondary news source and fallback for NewsAPI.
- **Free Tier**: 10,000 requests per month.
- **Key Features**:
  - Real-time financial news with built-in sentiment.
  - High-quality data, serves as a robust fallback.
  - Ensures news coverage if NewsAPI hits its rate limit.

### 5. Twitter & Reddit APIs (via Libraries)
- **Purpose**: Social media sentiment analysis.
- **Setup**: Requires developer accounts and API keys for both platforms.
- **Key Features**:
  - Real-time sentiment from retail investors and the public.
  - Crucial for the Unified Sentiment score (30% weight each).
  - Captures market hype and grassroots trends.

### 6. Grok AI API
- **Purpose**: Advanced, context-aware sentiment analysis.
- **Usage**: Serves as an intelligent fallback for the sentiment engine.
- **Key Features**:
  - Provides nuanced sentiment when traditional models are uncertain.
  - Understands complex financial language and context.
  - Enhances the reliability of the overall sentiment score.

## 🔧 Setup Instructions

### Step 1: Install Dependencies
Ensure all dependencies are installed from the project's `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Step 2: Get API Keys
You will need to acquire API keys from the following services:
- **Alpha Vantage**: [alphavantage.co](https://www.alphavantage.co/support/#api-key)
- **FRED**: [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html)
- **NewsAPI**: [newsapi.org](https://newsapi.org/s/google-news-api)
- **MarketAux**: [marketaux.com](https://www.marketaux.com/)
- **Twitter**: [developer.twitter.com](https://developer.twitter.com/en/portal/dashboard)
- **Reddit**: [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
- **Grok AI**: From your Grok account dashboard.

### Step 3: Update Environment Variables
Create or update your `.env` file with all the required keys:
```env
# Financial Data
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Economic Data
FRED_API_KEY=your_fred_api_key

# News APIs
NEWS_API_KEY=your_newsapi_key
MARKETAUX_API_KEY=your_marketaux_key

# Social Media APIs
TWITTER_CONSUMER_KEY=your_twitter_consumer_key
TWITTER_CONSUMER_SECRET=your_twitter_consumer_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_reddit_user_agent

# AI Model API
GROK_API_KEY=your_grok_api_key
```

### Step 4: Test the Integration
Run the full test suite to ensure all APIs are configured correctly:
```bash
python tests/full_test.py
```

## 🎯 Core System Integrations

### Unified Sentiment Analysis
The system fuses sentiment from multiple sources into a single, weighted score:
- **News Sentiment (40%)**: From NewsAPI & MarketAux, analyzed by FinBERT.
- **Twitter Sentiment (30%)**: Real-time tweets.
- **Reddit Sentiment (30%)**: Posts and comments from financial subreddits.
- **Grok AI Fallback**: Used when confidence is low.

```python
from src.sentiment_analysis.unified_sentiment import get_unified_sentiment

# Get the fused sentiment score for a stock
unified_score = get_unified_sentiment('TSLA')
print(f"Unified Sentiment Score for TSLA: {unified_score['unified_sentiment']:.3f}")
```

### Market Analysis with Economic Data
The FRED API powers the `analyze_market` function, providing real-world economic context.
```python
from src.analysis_engine.market_analysis import analyze_market

# Get comprehensive market analysis
analysis = analyze_market()
print(f"Market Condition: {analysis['condition']}")
print(f"Risk Score: {analysis['risk_score']}/10")
print(f"YoY Inflation: {analysis['economic_indicators']['inflation']}%")
```

## 📊 API Comparison

| Feature | Alpha Vantage | FRED | NewsAPI | MarketAux | Twitter/Reddit | Grok AI |
|----------------------|---------------|------|---------|-----------|----------------|---------|
| **Stock Data** | ✅ (Primary) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Economic Data** | ❌ | ✅ (Primary) | ❌ | ❌ | ❌ | ❌ |
| **News** | ❌ | ❌ | ✅ (Primary) | ✅ (Fallback) | ❌ | ❌ |
| **Social Sentiment** | ❌ | ❌ | ❌ | ❌ | ✅ (Primary) | ❌ |
| **Advanced Sentiment** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (Fallback) |
| **Rate Limits** | Low | None | Medium | High | Medium | Varies |
| **Reliability** | High | Very High | High | High | Medium | High |

## 🔄 Fallback & Redundancy Strategy

The system is designed for high availability with an intelligent fallback chain:

1.  **News Data**:
    - **Primary**: `NewsAPI`
    - **Fallback**: `MarketAux`
    - **Failure**: Proceeds with social media sentiment only.

2.  **Sentiment Analysis**:
    - **Primary**: `FinBERT` model on News, Twitter, and Reddit data.
    - **Fallback**: `Grok AI` is triggered if FinBERT's confidence is low or sources are unavailable.
    - **Failure**: A neutral sentiment score is assumed.

3.  **Market & Sector Analysis**:
    - **Primary**: Analysis based on available news and sentiment.
    - **Fallback**: If no trending sectors are found, the system recommends a diversified ETF portfolio (`SPY`, `QQQ`, `BND`).

## ⚡ Performance & Optimization

1.  **Caching**: API responses, especially for less volatile data like economic indicators, are cached to reduce redundant calls.
2.  **Asynchronous Calls**: `asyncio` is used to fetch data from multiple APIs concurrently, significantly speeding up analysis.
3.  **Rate Limit Handling**: The system includes built-in error handling to gracefully manage API rate limits.
4.  **Selective Loading**: Only necessary data points are requested from APIs to minimize payload size and processing time.

## 🚨 Common Issues & Solutions

### API Key Errors
- **Symptom**: `401 Unauthorized` or `Invalid Key` errors.
- **Solution**: Double-check that the correct API keys are in your `.env` file and that there are no extra spaces or characters. Ensure the `.env` file is in the project's root directory.

### Rate Limit Exceeded
- **Symptom**: `429 Too Many Requests` errors.
- **Solution**: This is expected with free-tier keys. The system is designed to handle this, but for extensive use, consider upgrading keys for NewsAPI and Alpha Vantage.

### Import Errors
- **Symptom**: `ModuleNotFoundError`.
- **Solution**:
    - Ensure you have run `pip install -r requirements.txt`.
    - Verify your Python interpreter is selected for the project's virtual environment.
    - Check that `__init__.py` files exist in all necessary directories.

## 🔗 Official API Documentation

- **Alpha Vantage**: https://www.alphavantage.co/documentation/
- **FRED**: https://fred.stlouisfed.org/docs/api/
- **NewsAPI**: https://newsapi.org/docs
- **MarketAux**: https://www.marketaux.com/documentation
- **Grok AI**: Provided with your developer account.
- **Twitter**: https://developer.twitter.com/en/docs
- **PRAW (for Reddit)**: https://praw.readthedocs.io/en/stable/

---

## 📚 Related Documentation

- 🏠 [**Main README**](../README.md) - Project overview and quick start
- 📋 [**Documentation Index**](INDEX.md) - Complete documentation navigation
- 🧪 [**API Testing Guide**](API_TESTING_GUIDE.md) - Test your API setup
- 🏗️ [**Implementation Summary**](IMPLEMENTATION_SUMMARY.md) - Technical details
- 📊 [**Project Documentation**](PROJECT_DOCUMENTATION.md) - Complete system overview

<div align="center">

[🏠 Back to Index](INDEX.md) | [🧪 Test APIs](API_TESTING_GUIDE.md) | [🏗️ Implementation](IMPLEMENTATION_SUMMARY.md)

</div>
