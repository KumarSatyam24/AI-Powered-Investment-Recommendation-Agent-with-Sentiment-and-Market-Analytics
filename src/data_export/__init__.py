"""
Data Export Module
Provides CSV data export functionality for stock analysis and predictive modeling

This module exports comprehensive stock data including:
- Stock price and volume data
- Technical indicators (SMA, RSI, etc.)
- Sentiment analysis scores from multiple sources
- Fundamental company data
- Market context and economic indicators
- News article summaries and sentiment

Main Components:
- StockDataExporter: Core export functionality
- CSV generation with comprehensive datasets
- Metadata generation for ML model development
- Support for single and multiple stock analysis

Usage:
    from src.data_export import StockDataExporter
    
    exporter = StockDataExporter()
    csv_file = exporter.export_stock_data('AAPL', days=30)
"""

from .stock_data_exporter import StockDataExporter

__all__ = ['StockDataExporter']
