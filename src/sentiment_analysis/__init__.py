"""
Sentiment Analysis Package
==========================

Optimized multi-source sentiment analysis for financial data including:
- Advanced news sentiment analysis with FinBERT
- Social media sentiment (Reddit, Twitter)  
- Unified sentiment analysis system
"""

from .news_sentiments import (
    analyze_comprehensive_news_sentiment_advanced,
    analyze_comprehensive_news_sentiment,
    analyze_news_sentiment
)
from .unified_sentiment import UnifiedSentimentAnalyzer

__all__ = [
    'analyze_comprehensive_news_sentiment_advanced',
    'analyze_comprehensive_news_sentiment',
    'analyze_news_sentiment',
    'UnifiedSentimentAnalyzer'
]
