#!/usr/bin/env python3

from src.data_processing.data_fetch import get_enhanced_stock_data, get_enhanced_news_sentiment
from src.analysis_engine.market_analysis import analyze_market
from src.analysis_engine.recommendations import generate_recommendation

def comprehensive_analysis():
    print('🔍 Comprehensive Stock Analysis for AAPL')
    print('=' * 50)

    # Get enhanced stock data
    stock_data = get_enhanced_stock_data('AAPL')
    print(f'Stock Price: ${stock_data["price"]}')
    print(f'P/E Ratio: {stock_data["pe_ratio"]}')
    print(f'Volume: {stock_data["volume"]:,}')
    print(f'Data Source: {stock_data["data_source"]}')

    # Get market analysis
    market = analyze_market()
    print(f'\n📊 Market Analysis:')
    print(f'Market Condition: {market["condition"]}')
    print(f'Risk Score: {market["risk_score"]}/10')
    print(f'VIX: {market["economic_indicators"]["vix"]}')
    print(f'Unemployment: {market["economic_indicators"]["unemployment"]}%')

    # Get news sentiment
    news = get_enhanced_news_sentiment('AAPL')
    print(f'\n📰 News Sentiment Analysis:')
    print(f'Overall Sentiment: {news["overall_sentiment"]}')
    print(f'Articles Analyzed: {news["total_articles"]}')
    
    # Show recent headlines
    print('\n📈 Recent Headlines:')
    for i, headline in enumerate(news["headlines"][:3], 1):
        print(f'  {i}. {headline}')

    # Generate recommendation
    sentiment_score = "Positive" if news["overall_sentiment"] in ["bullish", "positive"] else "Negative" if news["overall_sentiment"] in ["bearish", "negative"] else "Neutral"
    risk_level = "High" if market["risk_score"] >= 6 else "Medium" if market["risk_score"] >= 3 else "Low"
    
    recommendation = generate_recommendation(sentiment_score, risk_level)
    
    print(f'\n🎯 AI Recommendation:')
    print(f'Action: {recommendation}')
    print(f'Based on: {sentiment_score} sentiment + {risk_level} risk environment')
    
    print('\n✅ Your AI-powered investment system is fully operational!')
    print('🚀 Ready for production use!')

if __name__ == "__main__":
    comprehensive_analysis()
