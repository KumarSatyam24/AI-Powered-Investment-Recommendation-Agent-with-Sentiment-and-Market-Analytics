import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.api_clients.fred_api import fred_api

def analyze_market(index_data=None, vix=None, inflation=None):
    """Enhanced market analysis using FRED economic data."""
    try:
        # Get real economic indicators from FRED
        market_data = fred_api.get_market_indicators_summary()
        economic_indicators = market_data['summary']
        
        # Extract key metrics
        current_vix = economic_indicators.get('vix', {}).get('value', vix or 20)
        current_inflation = economic_indicators.get('inflation', {}).get('value', inflation or 3)
        unemployment = economic_indicators.get('unemployment', {}).get('value', 4)
        fed_rate = economic_indicators.get('fed_funds_rate', {}).get('value', 5)
        consumer_sentiment = economic_indicators.get('consumer_sentiment', {}).get('value', 80)
        
        # Convert to numeric values if they're strings
        try:
            current_vix = float(current_vix) if current_vix != 'N/A' else 20
            current_inflation = float(current_inflation) if current_inflation != 'N/A' else 3
            unemployment = float(unemployment) if unemployment != 'N/A' else 4
            fed_rate = float(fed_rate) if fed_rate != 'N/A' else 5
            consumer_sentiment = float(consumer_sentiment) if consumer_sentiment != 'N/A' else 80
        except (ValueError, TypeError):
            # Use fallback values if conversion fails
            current_vix = vix or 20
            current_inflation = inflation or 3
            unemployment = 4
            fed_rate = 5
            consumer_sentiment = 80
        
        # Enhanced market analysis logic
        risk_factors = 0
        risk_details = []
        
        # VIX analysis (fear index)
        if current_vix > 30:
            risk_factors += 3
            risk_details.append(f"High market volatility (VIX: {current_vix})")
        elif current_vix > 25:
            risk_factors += 2
            risk_details.append(f"Elevated market volatility (VIX: {current_vix})")
        elif current_vix > 20:
            risk_factors += 1
            risk_details.append(f"Moderate market volatility (VIX: {current_vix})")
        
        # Inflation analysis
        if current_inflation > 5:
            risk_factors += 2
            risk_details.append(f"High inflation concern ({current_inflation}%)")
        elif current_inflation > 3:
            risk_factors += 1
            risk_details.append(f"Moderate inflation ({current_inflation}%)")
        
        # Unemployment analysis
        if unemployment > 6:
            risk_factors += 2
            risk_details.append(f"High unemployment ({unemployment}%)")
        elif unemployment > 4:
            risk_factors += 1
            risk_details.append(f"Elevated unemployment ({unemployment}%)")
        
        # Federal funds rate analysis
        if fed_rate > 6:
            risk_factors += 2
            risk_details.append(f"High interest rates ({fed_rate}%)")
        elif fed_rate > 4:
            risk_factors += 1
            risk_details.append(f"Elevated interest rates ({fed_rate}%)")
        
        # Consumer sentiment analysis
        if consumer_sentiment < 70:
            risk_factors += 2
            risk_details.append(f"Poor consumer sentiment ({consumer_sentiment})")
        elif consumer_sentiment < 85:
            risk_factors += 1
            risk_details.append(f"Weak consumer sentiment ({consumer_sentiment})")
        
        # Determine overall market condition
        if risk_factors >= 6:
            market_condition = "High Risk - Defensive Strategy"
        elif risk_factors >= 4:
            market_condition = "Moderate Risk - Cautious Approach"
        elif risk_factors >= 2:
            market_condition = "Low Risk - Selective Opportunities"
        else:
            market_condition = "Risk-On - Growth Opportunities"
        
        return {
            'condition': market_condition,
            'risk_score': risk_factors,
            'risk_details': risk_details,
            'economic_indicators': {
                'vix': current_vix,
                'inflation': current_inflation,
                'unemployment': unemployment,
                'fed_funds_rate': fed_rate,
                'consumer_sentiment': consumer_sentiment
            },
            'recommendation': get_market_recommendation(risk_factors)
        }
    
    except Exception as e:
        print(f"Error in enhanced market analysis: {e}")
        # Fallback to simple analysis
        fallback_vix = vix or 25
        fallback_inflation = inflation or 5
        
        if fallback_vix > 25 or fallback_inflation > 5:
            return {
                'condition': "Risk-Off",
                'risk_score': 3,
                'risk_details': ["Using fallback analysis due to API issues"],
                'economic_indicators': {'vix': fallback_vix, 'inflation': fallback_inflation},
                'recommendation': "Defensive positioning recommended"
            }
        else:
            return {
                'condition': "Risk-On",
                'risk_score': 1,
                'risk_details': ["Using fallback analysis due to API issues"],
                'economic_indicators': {'vix': fallback_vix, 'inflation': fallback_inflation},
                'recommendation': "Growth opportunities available"
            }

def get_market_recommendation(risk_score):
    """Get investment recommendations based on risk score."""
    if risk_score >= 6:
        return "Focus on defensive assets: bonds, utilities, consumer staples. Consider hedging strategies."
    elif risk_score >= 4:
        return "Balanced approach: mix of defensive and growth stocks. Monitor economic indicators closely."
    elif risk_score >= 2:
        return "Selective growth opportunities: focus on quality stocks with strong fundamentals."
    else:
        return "Growth-oriented strategy: consider technology, growth stocks, and cyclical sectors."

def get_sector_analysis(sector):
    """Get sector-specific market analysis using FRED data."""
    try:
        sector_data = fred_api.get_sector_specific_indicators(sector)
        
        # Analyze sector-specific indicators
        analysis = {
            'sector': sector,
            'indicators': sector_data,
            'outlook': 'neutral'  # Default
        }
        
        # Sector-specific logic can be added here based on the indicators
        return analysis
    
    except Exception as e:
        print(f"Error in sector analysis: {e}")
        return {
            'sector': sector,
            'indicators': {},
            'outlook': 'neutral',
            'error': 'Unable to fetch sector-specific data'
        }