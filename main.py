#!/usr/bin/env python3
"""
Investment Recommendation System - Main Application
==================================================

Entry point for the AI-Powered Investment Recommendation Agent.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.data_processing.data_fetch import get_enhanced_stock_data, get_market_conditions, get_enhanced_news_sentiment
from src.analysis_engine.market_analysis import analyze_market
from src.analysis_engine.recommendations import generate_recommendation
from src.sentiment_analysis.enhanced_fusion import enhanced_sentiment_analysis

class InvestmentRecommendationSystem:
    """Main system class for investment analysis and recommendations."""
    
    def __init__(self):
        self.name = "AI Investment Recommendation Agent"
        self.version = "2.0.0"
    
    def analyze_stock(self, ticker: str) -> dict:
        """
        Perform comprehensive stock analysis.
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Complete analysis results dictionary
        """
        print(f"🔍 Analyzing {ticker}...")
        
        # Get stock data
        stock_data = get_enhanced_stock_data(ticker)
        
        # Get market conditions
        market_data = get_market_conditions()
        
        # Get enhanced sentiment
        sentiment_data = enhanced_sentiment_analysis(ticker)
        
        # Generate recommendation
        sentiment_score = "Positive" if sentiment_data["overall_sentiment"] in ["bullish", "positive"] else "Negative" if sentiment_data["overall_sentiment"] in ["bearish", "negative"] else "Neutral"
        risk_level = "High" if market_data.get('detailed_data', {}).get('vix', 20) > 25 else "Low"
        
        recommendation = generate_recommendation(sentiment_score, risk_level)
        
        return {
            'ticker': ticker,
            'stock_data': stock_data,
            'market_conditions': market_data,
            'sentiment_analysis': sentiment_data,
            'recommendation': recommendation,
            'analysis_timestamp': os.popen('date').read().strip()
        }
    
    def get_system_status(self) -> dict:
        """Get system status and API health."""
        return {
            'system': self.name,
            'version': self.version,
            'status': 'operational',
            'apis': {
                'alpha_vantage': 'configured',
                'fred': 'configured', 
                'marketaux': 'configured'
            }
        }

def main():
    """Main function for command line usage."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <STOCK_TICKER>")
        print("Example: python main.py AAPL")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    
    # Initialize system
    system = InvestmentRecommendationSystem()
    
    # Perform analysis
    try:
        results = system.analyze_stock(ticker)
        
        print(f"\n{'='*50}")
        print(f"📊 INVESTMENT ANALYSIS REPORT FOR {ticker}")
        print(f"{'='*50}")
        
        print(f"\n💰 Stock Information:")
        print(f"  Price: ${results['stock_data']['price']}")
        print(f"  P/E Ratio: {results['stock_data']['pe_ratio']}")
        print(f"  Volume: {results['stock_data']['volume']:,}")
        
        print(f"\n📈 Market Conditions:")
        print(f"  Overall: {results['market_conditions']['market_condition']}")
        print(f"  VIX: {results['market_conditions']['detailed_data'].get('vix', 'N/A')}")
        
        print(f"\n🧠 Sentiment Analysis:")
        print(f"  Overall Sentiment: {results['sentiment_analysis']['overall_sentiment']}")
        print(f"  Confidence: {results['sentiment_analysis']['confidence_score']:.2f}")
        print(f"  Sources: {results['sentiment_analysis']['analysis_details']['total_sources']}")
        
        print(f"\n🎯 AI Recommendation:")
        print(f"  {results['recommendation']}")
        
        print(f"\n⏰ Analysis completed at: {results['analysis_timestamp']}")
        
    except Exception as e:
        print(f"❌ Error analyzing {ticker}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
