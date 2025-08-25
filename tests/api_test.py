"""
API Testing and Demo Script
Test all implemented APIs and show their capabilities.
"""

from src.api_clients.alpha_vantage_api import alpha_vantage
from src.api_clients.fred_api import fred_api
from src.api_clients.marketaux_api import marketaux_api
from src.data_processing.data_fetch import get_enhanced_stock_data, get_market_conditions, get_enhanced_news_sentiment
from src.analysis_engine.market_analysis import analyze_market, get_sector_analysis

def test_alpha_vantage():
    """Test Alpha Vantage API functionality."""
    print("\n🔹 Testing Alpha Vantage API...")
    print("-" * 50)
    
    # Test stock quote
    quote = alpha_vantage.get_stock_quote('AAPL')
    print(f"AAPL Quote: ${quote.get('price', 'N/A')}")
    print(f"Change: {quote.get('change', 'N/A')} ({quote.get('change_percent', 'N/A')})")
    
    # Test company overview
    overview = alpha_vantage.get_company_overview('AAPL')
    print(f"Company: {overview.get('name', 'N/A')}")
    print(f"Sector: {overview.get('sector', 'N/A')}")
    print(f"P/E Ratio: {overview.get('pe_ratio', 'N/A')}")
    print(f"Market Cap: {overview.get('market_cap', 'N/A')}")
    
    # Test technical indicators
    sma = alpha_vantage.get_technical_indicators('AAPL', 'SMA', 20)
    print(f"20-day SMA: {sma.get('latest_value', {}).get('SMA', 'N/A')}")

def test_fred_api():
    """Test FRED API functionality."""
    print("\n🔹 Testing FRED API...")
    print("-" * 50)
    
    # Test market indicators summary
    market_summary = fred_api.get_market_indicators_summary()
    print("Economic Indicators:")
    for indicator, data in market_summary['summary'].items():
        print(f"  {indicator.replace('_', ' ').title()}: {data.get('value', 'N/A')}")
    
    print(f"Market Condition: {market_summary.get('market_condition', 'Unknown')}")
    
    # Test individual indicators
    vix = fred_api.get_vix_index()
    print(f"VIX: {vix.get('latest_value', 'N/A')}")
    
    unemployment = fred_api.get_unemployment_rate()
    print(f"Unemployment Rate: {unemployment.get('latest_value', 'N/A')}%")

def test_marketaux_api():
    """Test MarketAux API functionality."""
    print("\n🔹 Testing MarketAux API...")
    print("-" * 50)
    
    # Test general market news
    news = marketaux_api.get_trending_news(limit=3)
    print("Latest Market News:")
    for i, article in enumerate(news.get('data', [])[:3], 1):
        print(f"  {i}. {article.get('title', 'N/A')}")
        print(f"     Sentiment: {article.get('sentiment', 'N/A')}")
    
    # Test symbol-specific news
    symbol_news = marketaux_api.get_news_by_symbol('AAPL', limit=2)
    print(f"\nAAPL-specific news ({symbol_news.get('total_articles', 0)} articles):")
    for article in symbol_news.get('data', [])[:2]:
        print(f"  - {article.get('title', 'N/A')}")
    
    # Test sentiment analysis
    sentiment = marketaux_api.get_news_sentiment_analysis(['AAPL'], days=7)
    print(f"\nAAPL Sentiment Analysis (7 days):")
    print(f"  Overall Sentiment: {sentiment.get('overall_sentiment', 'N/A')}")
    dist = sentiment.get('sentiment_distribution', {})
    print(f"  Positive: {dist.get('positive', 0):.1f}%")
    print(f"  Negative: {dist.get('negative', 0):.1f}%")
    print(f"  Neutral: {dist.get('neutral', 0):.1f}%")

def test_enhanced_functions():
    """Test enhanced data fetching functions."""
    print("\n🔹 Testing Enhanced Functions...")
    print("-" * 50)
    
    # Test enhanced stock data
    stock_data = get_enhanced_stock_data('AAPL')
    print(f"Enhanced AAPL Data:")
    print(f"  Price: ${stock_data.get('price', 'N/A')}")
    print(f"  P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}")
    print(f"  Data Source: {stock_data.get('data_source', 'N/A')}")
    
    # Test market conditions
    market_conditions = get_market_conditions()
    print(f"\nMarket Conditions:")
    print(f"  Overall: {market_conditions.get('market_condition', 'N/A')}")
    print(f"  VIX: {market_conditions['detailed_data'].get('vix', 'N/A')}")
    print(f"  Inflation: {market_conditions['detailed_data'].get('inflation', 'N/A')}")
    
    # Test enhanced news sentiment
    news_sentiment = get_enhanced_news_sentiment('AAPL')
    print(f"\nEnhanced News Sentiment for AAPL:")
    print(f"  Overall: {news_sentiment.get('overall_sentiment', 'N/A')}")
    print(f"  Articles analyzed: {news_sentiment.get('total_articles', 0)}")
    print("  Recent headlines:")
    for headline in news_sentiment.get('headlines', [])[:3]:
        print(f"    - {headline}")

def test_market_analysis():
    """Test enhanced market analysis."""
    print("\n🔹 Testing Enhanced Market Analysis...")
    print("-" * 50)
    
    # Test market analysis
    analysis = analyze_market()
    print(f"Market Analysis:")
    print(f"  Condition: {analysis.get('condition', 'N/A')}")
    print(f"  Risk Score: {analysis.get('risk_score', 0)}/10")
    print(f"  Recommendation: {analysis.get('recommendation', 'N/A')}")
    print("  Risk Details:")
    for detail in analysis.get('risk_details', []):
        print(f"    - {detail}")
    
    # Test sector analysis
    tech_analysis = get_sector_analysis('technology')
    print(f"\nTechnology Sector Analysis:")
    print(f"  Outlook: {tech_analysis.get('outlook', 'N/A')}")

def run_all_tests():
    """Run all API tests."""
    print("🚀 API Integration Testing Suite")
    print("=" * 60)
    
    try:
        test_alpha_vantage()
    except Exception as e:
        print(f"❌ Alpha Vantage test failed: {e}")
    
    try:
        test_fred_api()
    except Exception as e:
        print(f"❌ FRED API test failed: {e}")
    
    try:
        test_marketaux_api()
    except Exception as e:
        print(f"❌ MarketAux API test failed: {e}")
    
    try:
        test_enhanced_functions()
    except Exception as e:
        print(f"❌ Enhanced functions test failed: {e}")
    
    try:
        test_market_analysis()
    except Exception as e:
        print(f"❌ Market analysis test failed: {e}")
    
    print("\n✅ Testing completed!")
    print("\n📝 Next Steps:")
    print("1. Get API keys from:")
    print("   - Alpha Vantage: https://www.alphavantage.co/support/#api-key")
    print("   - FRED: https://fred.stlouisfed.org/docs/api/api_key.html")
    print("   - MarketAux: https://www.marketaux.com/")
    print("2. Update your .env file with the actual API keys")
    print("3. Install new dependencies: pip install -r requirements.txt")
    print("4. Test individual APIs by calling specific test functions")

if __name__ == "__main__":
    run_all_tests()
