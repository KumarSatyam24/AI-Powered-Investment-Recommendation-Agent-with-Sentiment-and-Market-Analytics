import requests
import pandas as pd
from typing import Dict, Optional, List
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ALPHA_VANTAGE_KEY

# Try to import yfinance for backup data
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("📝 Note: yfinance not available - install with 'pip install yfinance' for better backup data")

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
            elif "Information" in data:
                # Handle rate limit information
                if "rate limit" in data["Information"].lower():
                    print(f"⚠️ Alpha Vantage Rate Limit: {data['Information']}")
                    print("🔄 Using mock data due to API rate limits")
                    return None
                else:
                    print(f"Alpha Vantage Info: {data['Information']}")
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
            return self._get_yfinance_quote(symbol)
        
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
                'latest_trading_day': quote['07. latest trading day'],
                'data_source': 'alpha_vantage'
            }
        except (KeyError, ValueError) as e:
            print(f"Error parsing Alpha Vantage quote data: {e}")
            print("🔄 Falling back to Yahoo Finance data...")
            return self._get_yfinance_quote(symbol)
    
    def get_company_overview(self, symbol: str) -> Dict:
        """Get company fundamental data."""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        
        data = self._make_request(params)
        if not data:
            return self._get_yfinance_overview(symbol)
        
        try:
            overview_data = {
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
                'ex_dividend_date': data.get('ExDividendDate', 'N/A'),
                'data_source': 'alpha_vantage'
            }
            return overview_data
        except Exception as e:
            print(f"Error parsing Alpha Vantage overview data: {e}")
            print("🔄 Falling back to Yahoo Finance data...")
            return self._get_yfinance_overview(symbol)
    
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
            return self._get_mock_technical_indicator(symbol, indicator, time_period)
        
        try:
            # Different indicators have different response structures
            technical_data = None
            
            # Try common response key patterns
            possible_keys = [
                f'Technical Analysis: {indicator}',
                f'{indicator}({time_period})',
                indicator,
                f'{indicator}_{time_period}'
            ]
            
            for key in possible_keys:
                if key in data:
                    technical_data = data[key]
                    break
            
            # If still no data found, try to find the second key (first is usually metadata)
            if not technical_data and len(data.keys()) >= 2:
                keys = list(data.keys())
                technical_data = data[keys[1]]
            
            if not technical_data:
                print(f"Could not find technical data in response. Available keys: {list(data.keys())}")
                return self._get_mock_technical_indicator(symbol, indicator, time_period)
            
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
            # Try Yahoo Finance for basic indicators
            if indicator in ['RSI', 'SMA'] and YFINANCE_AVAILABLE:
                return self._get_yfinance_technical_indicator(symbol, indicator, time_period)
            return self._get_mock_technical_indicator(symbol, indicator, time_period)
    
    def _get_yfinance_technical_indicator(self, symbol: str, indicator: str, time_period: int = 20) -> Dict:
        """Get basic technical indicators from Yahoo Finance historical data"""
        if not YFINANCE_AVAILABLE:
            return self._get_mock_technical_indicator(symbol, indicator, time_period)
        
        try:
            ticker = yf.Ticker(symbol)
            # Get historical data for calculations
            hist = ticker.history(period="3mo")  # 3 months should be enough for most indicators
            
            if hist.empty:
                print(f"⚠️ Yahoo Finance: No historical data for {symbol}")
                return self._get_mock_technical_indicator(symbol, indicator, time_period)
            
            if indicator == 'SMA':
                # Simple Moving Average
                sma_values = hist['Close'].rolling(window=time_period).mean()
                latest_value = sma_values.iloc[-1] if not sma_values.empty else hist['Close'].iloc[-1]
                
                # Create historical data dict
                historical_data = {}
                for i, (date, value) in enumerate(sma_values.tail(10).items()):
                    if not pd.isna(value):
                        historical_data[date.strftime('%Y-%m-%d')] = f'{value:.4f}'
                
                return {
                    'indicator': indicator,
                    'symbol': symbol,
                    'latest_date': hist.index[-1].strftime('%Y-%m-%d'),
                    'latest_value': f'{latest_value:.4f}',
                    'historical_data': historical_data,
                    'data_source': 'yahoo_finance'
                }
            
            elif indicator == 'RSI':
                # Relative Strength Index (simplified calculation)
                close_prices = hist['Close']
                delta = close_prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=time_period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=time_period).mean()
                
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                latest_value = rsi.iloc[-1] if not rsi.empty else 50.0
                
                # Create historical data dict
                historical_data = {}
                for i, (date, value) in enumerate(rsi.tail(10).items()):
                    if not pd.isna(value):
                        historical_data[date.strftime('%Y-%m-%d')] = f'{value:.4f}'
                
                return {
                    'indicator': indicator,
                    'symbol': symbol,
                    'latest_date': hist.index[-1].strftime('%Y-%m-%d'),
                    'latest_value': f'{latest_value:.4f}',
                    'historical_data': historical_data,
                    'data_source': 'yahoo_finance'
                }
            
            else:
                # For other indicators, return mock data
                return self._get_mock_technical_indicator(symbol, indicator, time_period)
                
        except Exception as e:
            print(f"⚠️ Yahoo Finance technical indicator error for {symbol}: {e}")
            return self._get_mock_technical_indicator(symbol, indicator, time_period)
    
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
    
    def _get_mock_technical_indicator(self, symbol: str, indicator: str, time_period: int) -> Dict:
        """Return mock technical indicator data when API is not available."""
        # Generate realistic mock values based on indicator type
        if indicator == 'SMA':
            value = {'SMA': '150.25'}
        elif indicator == 'EMA':
            value = {'EMA': '149.80'}
        elif indicator == 'RSI':
            value = {'RSI': '58.34'}
        elif indicator == 'MACD':
            value = {'MACD': '1.23', 'MACD_Hist': '0.45', 'MACD_Signal': '0.78'}
        else:
            value = {indicator: '50.00'}
        
        return {
            'indicator': indicator,
            'symbol': symbol,
            'latest_date': '2025-09-16',
            'latest_value': value,
            'historical_data': {f'2025-09-{i:02d}': value for i in range(16, 6, -1)},
            'note': 'Mock data - API rate limit exceeded'
        }
    
    def _get_yfinance_quote(self, symbol: str) -> Dict:
        """Get stock quote from Yahoo Finance as backup"""
        if not YFINANCE_AVAILABLE:
            print("📝 Yahoo Finance not available - using mock data")
            return self._get_mock_quote(symbol)
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'currentPrice' not in info:
                print(f"⚠️ Yahoo Finance: No data for {symbol} - using mock data")
                return self._get_mock_quote(symbol)
            
            current_price = info.get('currentPrice', 0)
            previous_close = info.get('previousClose', current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close > 0 else 0
            
            return {
                'symbol': symbol,
                'price': float(current_price),
                'change': round(change, 2),
                'change_percent': f'{change_percent:.2f}%',
                'volume': int(info.get('volume', 0)),
                'open': float(info.get('open', current_price)),
                'high': float(info.get('dayHigh', current_price)),
                'low': float(info.get('dayLow', current_price)),
                'previous_close': float(previous_close),
                'latest_trading_day': info.get('lastTradeDate', '2025-09-16'),
                'data_source': 'yahoo_finance'
            }
            
        except Exception as e:
            print(f"⚠️ Yahoo Finance error for {symbol}: {e}")
            return self._get_mock_quote(symbol)
    
    def _get_yfinance_overview(self, symbol: str) -> Dict:
        """Get company overview from Yahoo Finance as backup"""
        if not YFINANCE_AVAILABLE:
            print("📝 Yahoo Finance not available - using mock data")
            return self._get_mock_overview(symbol)
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                print(f"⚠️ Yahoo Finance: No overview data for {symbol} - using mock data")
                return self._get_mock_overview(symbol)
            
            # Convert market cap to string format
            market_cap = info.get('marketCap', 0)
            market_cap_str = str(market_cap) if market_cap else 'N/A'
            
            return {
                'symbol': symbol,
                'name': info.get('longName', f'{symbol} Corporation'),
                'description': info.get('longBusinessSummary', 'N/A')[:500] + '...' if info.get('longBusinessSummary') else 'N/A',
                'sector': info.get('sector', 'Technology'),
                'industry': info.get('industry', 'Software'),
                'market_cap': market_cap_str,
                'pe_ratio': str(info.get('trailingPE', 'N/A')),
                'peg_ratio': str(info.get('pegRatio', 'N/A')),
                'book_value': str(info.get('bookValue', 'N/A')),
                'dividend_per_share': str(info.get('dividendRate', 'N/A')),
                'dividend_yield': str(info.get('dividendYield', 'N/A')),
                'eps': str(info.get('trailingEps', 'N/A')),
                'revenue_ttm': str(info.get('totalRevenue', 'N/A')),
                'profit_margin': str(info.get('profitMargins', 'N/A')),
                'operating_margin': str(info.get('operatingMargins', 'N/A')),
                'return_on_assets': str(info.get('returnOnAssets', 'N/A')),
                'return_on_equity': str(info.get('returnOnEquity', 'N/A')),
                'revenue_per_share': str(info.get('revenuePerShare', 'N/A')),
                'quarterly_earnings_growth': str(info.get('earningsQuarterlyGrowth', 'N/A')),
                'quarterly_revenue_growth': str(info.get('revenueQuarterlyGrowth', 'N/A')),
                'analyst_target_price': str(info.get('targetMeanPrice', 'N/A')),
                'trailing_pe': str(info.get('trailingPE', 'N/A')),
                'forward_pe': str(info.get('forwardPE', 'N/A')),
                'price_to_sales_ratio': str(info.get('priceToSalesTrailing12Months', 'N/A')),
                'price_to_book_ratio': str(info.get('priceToBook', 'N/A')),
                'ev_to_revenue': str(info.get('enterpriseToRevenue', 'N/A')),
                'ev_to_ebitda': str(info.get('enterpriseToEbitda', 'N/A')),
                'beta': str(info.get('beta', 'N/A')),
                '52_week_high': str(info.get('fiftyTwoWeekHigh', 'N/A')),
                '52_week_low': str(info.get('fiftyTwoWeekLow', 'N/A')),
                '50_day_ma': str(info.get('fiftyDayAverage', 'N/A')),
                '200_day_ma': str(info.get('twoHundredDayAverage', 'N/A')),
                'shares_outstanding': str(info.get('sharesOutstanding', 'N/A')),
                'shares_float': str(info.get('floatShares', 'N/A')),
                'shares_short': str(info.get('sharesShort', 'N/A')),
                'shares_short_prior_month': str(info.get('sharesShortPriorMonth', 'N/A')),
                'short_ratio': str(info.get('shortRatio', 'N/A')),
                'short_percent_outstanding': str(info.get('shortPercentOfFloat', 'N/A')),
                'short_percent_float': str(info.get('shortPercentOfFloat', 'N/A')),
                'percent_insiders': str(info.get('heldPercentInsiders', 'N/A')),
                'percent_institutions': str(info.get('heldPercentInstitutions', 'N/A')),
                'forward_annual_dividend_rate': str(info.get('dividendRate', 'N/A')),
                'forward_annual_dividend_yield': str(info.get('dividendYield', 'N/A')),
                'payout_ratio': str(info.get('payoutRatio', 'N/A')),
                'dividend_date': str(info.get('dividendDate', 'N/A')),
                'ex_dividend_date': str(info.get('exDividendDate', 'N/A')),
                'data_source': 'yahoo_finance'
            }
            
        except Exception as e:
            print(f"⚠️ Yahoo Finance overview error for {symbol}: {e}")
            return self._get_mock_overview(symbol)

# Global instance
alpha_vantage = AlphaVantageAPI()
