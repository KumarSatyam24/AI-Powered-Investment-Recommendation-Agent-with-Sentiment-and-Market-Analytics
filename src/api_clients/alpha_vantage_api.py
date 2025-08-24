import requests
import pandas as pd
from typing import Dict, Optional, List
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ALPHA_VANTAGE_KEY

class AlphaVantageAPI:
    """Alpha Vantage API client for stock data and financial information."""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self):
        self.api_key = ALPHA_VANTAGE_KEY
        self.session = requests.Session()
    
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Make API request with rate limiting."""
        if not self.api_key or self.api_key == "YOUR_ALPHA_VANTAGE_KEY":
            print("Alpha Vantage API key not configured. Using mock data.")
            return None
        
        params['apikey'] = self.api_key
        
        try:
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for API error messages
            if "Error Message" in data:
                print(f"Alpha Vantage API Error: {data['Error Message']}")
                return None
            elif "Note" in data:
                print(f"Alpha Vantage API Note: {data['Note']}")
                time.sleep(60)  # Rate limit exceeded, wait
                return None
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error making Alpha Vantage API request: {e}")
            return None
    
    def get_stock_quote(self, symbol: str) -> Dict:
        """Get real-time stock quote."""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }
        
        data = self._make_request(params)
        if not data:
            return self._get_mock_quote(symbol)
        
        try:
            quote = data['Global Quote']
            return {
                'symbol': quote['01. symbol'],
                'price': float(quote['05. price']),
                'change': float(quote['09. change']),
                'change_percent': quote['10. change percent'].rstrip('%'),
                'volume': int(quote['06. volume']),
                'open': float(quote['02. open']),
                'high': float(quote['03. high']),
                'low': float(quote['04. low']),
                'previous_close': float(quote['08. previous close']),
                'latest_trading_day': quote['07. latest trading day']
            }
        except (KeyError, ValueError) as e:
            print(f"Error parsing Alpha Vantage quote data: {e}")
            return self._get_mock_quote(symbol)
    
    def get_company_overview(self, symbol: str) -> Dict:
        """Get company fundamental data."""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        
        data = self._make_request(params)
        if not data:
            return self._get_mock_overview(symbol)
        
        try:
            return {
                'symbol': data.get('Symbol', symbol),
                'name': data.get('Name', 'N/A'),
                'description': data.get('Description', 'N/A'),
                'sector': data.get('Sector', 'N/A'),
                'industry': data.get('Industry', 'N/A'),
                'market_cap': data.get('MarketCapitalization', 'N/A'),
                'pe_ratio': data.get('PERatio', 'N/A'),
                'peg_ratio': data.get('PEGRatio', 'N/A'),
                'book_value': data.get('BookValue', 'N/A'),
                'dividend_per_share': data.get('DividendPerShare', 'N/A'),
                'dividend_yield': data.get('DividendYield', 'N/A'),
                'eps': data.get('EPS', 'N/A'),
                'revenue_ttm': data.get('RevenueTTM', 'N/A'),
                'profit_margin': data.get('ProfitMargin', 'N/A'),
                'operating_margin': data.get('OperatingMarginTTM', 'N/A'),
                'return_on_assets': data.get('ReturnOnAssetsTTM', 'N/A'),
                'return_on_equity': data.get('ReturnOnEquityTTM', 'N/A'),
                'revenue_per_share': data.get('RevenuePerShareTTM', 'N/A'),
                'quarterly_earnings_growth': data.get('QuarterlyEarningsGrowthYOY', 'N/A'),
                'quarterly_revenue_growth': data.get('QuarterlyRevenueGrowthYOY', 'N/A'),
                'analyst_target_price': data.get('AnalystTargetPrice', 'N/A'),
                'trailing_pe': data.get('TrailingPE', 'N/A'),
                'forward_pe': data.get('ForwardPE', 'N/A'),
                'price_to_sales_ratio': data.get('PriceToSalesRatioTTM', 'N/A'),
                'price_to_book_ratio': data.get('PriceToBookRatio', 'N/A'),
                'ev_to_revenue': data.get('EVToRevenue', 'N/A'),
                'ev_to_ebitda': data.get('EVToEBITDA', 'N/A'),
                'beta': data.get('Beta', 'N/A'),
                '52_week_high': data.get('52WeekHigh', 'N/A'),
                '52_week_low': data.get('52WeekLow', 'N/A'),
                '50_day_ma': data.get('50DayMovingAverage', 'N/A'),
                '200_day_ma': data.get('200DayMovingAverage', 'N/A'),
                'shares_outstanding': data.get('SharesOutstanding', 'N/A'),
                'shares_float': data.get('SharesFloat', 'N/A'),
                'shares_short': data.get('SharesShort', 'N/A'),
                'shares_short_prior_month': data.get('SharesShortPriorMonth', 'N/A'),
                'short_ratio': data.get('ShortRatio', 'N/A'),
                'short_percent_outstanding': data.get('ShortPercentOutstanding', 'N/A'),
                'short_percent_float': data.get('ShortPercentFloat', 'N/A'),
                'percent_insiders': data.get('PercentInsiders', 'N/A'),
                'percent_institutions': data.get('PercentInstitutions', 'N/A'),
                'forward_annual_dividend_rate': data.get('ForwardAnnualDividendRate', 'N/A'),
                'forward_annual_dividend_yield': data.get('ForwardAnnualDividendYield', 'N/A'),
                'payout_ratio': data.get('PayoutRatio', 'N/A'),
                'dividend_date': data.get('DividendDate', 'N/A'),
                'ex_dividend_date': data.get('ExDividendDate', 'N/A')
            }
        except Exception as e:
            print(f"Error parsing Alpha Vantage overview data: {e}")
            return self._get_mock_overview(symbol)
    
    def get_technical_indicators(self, symbol: str, indicator: str = 'SMA', 
                               time_period: int = 20, interval: str = 'daily') -> Dict:
        """Get technical indicators like SMA, EMA, RSI, etc."""
        params = {
            'function': indicator,
            'symbol': symbol,
            'interval': interval,
            'time_period': time_period,
            'series_type': 'close'
        }
        
        data = self._make_request(params)
        if not data:
            return {'error': 'Failed to fetch technical indicator data'}
        
        try:
            # Different indicators have different response structures
            if indicator == 'SMA':
                technical_data = data[f'Technical Analysis: {indicator}']
            elif indicator == 'EMA':
                technical_data = data[f'Technical Analysis: {indicator}']
            elif indicator == 'RSI':
                technical_data = data[f'Technical Analysis: {indicator}']
            elif indicator == 'MACD':
                technical_data = data[f'Technical Analysis: {indicator}']
            else:
                technical_data = list(data.values())[1]  # Skip metadata
            
            # Get the latest values
            latest_date = max(technical_data.keys())
            return {
                'indicator': indicator,
                'symbol': symbol,
                'latest_date': latest_date,
                'latest_value': technical_data[latest_date],
                'historical_data': dict(list(technical_data.items())[:10])  # Last 10 data points
            }
        except Exception as e:
            print(f"Error parsing technical indicator data: {e}")
            return {'error': f'Failed to parse {indicator} data'}
    
    def _get_mock_quote(self, symbol: str) -> Dict:
        """Return mock quote data when API is not available."""
        return {
            'symbol': symbol,
            'price': 150.00,
            'change': 2.50,
            'change_percent': '1.69%',
            'volume': 1000000,
            'open': 148.00,
            'high': 152.00,
            'low': 147.50,
            'previous_close': 147.50,
            'latest_trading_day': '2025-08-25'
        }
    
    def _get_mock_overview(self, symbol: str) -> Dict:
        """Return mock overview data when API is not available."""
        return {
            'symbol': symbol,
            'name': f'{symbol} Corporation',
            'sector': 'Technology',
            'industry': 'Software',
            'market_cap': '1000000000',
            'pe_ratio': '25.5',
            'eps': '5.89',
            'dividend_yield': '2.5%'
        }

# Global instance
alpha_vantage = AlphaVantageAPI()
