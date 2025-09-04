"""
Enhanced Investment Recommendation Engine
Combines sector analysis with individual stock analysis for comprehensive investment recommendations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from analysis_engine.sector_analysis import SectorSentimentAnalyzer, SECTOR_MAPPINGS
from sentiment_analysis.news_sentiments import analyze_comprehensive_news_sentiment_advanced

class SimpleRiskProfiler:
    """Simple risk profiler for the hybrid system"""
    @staticmethod
    def assess_risk_level(risk_tolerance: str) -> str:
        return risk_tolerance.title()

class HybridRecommendationEngine:
    """
    Advanced recommendation engine combining:
    1. Top-down sector analysis for allocation
    2. Bottom-up stock analysis for selection within favored sectors
    3. Risk management and portfolio optimization
    """
    
    def __init__(self):
        self.sector_analyzer = SectorSentimentAnalyzer()
        self.risk_profiler = SimpleRiskProfiler()
        self.sector_mappings = SECTOR_MAPPINGS
        
    def generate_investment_recommendations(self, 
                                          portfolio_size: float = 100000,
                                          risk_tolerance: str = 'moderate',
                                          max_sectors: int = 5,
                                          stocks_per_sector: int = 3) -> Dict:
        """
        Generate comprehensive investment recommendations using hybrid approach
        
        Args:
            portfolio_size: Total portfolio value in USD
            risk_tolerance: 'conservative', 'moderate', 'aggressive'
            max_sectors: Maximum number of sectors to invest in
            stocks_per_sector: Maximum stocks per sector
            
        Returns:
            Dict: Comprehensive investment recommendations
        """
        print("🎯 Generating Hybrid Investment Recommendations")
        print("=" * 60)
        print(f"💰 Portfolio Size: ${portfolio_size:,.0f}")
        print(f"⚡ Risk Tolerance: {risk_tolerance.title()}")
        print(f"🏭 Max Sectors: {max_sectors}")
        print(f"📈 Stocks per Sector: {stocks_per_sector}")
        print()
        
        try:
            # Step 1: Sector Analysis (Top-down)
            print("🔍 Step 1: Analyzing Sector Trends...")
            sector_results = self.sector_analyzer.analyze_sector_sentiment()
            
            if 'error' in sector_results:
                return {'error': f"Sector analysis failed: {sector_results['error']}"}
            
            # Step 2: Select Top Sectors
            top_sectors = self._select_top_sectors(
                sector_results['sector_rankings'], 
                max_sectors, 
                risk_tolerance
            )
            
            print(f"✅ Selected {len(top_sectors)} top sectors")
            
            # Step 3: Stock Analysis within Selected Sectors (Bottom-up)
            print("\n🔍 Step 2: Analyzing Individual Stocks...")
            stock_recommendations = {}
            
            for sector_info in top_sectors:
                sector = sector_info['sector']
                sector_tickers = self.sector_mappings.get(sector, {}).get('tickers', [])
                
                if sector_tickers:
                    print(f"   📊 Analyzing {sector.replace('_', ' ').title()} stocks...")
                    
                    sector_stocks = self._analyze_sector_stocks(
                        sector_tickers[:stocks_per_sector * 2],  # Analyze more, select fewer
                        stocks_per_sector
                    )
                    
                    if sector_stocks:
                        stock_recommendations[sector] = {
                            'sector_info': sector_info,
                            'recommended_stocks': sector_stocks
                        }
            
            # Step 4: Portfolio Allocation
            print("\n🔍 Step 3: Optimizing Portfolio Allocation...")
            portfolio_allocation = self._calculate_portfolio_allocation(
                stock_recommendations,
                portfolio_size,
                risk_tolerance
            )
            
            # Step 5: Risk Assessment
            risk_metrics = self._assess_portfolio_risk(portfolio_allocation, risk_tolerance)
            
            # Step 6: Generate Final Recommendations
            final_recommendations = {
                'portfolio_summary': {
                    'total_value': portfolio_size,
                    'risk_tolerance': risk_tolerance,
                    'sectors_selected': len(stock_recommendations),
                    'total_positions': sum(len(data['recommended_stocks']) for data in stock_recommendations.values()),
                    'analysis_date': datetime.now().isoformat()
                },
                'sector_analysis': sector_results['sector_rankings'],
                'selected_sectors': list(stock_recommendations.keys()),
                'portfolio_allocation': portfolio_allocation,
                'risk_assessment': risk_metrics,
                'execution_plan': self._create_execution_plan(portfolio_allocation),
                'monitoring_alerts': self._generate_monitoring_alerts(stock_recommendations)
            }
            
            # Display results
            self._display_recommendations(final_recommendations)
            
            return final_recommendations
            
        except Exception as e:
            print(f"❌ Error generating recommendations: {e}")
            return {'error': str(e)}
    
    def _select_top_sectors(self, sector_rankings: Dict, max_sectors: int, risk_tolerance: str) -> List[Dict]:
        """
        Select top sectors based on sentiment and risk tolerance
        """
        rankings = sector_rankings.get('rankings', [])
        
        if not rankings:
            return []
        
        # Filter by risk tolerance
        risk_filters = {
            'conservative': lambda x: x['confidence'] >= 0.5 and x['sentiment_score'] >= 0,
            'moderate': lambda x: x['confidence'] >= 0.3 and x['sentiment_score'] >= -0.1,
            'aggressive': lambda x: x['confidence'] >= 0.2  # Accept higher risk
        }
        
        filter_func = risk_filters.get(risk_tolerance, risk_filters['moderate'])
        filtered_sectors = [sector for sector in rankings if filter_func(sector)]
        
        # Select top sectors
        selected = filtered_sectors[:max_sectors]
        
        print(f"   🎯 Top sectors selected:")
        for i, sector in enumerate(selected, 1):
            print(f"      {i}. {sector['sector'].replace('_', ' ').title()} "
                  f"(Score: {sector['sentiment_score']:+.3f}, "
                  f"Confidence: {sector['confidence']:.3f})")
        
        return selected
    
    def _analyze_sector_stocks(self, tickers: List[str], max_stocks: int) -> List[Dict]:
        """
        Analyze individual stocks within a sector
        """
        stock_analyses = []
        
        for ticker in tickers[:max_stocks * 2]:  # Analyze extra to have choices
            try:
                # Use existing sentiment analysis
                analysis = analyze_comprehensive_news_sentiment_advanced(ticker)
                
                if 'error' not in analysis:
                    sentiment_data = analysis.get('sentiment_analysis', {})
                    
                    stock_score = {
                        'ticker': ticker,
                        'sentiment_score': sentiment_data.get('combined_sentiment_score', 0),
                        'sentiment_label': sentiment_data.get('sentiment_label', 'Neutral'),
                        'confidence': sentiment_data.get('weights', {}).get('stock_specific_weight', 0.5),
                        'articles_analyzed': sentiment_data.get('component_analysis', {}).get('stock_specific', {}).get('article_count', 0),
                        'analysis_timestamp': analysis.get('analysis_metadata', {}).get('timestamp', '')
                    }
                    
                    stock_analyses.append(stock_score)
                    
            except Exception as e:
                print(f"      ⚠️ Could not analyze {ticker}: {e}")
                continue
        
        # Sort by sentiment score and confidence
        stock_analyses.sort(
            key=lambda x: x['sentiment_score'] * x['confidence'],
            reverse=True
        )
        
        return stock_analyses[:max_stocks]
    
    def _calculate_portfolio_allocation(self, stock_recommendations: Dict, 
                                      portfolio_size: float, risk_tolerance: str) -> Dict:
        """
        Calculate optimal portfolio allocation
        """
        if not stock_recommendations:
            return {}
        
        # Base allocation weights by risk tolerance
        risk_weights = {
            'conservative': {'equal_weight': 0.8, 'performance_weight': 0.2},
            'moderate': {'equal_weight': 0.6, 'performance_weight': 0.4},
            'aggressive': {'equal_weight': 0.4, 'performance_weight': 0.6}
        }
        
        weights = risk_weights.get(risk_tolerance, risk_weights['moderate'])
        
        # Calculate sector allocations
        total_sectors = len(stock_recommendations)
        sector_allocations = {}
        
        for sector, data in stock_recommendations.items():
            sector_info = data['sector_info']
            stocks = data['recommended_stocks']
            
            # Base sector weight (equal + performance adjustment)
            base_weight = 1.0 / total_sectors
            performance_adjustment = sector_info['sentiment_score'] * sector_info['confidence']
            
            sector_weight = (
                base_weight * weights['equal_weight'] +
                performance_adjustment * weights['performance_weight'] / total_sectors
            )
            
            sector_allocation = portfolio_size * sector_weight
            
            # Allocate within sector
            stock_allocations = []
            total_stocks = len(stocks)
            
            for stock in stocks:
                # Stock weight within sector
                stock_base_weight = 1.0 / total_stocks
                stock_performance = stock['sentiment_score'] * stock['confidence']
                
                stock_weight = (
                    stock_base_weight * weights['equal_weight'] +
                    stock_performance * weights['performance_weight'] / total_stocks
                )
                
                stock_allocation = sector_allocation * stock_weight
                
                stock_allocations.append({
                    'ticker': stock['ticker'],
                    'allocation_amount': stock_allocation,
                    'allocation_percentage': (stock_allocation / portfolio_size) * 100,
                    'sentiment_score': stock['sentiment_score'],
                    'confidence': stock['confidence'],
                    'recommendation': self._get_stock_recommendation(stock['sentiment_score'], stock['confidence'])
                })
            
            sector_allocations[sector] = {
                'sector_allocation': sector_allocation,
                'sector_percentage': (sector_allocation / portfolio_size) * 100,
                'sector_sentiment': sector_info['sentiment_score'],
                'stocks': stock_allocations
            }
        
        return sector_allocations
    
    def _get_stock_recommendation(self, sentiment_score: float, confidence: float) -> str:
        """
        Generate stock recommendation based on sentiment and confidence
        """
        if confidence < 0.3:
            return 'HOLD - Monitor'
        
        if sentiment_score > 0.2:
            return 'STRONG BUY'
        elif sentiment_score > 0.05:
            return 'BUY'
        elif sentiment_score < -0.2:
            return 'STRONG SELL'
        elif sentiment_score < -0.05:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _assess_portfolio_risk(self, portfolio_allocation: Dict, risk_tolerance: str) -> Dict:
        """
        Assess overall portfolio risk
        """
        if not portfolio_allocation:
            return {}
        
        # Calculate risk metrics
        total_positions = sum(len(sector_data['stocks']) for sector_data in portfolio_allocation.values())
        sector_concentration = max(sector_data['sector_percentage'] for sector_data in portfolio_allocation.values())
        
        # Calculate sentiment diversity
        sentiment_scores = []
        for sector_data in portfolio_allocation.values():
            for stock in sector_data['stocks']:
                sentiment_scores.append(stock['sentiment_score'])
        
        sentiment_std = np.std(sentiment_scores) if sentiment_scores else 0
        avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
        
        # Risk assessment
        risk_level = 'Low'
        if sector_concentration > 40 or total_positions < 5:
            risk_level = 'High'
        elif sector_concentration > 25 or sentiment_std > 0.3:
            risk_level = 'Medium'
        
        return {
            'risk_level': risk_level,
            'diversification_score': min(100, (total_positions / 15) * 100),
            'sector_concentration': round(sector_concentration, 1),
            'sentiment_consistency': round(1 - sentiment_std, 3),
            'average_sentiment': round(avg_sentiment, 3),
            'total_positions': total_positions,
            'recommendations': self._get_risk_recommendations(risk_level, sector_concentration, total_positions)
        }
    
    def _get_risk_recommendations(self, risk_level: str, concentration: float, positions: int) -> List[str]:
        """
        Generate risk management recommendations
        """
        recommendations = []
        
        if risk_level == 'High':
            recommendations.append("Consider increasing diversification")
            if concentration > 40:
                recommendations.append("Reduce sector concentration below 30%")
            if positions < 5:
                recommendations.append("Consider adding more positions to reduce single-stock risk")
        
        if concentration > 30:
            recommendations.append("Monitor sector concentration risk")
        
        recommendations.append("Set stop-loss orders at 5-10% below entry points")
        recommendations.append("Review and rebalance portfolio monthly")
        
        return recommendations
    
    def _create_execution_plan(self, portfolio_allocation: Dict) -> Dict:
        """
        Create step-by-step execution plan
        """
        execution_steps = []
        total_value = 0
        
        for sector, sector_data in portfolio_allocation.items():
            for stock in sector_data['stocks']:
                execution_steps.append({
                    'step': len(execution_steps) + 1,
                    'action': 'BUY',
                    'ticker': stock['ticker'],
                    'amount': stock['allocation_amount'],
                    'percentage': stock['allocation_percentage'],
                    'priority': 'High' if stock['sentiment_score'] > 0.1 else 'Medium',
                    'sector': sector.replace('_', ' ').title()
                })
                total_value += stock['allocation_amount']
        
        # Sort by priority and amount
        execution_steps.sort(key=lambda x: (x['priority'] == 'High', x['amount']), reverse=True)
        
        return {
            'execution_steps': execution_steps,
            'total_investment': total_value,
            'estimated_commissions': len(execution_steps) * 10,  # Assume $10 per trade
            'execution_timeline': '1-2 trading days'
        }
    
    def _generate_monitoring_alerts(self, stock_recommendations: Dict) -> List[Dict]:
        """
        Generate monitoring alerts and triggers
        """
        alerts = []
        
        for sector, data in stock_recommendations.items():
            for stock in data['recommended_stocks']:
                ticker = stock['ticker']
                
                alerts.append({
                    'ticker': ticker,
                    'alert_type': 'sentiment_change',
                    'threshold': 'Monitor if sentiment drops below -0.2',
                    'action': 'Consider reducing position if sustained'
                })
                
                alerts.append({
                    'ticker': ticker,
                    'alert_type': 'price_movement',
                    'threshold': 'Alert on 10%+ daily move',
                    'action': 'Reassess position sizing'
                })
        
        # Add sector-level alerts
        alerts.append({
            'alert_type': 'sector_rotation',
            'threshold': 'Weekly sector sentiment analysis',
            'action': 'Rebalance if sector rankings change significantly'
        })
        
        return alerts
    
    def _display_recommendations(self, recommendations: Dict):
        """
        Display formatted recommendations
        """
        print("\n🎯 INVESTMENT RECOMMENDATIONS SUMMARY")
        print("=" * 50)
        
        portfolio = recommendations['portfolio_summary']
        print(f"💰 Portfolio Value: ${portfolio['total_value']:,.0f}")
        print(f"🏭 Sectors: {portfolio['sectors_selected']}")
        print(f"📈 Total Positions: {portfolio['total_positions']}")
        
        risk = recommendations['risk_assessment']
        print(f"⚡ Risk Level: {risk['risk_level']}")
        print(f"🎯 Diversification Score: {risk['diversification_score']:.1f}/100")
        
        print(f"\n📊 SECTOR ALLOCATION:")
        print("-" * 30)
        
        for sector, data in recommendations['portfolio_allocation'].items():
            print(f"\n🏢 {sector.replace('_', ' ').title()}")
            print(f"   Allocation: ${data['sector_allocation']:,.0f} ({data['sector_percentage']:.1f}%)")
            print(f"   Stocks:")
            
            for stock in data['stocks']:
                print(f"      • {stock['ticker']}: ${stock['allocation_amount']:,.0f} "
                      f"({stock['allocation_percentage']:.1f}%) - {stock['recommendation']}")
        
        print(f"\n⚠️  RISK MANAGEMENT:")
        for rec in risk['recommendations']:
            print(f"   • {rec}")

# Test and demonstration
if __name__ == "__main__":
    engine = HybridRecommendationEngine()
    
    print("🚀 Hybrid Investment Recommendation Engine")
    print("Features: Sector Analysis + Stock Selection + Risk Management")
    print("=" * 70)
    
    # Generate recommendations for different risk profiles
    test_cases = [
        {'portfolio_size': 50000, 'risk_tolerance': 'conservative', 'max_sectors': 3},
        {'portfolio_size': 100000, 'risk_tolerance': 'moderate', 'max_sectors': 4},
        {'portfolio_size': 250000, 'risk_tolerance': 'aggressive', 'max_sectors': 6}
    ]
    
    for i, params in enumerate(test_cases, 1):
        print(f"\n{'='*20} TEST CASE {i} {'='*20}")
        recommendations = engine.generate_investment_recommendations(**params)
        
        if 'error' not in recommendations:
            print("✅ Recommendations generated successfully!")
        else:
            print(f"❌ Error: {recommendations['error']}")
        
        print("\n" + "="*50)
