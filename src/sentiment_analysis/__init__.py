"""
Sentiment Analysis Package
==========================

Multi-source sentiment analysis for financial data including:
- News sentiment analysis with FinBERT
- Social media sentiment (Reddit, Twitter)
- Enhanced fusion algorithms
"""

from .sentiment_model import analyze_sentiment
from .enhanced_fusion import enhanced_sentiment_analysis, get_sentiment_summary
from .fusion import fuse_sentiments

__all__ = [
    'analyze_sentiment',
    'enhanced_sentiment_analysis', 
    'get_sentiment_summary',
    'fuse_sentiments'
]
