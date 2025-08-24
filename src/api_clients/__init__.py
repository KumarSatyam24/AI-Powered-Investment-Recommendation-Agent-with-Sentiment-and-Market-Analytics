"""
API Clients Package
===================

This package contains all external API client implementations for the investment system.
"""

from .alpha_vantage_api import AlphaVantageAPI as AlphaVantageClient
from .fred_api import FREDAPI as FREDClient  
from .marketaux_api import MarketAuxAPI as MarketAuxClient

__all__ = ['AlphaVantageClient', 'FREDClient', 'MarketAuxClient']
