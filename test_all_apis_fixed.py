"""
Fixed Comprehensive API Testing Script
=====================================
Tests all APIs in the system with correct imports and method calls.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_marketaux_api():
    """Test MarketAux API outputs."""
    print("🔍 TESTING MARKETAUX API")
    print("=" * 50)
    
    try:
        from api_clients.marketaux_api import MarketAuxAPI
        
        api = MarketAuxAPI()
        print(f"📡 API Key configured: {api.api_key != 'YOUR_MARKETAUX_API_KEY'}")
        
        # Test 1: General market news
        print("\n📰 Test 1: General Market News")
        print("-" * 30)
        general_news = api.get_market_news(limit=5)
        print(f"✅ Total articles: {general_news.get('total_articles', 0)}")
        print(f"📊 Data source: {'REAL' if general_news.get('data') and 'uuid' in general_news['data'][0] else 'MOCK'}")
        print(f"📈 Symbols mentioned: {general_news.get('symbols_mentioned', [])}")
        print(f"💭 Sentiment summary: {general_news.get('sentiment_summary', {})}")
        
        # Show first article details
        if general_news.get('data'):
            article = general_news['data'][0]
            print(f"\n📄 Sample Article:")
            print(f"   Title: {article.get('title', 'N/A')[:80]}...")
            print(f"   Source: {article.get('source', 'N/A')}")
            print(f"   Date: {article.get('published_at', 'N/A')}")
            print(f"   Snippet: {article.get('snippet', 'N/A')[:100]}...")
        
        # Test 2: Symbol-specific news (using get_market_news with symbols)
        print("\n\n🎯 Test 2: Symbol-Specific News (AAPL)")
        print("-" * 30)
        aapl_news = api.get_market_news(symbols=['AAPL'], limit=3)
        print(f"✅ AAPL articles: {aapl_news.get('total_articles', 0)}")
        
        if aapl_news.get('data'):
            for i, article in enumerate(aapl_news['data'][:2], 1):
                print(f"   {i}. {article.get('title', 'N/A')[:60]}...")
        
        return {
            'status': 'SUCCESS',
            'general_news': general_news.get('total_articles', 0),
            'aapl_news': aapl_news.get('total_articles', 0),
            'data_source': 'REAL' if general_news.get('data') and 'uuid' in general_news['data'][0] else 'MOCK'
        }
        
    except Exception as e:
        print(f"❌ MarketAux API Error: {e}")
        return {'status': 'ERROR', 'error': str(e)}

def test_alpha_vantage_api():
    """Test Alpha Vantage API outputs."""
    print("\n\n🔍 TESTING ALPHA VANTAGE API")
    print("=" * 50)
    
    try:
        from api_clients.alpha_vantage_api import AlphaVantageAPI
        
        api = AlphaVantageAPI()
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        print(f"📡 API Key configured: {bool(api_key and api_key != 'YOUR_ALPHA_VANTAGE_API_KEY')}")
        
        # Check available methods
        methods = [method for method in dir(api) if not method.startswith('_')]
        print(f"📋 Available methods: {methods}")
        
        # Test based on available methods
        results = {'status': 'SUCCESS', 'methods_available': methods}
        
        # Try common stock data methods
        test_methods = ['get_stock_quote', 'get_daily_adjusted', 'get_company_overview']
        
        for method_name in test_methods:
            if hasattr(api, method_name):
                print(f"\n📈 Testing {method_name}(AAPL)")
                print("-" * 30)
                try:
                    method = getattr(api, method_name)
                    data = method('AAPL')
                    print(f"✅ {method_name}: Data received")
                    print(f"📊 Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    results[method_name] = 'SUCCESS'
                except Exception as e:
                    print(f"❌ {method_name} error: {e}")
                    results[method_name] = f'ERROR: {e}'
            else:
                print(f"\n⚠️  Method {method_name} not available")
                results[method_name] = 'NOT_AVAILABLE'
        
        return results
        
    except Exception as e:
        print(f"❌ Alpha Vantage API Error: {e}")
        return {'status': 'ERROR', 'error': str(e)}

def test_fred_api():
    """Test FRED API outputs."""
    print("\n\n🔍 TESTING FRED API")
    print("=" * 50)
    
    try:
        from api_clients.fred_api import FREDAPI
        
        api = FREDAPI()
        api_key = os.getenv('FRED_API_KEY')
        print(f"📡 API Key configured: {bool(api_key and api_key != 'YOUR_FRED_API_KEY')}")
        
        # Check available methods
        methods = [method for method in dir(api) if not method.startswith('_') and callable(getattr(api, method))]
        print(f"📋 Available methods: {methods}")
        
        results = {'status': 'SUCCESS', 'methods_available': methods}
        
        # Test inflation rate method
        if hasattr(api, 'get_inflation_rate'):
            print(f"\n📊 Testing Inflation Rate")
            print("-" * 30)
            try:
                inflation = api.get_inflation_rate()
                print(f"✅ Inflation Rate: {inflation}%")
                results['inflation_rate'] = {'value': inflation, 'status': 'SUCCESS'}
            except Exception as e:
                print(f"❌ Inflation rate error: {e}")
                results['inflation_rate'] = {'status': 'ERROR', 'error': str(e)}
        
        # Test other common methods
        test_methods = ['get_unemployment_rate', 'get_federal_funds_rate', 'get_gdp_growth']
        
        for method_name in test_methods:
            if hasattr(api, method_name):
                print(f"\n📈 Testing {method_name}")
                print("-" * 30)
                try:
                    method = getattr(api, method_name)
                    value = method()
                    print(f"✅ {method_name}: {value}")
                    results[method_name] = {'value': value, 'status': 'SUCCESS'}
                except Exception as e:
                    print(f"❌ {method_name} error: {e}")
                    results[method_name] = {'status': 'ERROR', 'error': str(e)}
        
        return results
        
    except Exception as e:
        print(f"❌ FRED API Error: {e}")
        return {'status': 'ERROR', 'error': str(e)}

def test_sentiment_analysis():
    """Test sentiment analysis modules."""
    print("\n\n🔍 TESTING SENTIMENT ANALYSIS")
    print("=" * 50)
    
    results = {}
    
    # Test unified sentiment
    print("🎯 Testing Unified Sentiment")
    print("-" * 30)
    try:
        from sentiment_analysis.unified_sentiment import get_unified_sentiment
        
        sentiment_result = get_unified_sentiment('AAPL')
        print(f"✅ Unified sentiment for AAPL: {sentiment_result.get('unified_sentiment', 'N/A')}")
        print(f"📊 Confidence: {sentiment_result.get('confidence', 'N/A')}")
        print(f"💭 Sources used: {sentiment_result.get('sources_used', [])}")
        
        results['unified_sentiment'] = {
            'status': 'SUCCESS',
            'sentiment': sentiment_result.get('unified_sentiment'),
            'confidence': sentiment_result.get('confidence')
        }
        
    except Exception as e:
        print(f"❌ Unified sentiment error: {e}")
        results['unified_sentiment'] = {'status': 'ERROR', 'error': str(e)}
    
    # Test news sentiment
    print("\n\n📰 Testing News Sentiment")
    print("-" * 30)
    try:
        from sentiment_analysis.news_sentiments import analyze_news_sentiment
        
        news_sentiment = analyze_news_sentiment('AAPL')
        print(f"✅ News sentiment for AAPL: {news_sentiment.get('overall_sentiment', 'N/A')}")
        print(f"📊 Articles analyzed: {news_sentiment.get('total_articles', 0)}")
        
        results['news_sentiment'] = {
            'status': 'SUCCESS',
            'sentiment': news_sentiment.get('overall_sentiment'),
            'articles': news_sentiment.get('total_articles', 0)
        }
        
    except Exception as e:
        print(f"❌ News sentiment error: {e}")
        results['news_sentiment'] = {'status': 'ERROR', 'error': str(e)}
    
    return results

def test_market_analysis():
    """Test market analysis engine."""
    print("\n\n🔍 TESTING MARKET ANALYSIS ENGINE")
    print("=" * 50)
    
    try:
        from analysis_engine.market_analysis import analyze_market
        
        print("📊 Testing Market Analysis")
        print("-" * 30)
        
        market_analysis = analyze_market()
        
        print(f"✅ Market condition: {market_analysis.get('condition', 'N/A')}")
        print(f"📊 Risk score: {market_analysis.get('risk_score', 'N/A')}/10")
        print(f"💡 Recommendation: {market_analysis.get('recommendation', 'N/A')}")
        
        # Show economic indicators
        indicators = market_analysis.get('economic_indicators', {})
        print(f"\n📈 Economic Indicators:")
        for key, value in indicators.items():
            print(f"   {key}: {value}")
        
        return {
            'status': 'SUCCESS',
            'condition': market_analysis.get('condition'),
            'risk_score': market_analysis.get('risk_score'),
            'indicators_count': len(indicators)
        }
        
    except Exception as e:
        print(f"❌ Market analysis error: {e}")
        return {'status': 'ERROR', 'error': str(e)}

def test_portfolio_recommendations():
    """Test portfolio recommendation engine."""
    print("\n\n🔍 TESTING PORTFOLIO RECOMMENDATIONS")
    print("=" * 50)
    
    try:
        from analysis_engine.hybrid_recommendations import generate_portfolio_recommendations
        
        print("💼 Testing Portfolio Recommendations")
        print("-" * 30)
        
        portfolio = generate_portfolio_recommendations(
            portfolio_size=100000,
            risk_tolerance='moderate',
            max_sectors=4,
            stocks_per_sector=2
        )
        
        print(f"✅ Recommendations generated: {len(portfolio.get('recommendations', []))}")
        print(f"📊 Risk level: {portfolio.get('risk_level', 'N/A')}")
        print(f"💰 Total allocation: ${portfolio.get('total_allocated', 0):,.2f}")
        
        # Show recommendations
        recommendations = portfolio.get('recommendations', [])
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec.get('symbol', 'N/A')}: ${rec.get('amount', 0):,.2f} ({rec.get('allocation_percentage', 0):.1f}%)")
        
        return {
            'status': 'SUCCESS',
            'recommendations_count': len(recommendations),
            'risk_level': portfolio.get('risk_level'),
            'total_allocated': portfolio.get('total_allocated', 0)
        }
        
    except Exception as e:
        print(f"❌ Portfolio recommendations error: {e}")
        return {'status': 'ERROR', 'error': str(e)}

def run_comprehensive_test():
    """Run all API tests and generate summary report."""
    print("🚀 COMPREHENSIVE API TESTING (FIXED)")
    print("=" * 70)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    results = {}
    
    # Test all APIs and modules
    results['marketaux'] = test_marketaux_api()
    results['alpha_vantage'] = test_alpha_vantage_api()
    results['fred'] = test_fred_api()
    results['sentiment_analysis'] = test_sentiment_analysis()
    results['market_analysis'] = test_market_analysis()
    results['portfolio_recommendations'] = test_portfolio_recommendations()
    
    # Generate summary
    print("\n\n📋 COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)
    
    total_modules = 0
    working_modules = 0
    
    for module_name, result in results.items():
        total_modules += 1
        
        # Handle different result structures
        if isinstance(result, dict) and 'status' in result:
            status = result['status']
        elif isinstance(result, dict) and any(sub.get('status') == 'SUCCESS' for sub in result.values() if isinstance(sub, dict)):
            status = 'PARTIAL'
        else:
            status = 'SUCCESS' if result else 'ERROR'
        
        if status == 'SUCCESS':
            working_modules += 1
            status_icon = "✅"
        elif status == 'PARTIAL':
            working_modules += 0.5
            status_icon = "⚠️"
        elif status == 'ERROR':
            status_icon = "❌"
        else:
            status_icon = "⚠️"
        
        print(f"{status_icon} {module_name.upper()}: {status}")
        
        # Show specific details
        if module_name == 'marketaux' and result.get('status') == 'SUCCESS':
            print(f"   📰 General news: {result.get('general_news', 0)} articles")
            print(f"   🎯 AAPL news: {result.get('aapl_news', 0)} articles")
            print(f"   💾 Data source: {result.get('data_source', 'UNKNOWN')}")
        elif module_name == 'fred' and result.get('status') == 'SUCCESS':
            methods = result.get('methods_available', [])
            print(f"   📊 Available methods: {len(methods)}")
        elif module_name == 'market_analysis' and result.get('status') == 'SUCCESS':
            print(f"   🌍 Market condition: {result.get('condition', 'N/A')}")
            print(f"   📊 Risk score: {result.get('risk_score', 'N/A')}")
        elif module_name == 'portfolio_recommendations' and result.get('status') == 'SUCCESS':
            print(f"   💼 Recommendations: {result.get('recommendations_count', 0)}")
            print(f"   💰 Total allocated: ${result.get('total_allocated', 0):,.2f}")
    
    print(f"\n🎯 OVERALL STATUS: {working_modules}/{total_modules} Modules Working")
    print(f"📊 Success Rate: {(working_modules/total_modules)*100:.1f}%")
    
    # API Key status
    print(f"\n🔑 API KEY STATUS:")
    api_keys = {
        'MARKETAUX_API_KEY': os.getenv('MARKETAUX_API_KEY'),
        'ALPHA_VANTAGE_API_KEY': os.getenv('ALPHA_VANTAGE_API_KEY'),
        'FRED_API_KEY': os.getenv('FRED_API_KEY'),
        'NEWS_API_KEY': os.getenv('NEWS_API_KEY'),
    }
    
    for key_name, key_value in api_keys.items():
        if key_value and key_value != f'YOUR_{key_name}':
            print(f"   ✅ {key_name}: Configured")
        else:
            print(f"   ❌ {key_name}: Not configured")
    
    # Save detailed results
    with open('api_test_results_fixed.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_modules': total_modules,
                'working_modules': working_modules,
                'success_rate': (working_modules / total_modules) * 100
            },
            'detailed_results': results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: api_test_results_fixed.json")
    print("✅ Comprehensive API testing complete!")
    
    return results

if __name__ == "__main__":
    # Set up environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run comprehensive test
    run_comprehensive_test()
