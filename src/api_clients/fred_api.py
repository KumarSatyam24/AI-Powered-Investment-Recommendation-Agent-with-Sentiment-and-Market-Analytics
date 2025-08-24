import requests
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import FRED_API_KEY

class FREDAPI:
    """Federal Reserve Economic Data (FRED) API client for macroeconomic indicators."""
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    def __init__(self):
        self.api_key = FRED_API_KEY
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request to FRED."""
        if not self.api_key or self.api_key == "YOUR_FRED_API_KEY":
            print("FRED API key not configured. Using mock data.")
            return None
        
        params.update({
            'api_key': self.api_key,
            'file_type': 'json'
        })
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making FRED API request: {e}")
            return None
    
    def get_economic_indicator(self, series_id: str, limit: int = 10) -> Dict:
        """Get economic indicator data by series ID."""
        params = {
            'series_id': series_id,
            'limit': limit,
            'sort_order': 'desc'
        }
        
        data = self._make_request('series/observations', params)
        if not data:
            return self._get_mock_indicator(series_id)
        
        try:
            observations = data['observations']
            return {
                'series_id': series_id,
                'observations': observations,
                'latest_value': observations[0]['value'] if observations else 'N/A',
                'latest_date': observations[0]['date'] if observations else 'N/A',
                'count': len(observations)
            }
        except Exception as e:
            print(f"Error parsing FRED data for {series_id}: {e}")
            return self._get_mock_indicator(series_id)
    
    def get_inflation_rate(self) -> Dict:
        """Get Consumer Price Index (CPI) inflation rate."""
        return self.get_economic_indicator('CPIAUCSL')
    
    def get_unemployment_rate(self) -> Dict:
        """Get unemployment rate."""
        return self.get_economic_indicator('UNRATE')
    
    def get_gdp_growth(self) -> Dict:
        """Get GDP growth rate."""
        return self.get_economic_indicator('GDP')
    
    def get_federal_funds_rate(self) -> Dict:
        """Get Federal Funds Rate."""
        return self.get_economic_indicator('FEDFUNDS')
    
    def get_10_year_treasury(self) -> Dict:
        """Get 10-Year Treasury Constant Maturity Rate."""
        return self.get_economic_indicator('GS10')
    
    def get_vix_index(self) -> Dict:
        """Get CBOE Volatility Index (VIX)."""
        return self.get_economic_indicator('VIXCLS')
    
    def get_consumer_sentiment(self) -> Dict:
        """Get University of Michigan Consumer Sentiment."""
        return self.get_economic_indicator('UMCSENT')
    
    def get_industrial_production(self) -> Dict:
        """Get Industrial Production Index."""
        return self.get_economic_indicator('INDPRO')
    
    def get_housing_starts(self) -> Dict:
        """Get Housing Starts."""
        return self.get_economic_indicator('HOUST')
    
    def get_retail_sales(self) -> Dict:
        """Get Advance Retail Sales."""
        return self.get_economic_indicator('RSAFS')
    
    def get_market_indicators_summary(self) -> Dict:
        """Get a summary of key market indicators."""
        indicators = {
            'inflation': self.get_inflation_rate(),
            'unemployment': self.get_unemployment_rate(),
            'fed_funds_rate': self.get_federal_funds_rate(),
            'treasury_10y': self.get_10_year_treasury(),
            'vix': self.get_vix_index(),
            'consumer_sentiment': self.get_consumer_sentiment()
        }
        
        # Extract latest values for easy access
        summary = {}
        for key, data in indicators.items():
            if data and data.get('latest_value') not in ['N/A', '.']:
                try:
                    summary[key] = {
                        'value': float(data['latest_value']),
                        'date': data['latest_date']
                    }
                except (ValueError, TypeError):
                    summary[key] = {
                        'value': data['latest_value'],
                        'date': data['latest_date']
                    }
            else:
                summary[key] = {'value': 'N/A', 'date': 'N/A'}
        
        return {
            'summary': summary,
            'detailed_data': indicators,
            'market_condition': self._assess_market_condition(summary)
        }
    
    def _assess_market_condition(self, summary: Dict) -> str:
        """Assess overall market condition based on economic indicators."""
        try:
            vix = summary.get('vix', {}).get('value', 0)
            unemployment = summary.get('unemployment', {}).get('value', 0)
            fed_rate = summary.get('fed_funds_rate', {}).get('value', 0)
            
            if isinstance(vix, (int, float)) and isinstance(unemployment, (int, float)):
                if vix > 30 or unemployment > 7:
                    return "High Risk - Market Stress"
                elif vix > 20 or unemployment > 5:
                    return "Moderate Risk - Caution Advised"
                else:
                    return "Low Risk - Market Stable"
            else:
                return "Unknown - Insufficient Data"
        except Exception:
            return "Unknown - Assessment Error"
    
    def get_sector_specific_indicators(self, sector: str) -> Dict:
        """Get sector-specific economic indicators."""
        sector_indicators = {
            'technology': {
                'productivity': 'OPHNFB',  # Nonfarm Business Sector: Labor Productivity
                'patent_apps': 'USPATENTAPP'  # US Patent Applications
            },
            'real_estate': {
                'housing_starts': 'HOUST',
                'home_sales': 'HSN1F',
                'mortgage_rates': 'MORTGAGE30US'
            },
            'energy': {
                'oil_price': 'DCOILWTICO',
                'natural_gas': 'DHHNGSP'
            },
            'finance': {
                'credit_spread': 'BAA10Y',  # Corporate bond spread
                'bank_lending': 'TOTLL'
            }
        }
        
        indicators = sector_indicators.get(sector.lower(), {})
        result = {}
        
        for name, series_id in indicators.items():
            result[name] = self.get_economic_indicator(series_id, limit=5)
        
        return result
    
    def _get_mock_indicator(self, series_id: str) -> Dict:
        """Return mock indicator data when API is not available."""
        mock_values = {
            'CPIAUCSL': '310.5',  # CPI
            'UNRATE': '3.8',      # Unemployment
            'GDP': '27000.0',     # GDP
            'FEDFUNDS': '5.25',   # Fed Funds Rate
            'GS10': '4.2',        # 10Y Treasury
            'VIXCLS': '18.5',     # VIX
            'UMCSENT': '85.0'     # Consumer Sentiment
        }
        
        return {
            'series_id': series_id,
            'observations': [{
                'date': '2025-08-25',
                'value': mock_values.get(series_id, '100.0')
            }],
            'latest_value': mock_values.get(series_id, '100.0'),
            'latest_date': '2025-08-25',
            'count': 1
        }

# Global instance
fred_api = FREDAPI()
