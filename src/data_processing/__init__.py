"""
Data Processing Package
=======================

Data fetching, processing, and transformation utilities.
"""

from .data_fetch import (
    get_stock_data,
    get_enhanced_stock_data,
    get_market_conditions,
    get_latest_headlines,
    get_enhanced_news_sentiment,
    get_reddit_posts,
    get_tweets
)

class DataProcessor:
    """Main data processing class."""
    pass

__all__ = [
    'DataProcessor',
    'get_stock_data',
    'get_enhanced_stock_data', 
    'get_market_conditions',
    'get_latest_headlines',
    'get_enhanced_news_sentiment'
]
