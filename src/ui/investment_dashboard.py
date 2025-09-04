"""
Investment Dashboard - Comprehensive Market Analysis Summary
Combines all advanced features for complete investment decision-making
"""

import json
from datetime import datetime
from typing import Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from analysis_engine.sector_analysis import SectorSentimentAnalyzer
from analysis_engine.hybrid_recommendations import HybridRecommendationEngine
from sentiment_analysis.news_sentiments import (
    analyze_comprehensive_news_sentiment_advanced,
    get_feedback_insights
)

class InvestmentDashboard:
    """
    Comprehensive investment dashboard combining all analysis features
    """
    
    def __init__(self):
        self.sector_analyzer = SectorSentimentAnalyzer()
        self.hybrid_engine = HybridRecommendationEngine()
        
    def generate_comprehensive_analysis(self, 
                                      portfolio_size: float = 100000,
                                      risk_tolerance: str = 'moderate',
                                      focus_tickers: list = None) -> Dict[str, Any]:
        """
        Generate complete investment analysis dashboard
        
        Args:
            portfolio_size: Portfolio value in USD
            risk_tolerance: Risk tolerance level
            focus_tickers: Specific tickers to analyze
            
        Returns:
            Comprehensive analysis results
        """
        print("🎯 COMPREHENSIVE INVESTMENT ANALYSIS DASHBOARD")
        print("=" * 70)
        print(f"💰 Portfolio Size: ${portfolio_size:,.0f}")
        print(f"⚡ Risk Tolerance: {risk_tolerance.title()}")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        dashboard_data = {
            'metadata': {
                'portfolio_size': portfolio_size,
                'risk_tolerance': risk_tolerance,
                'analysis_timestamp': datetime.now().isoformat(),
                'focus_tickers': focus_tickers or []
            }
        }
        
        # 1. Sector Analysis
        print("📊 PHASE 1: SECTOR TREND ANALYSIS")
        print("-" * 40)
        
        try:
            sector_results = self.sector_analyzer.analyze_sector_sentiment()
            dashboard_data['sector_analysis'] = sector_results
            
            if 'sector_rankings' in sector_results:
                rankings = sector_results['sector_rankings']['rankings']
                print(f"✅ Analyzed {len(rankings)} sectors")
                
                if rankings:
                    top_sector = rankings[0]
                    print(f"🥇 Top Sector: {top_sector['sector'].replace('_', ' ').title()}")
                    print(f"   Score: {top_sector['sentiment_score']:+.3f}")
                    print(f"   ETF: {top_sector['etf_ticker']}")
                    
        except Exception as e:
            print(f"⚠️ Sector analysis warning: {e}")
            dashboard_data['sector_analysis'] = {'error': str(e)}
        
        print()
        
        # 2. Hybrid Recommendations
        print("🎯 PHASE 2: HYBRID PORTFOLIO RECOMMENDATIONS")
        print("-" * 45)
        
        try:
            hybrid_results = self.hybrid_engine.generate_investment_recommendations(
                portfolio_size=portfolio_size,
                risk_tolerance=risk_tolerance,
                max_sectors=4,
                stocks_per_sector=2
            )
            dashboard_data['hybrid_recommendations'] = hybrid_results
            
            if 'portfolio_summary' in hybrid_results:
                summary = hybrid_results['portfolio_summary']
                risk = hybrid_results['risk_assessment']
                print(f"✅ Generated recommendations for {summary['sectors_selected']} sectors")
                print(f"📈 Total positions: {summary['total_positions']}")
                print(f"⚡ Risk level: {risk['risk_level']}")
                
        except Exception as e:
            print(f"⚠️ Hybrid recommendations warning: {e}")
            dashboard_data['hybrid_recommendations'] = {'error': str(e)}
        
        print()
        
        # 3. Individual Stock Deep Dive
        if focus_tickers:
            print("📈 PHASE 3: INDIVIDUAL STOCK ANALYSIS")
            print("-" * 40)
            
            stock_analyses = {}
            for ticker in focus_tickers[:5]:  # Limit to 5 for performance
                try:
                    print(f"   🔍 Analyzing {ticker}...")
                    stock_result = analyze_comprehensive_news_sentiment_advanced(ticker)
                    stock_analyses[ticker] = stock_result
                    
                    if 'sentiment_analysis' in stock_result:
                        sentiment = stock_result['sentiment_analysis']
                        print(f"      Sentiment: {sentiment.get('sentiment_label', 'N/A')} "
                              f"({sentiment.get('combined_sentiment_score', 0):+.3f})")
                        
                except Exception as e:
                    print(f"      ⚠️ Error analyzing {ticker}: {e}")
                    stock_analyses[ticker] = {'error': str(e)}
            
            dashboard_data['individual_stocks'] = stock_analyses
            print()
        
        # 4. System Intelligence & Learning
        print("🤖 PHASE 4: AI SYSTEM INTELLIGENCE")
        print("-" * 35)
        
        try:
            feedback_insights = get_feedback_insights()
            dashboard_data['ai_insights'] = feedback_insights
            
            total_feedback = feedback_insights.get('total_feedback_count', 0)
            print(f"🧠 Total AI learning feedback: {total_feedback}")
            
            if total_feedback > 0:
                print(f"   • Sentiment corrections: {feedback_insights.get('sentiment_feedback_count', 0)}")
                print(f"   • Classification corrections: {feedback_insights.get('classification_feedback_count', 0)}")
                
                recommendations = feedback_insights.get('recommendations', [])
                if recommendations:
                    print("   📋 AI Improvement Recommendations:")
                    for rec in recommendations:
                        print(f"      • {rec}")
            else:
                print("   💡 Collect user feedback to improve AI accuracy")
                
        except Exception as e:
            print(f"⚠️ AI insights warning: {e}")
            dashboard_data['ai_insights'] = {'error': str(e)}
        
        print()
        
        # 5. Executive Summary
        self._generate_executive_summary(dashboard_data)
        
        return dashboard_data
    
    def _generate_executive_summary(self, dashboard_data: Dict[str, Any]):
        """
        Generate executive summary of all analyses
        """
        print("📋 EXECUTIVE SUMMARY")
        print("=" * 30)
        
        portfolio_size = dashboard_data['metadata']['portfolio_size']
        risk_tolerance = dashboard_data['metadata']['risk_tolerance']
        
        # Market Outlook
        print("🌍 MARKET OUTLOOK:")
        
        sector_analysis = dashboard_data.get('sector_analysis', {})
        if 'sector_rankings' in sector_analysis:
            rankings = sector_analysis['sector_rankings'].get('rankings', [])
            recommendations = sector_analysis['sector_rankings'].get('recommendations', {})
            
            overweight = recommendations.get('overweight', [])
            underweight = recommendations.get('underweight', [])
            
            if overweight:
                print(f"   🟢 BULLISH on: {', '.join([s.replace('_', ' ').title() for s in overweight])}")
            if underweight:
                print(f"   🔴 BEARISH on: {', '.join([s.replace('_', ' ').title() for s in underweight])}")
            
            if not overweight and not underweight:
                print("   🟡 NEUTRAL market conditions - Favor defensive positioning")
        
        # Portfolio Recommendations
        print("\n💼 PORTFOLIO RECOMMENDATIONS:")
        
        hybrid_recs = dashboard_data.get('hybrid_recommendations', {})
        if 'portfolio_allocation' in hybrid_recs:
            allocation = hybrid_recs['portfolio_allocation']
            risk_assessment = hybrid_recs.get('risk_assessment', {})
            
            print(f"   🎯 Recommended allocation across {len(allocation)} sectors")
            print(f"   ⚡ Risk level: {risk_assessment.get('risk_level', 'Unknown')}")
            print(f"   📊 Diversification score: {risk_assessment.get('diversification_score', 0):.0f}/100")
            
            # Top allocation
            if allocation:
                top_sector = max(allocation.items(), key=lambda x: x[1]['sector_percentage'])
                print(f"   🏆 Largest allocation: {top_sector[0].replace('_', ' ').title()} "
                      f"({top_sector[1]['sector_percentage']:.1f}%)")
        
        # Action Items
        print("\n🎯 IMMEDIATE ACTION ITEMS:")
        
        if hybrid_recs.get('risk_assessment', {}).get('risk_level') == 'High':
            print("   ⚠️  HIGH PRIORITY: Reduce concentration risk")
        
        execution_plan = hybrid_recs.get('execution_plan', {})
        if execution_plan.get('execution_steps'):
            high_priority_trades = [
                step for step in execution_plan['execution_steps'] 
                if step.get('priority') == 'High'
            ]
            print(f"   📈 Execute {len(high_priority_trades)} high-priority trades")
            print(f"   ⏱️  Timeline: {execution_plan.get('execution_timeline', 'N/A')}")
        
        ai_insights = dashboard_data.get('ai_insights', {})
        ai_recommendations = ai_insights.get('recommendations', [])
        if ai_recommendations:
            print("   🤖 AI System Improvements:")
            for rec in ai_recommendations:
                print(f"      • {rec}")
        
        # Performance Monitoring
        print("\n📊 MONITORING SCHEDULE:")
        print("   • Daily: Monitor high-priority positions")
        print("   • Weekly: Review sector sentiment changes")
        print("   • Monthly: Rebalance portfolio allocation")
        print("   • Quarterly: Reassess risk tolerance and objectives")
        
        print(f"\n💡 CONFIDENCE LEVEL: {'High' if len(dashboard_data.keys()) >= 4 else 'Medium'}")
        print("   Based on comprehensive multi-factor analysis")
        
    def save_dashboard_report(self, dashboard_data: Dict[str, Any], filename: str = None) -> str:
        """
        Save dashboard data to JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"investment_dashboard_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        print(f"\n📄 Dashboard report saved: {filename}")
        return filename

# Demo and testing
if __name__ == "__main__":
    dashboard = InvestmentDashboard()
    
    print("🚀 LAUNCHING COMPREHENSIVE INVESTMENT DASHBOARD")
    print("Features: Sector Analysis + Hybrid Recommendations + AI Intelligence")
    print("=" * 80)
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'Conservative Investor',
            'portfolio_size': 250000,
            'risk_tolerance': 'conservative',
            'focus_tickers': ['AAPL', 'MSFT', 'JNJ']
        },
        {
            'name': 'Moderate Growth Portfolio',
            'portfolio_size': 100000,
            'risk_tolerance': 'moderate',
            'focus_tickers': ['TSLA', 'GOOGL', 'JPM']
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*20} SCENARIO {i}: {scenario['name']} {'='*20}")
        
        results = dashboard.generate_comprehensive_analysis(
            portfolio_size=scenario['portfolio_size'],
            risk_tolerance=scenario['risk_tolerance'],
            focus_tickers=scenario['focus_tickers']
        )
        
        # Save report
        filename = f"dashboard_scenario_{i}.json"
        dashboard.save_dashboard_report(results, filename)
        
        print(f"\n✅ Scenario {i} analysis completed!")
        print("="*70)
