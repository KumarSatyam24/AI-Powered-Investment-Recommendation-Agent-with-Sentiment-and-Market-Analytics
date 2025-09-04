"""
Sector/Domain-based Sentiment Analysis and Trend Prediction
Enhanced system for analyzing market trends by sector/domain for better investment allocation
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import re
from collections import defaultdict
import numpy as np
from typing import Dict, List, Tuple, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sentiment_analysis.news_sentiments import (
    get_general_market_news, 
    analyze_general_market_sentiment,
    classify_financial_news_finbert,
    calculate_time_decay_weight
)

# Sector mapping and classification
SECTOR_MAPPINGS = {
    'technology': {
        'tickers': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'CRM', 'ORCL', 'ADBE'],
        'etf': 'XLK',
        'keywords': [
            'technology', 'tech', 'software', 'cloud', 'ai', 'artificial intelligence',
            'semiconductor', 'chip', 'hardware', 'internet', 'digital', 'cyber',
            'app', 'platform', 'algorithm', 'data center', 'quantum', 'robotics'
        ]
    },
    'healthcare': {
        'tickers': ['JNJ', 'PFE', 'UNH', 'MRK', 'ABBV', 'TMO', 'ABT', 'LLY', 'BMY', 'AMGN'],
        'etf': 'XLV',
        'keywords': [
            'healthcare', 'health', 'pharmaceutical', 'pharma', 'biotech', 'medical',
            'drug', 'vaccine', 'clinical', 'fda', 'medicine', 'hospital', 'therapy',
            'biomedical', 'genomic', 'diagnostic', 'treatment', 'patient'
        ]
    },
    'financial': {
        'tickers': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB'],
        'etf': 'XLF',
        'keywords': [
            'bank', 'banking', 'financial', 'finance', 'credit', 'loan', 'mortgage',
            'insurance', 'investment', 'trading', 'broker', 'wealth', 'asset management',
            'fintech', 'payment', 'cryptocurrency', 'blockchain', 'defi'
        ]
    },
    'energy': {
        'tickers': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PXD', 'MPC', 'VLO', 'PSX', 'HES'],
        'etf': 'XLE',
        'keywords': [
            'energy', 'oil', 'gas', 'petroleum', 'crude', 'natural gas', 'renewable',
            'solar', 'wind', 'coal', 'nuclear', 'electric', 'battery', 'fossil fuel',
            'drilling', 'refinery', 'pipeline', 'opec', 'shale'
        ]
    },
    'consumer_discretionary': {
        'tickers': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TJX', 'LOW', 'BKNG', 'TGT'],
        'etf': 'XLY',
        'keywords': [
            'retail', 'consumer', 'shopping', 'restaurant', 'hotel', 'travel',
            'entertainment', 'automotive', 'luxury', 'fashion', 'gaming',
            'ecommerce', 'marketplace', 'brand', 'advertising', 'media'
        ]
    },
    'consumer_staples': {
        'tickers': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'CL', 'KMB', 'GIS', 'K', 'HSY'],
        'etf': 'XLP',
        'keywords': [
            'food', 'beverage', 'grocery', 'consumer goods', 'household',
            'personal care', 'tobacco', 'alcohol', 'supermarket', 'packaged goods',
            'dairy', 'meat', 'snack', 'drink', 'cleaning'
        ]
    },
    'industrials': {
        'tickers': ['BA', 'CAT', 'GE', 'HON', 'MMM', 'UPS', 'RTX', 'LMT', 'DE', 'UNP'],
        'etf': 'XLI',
        'keywords': [
            'industrial', 'manufacturing', 'aerospace', 'defense', 'construction',
            'machinery', 'equipment', 'transportation', 'logistics', 'shipping',
            'infrastructure', 'railway', 'airline', 'freight', 'supply chain'
        ]
    },
    'materials': {
        'tickers': ['LIN', 'APD', 'SHW', 'FCX', 'NEM', 'ECL', 'DD', 'DOW', 'PPG', 'IFF'],
        'etf': 'XLB',
        'keywords': [
            'materials', 'chemicals', 'mining', 'metals', 'steel', 'aluminum',
            'copper', 'gold', 'silver', 'commodity', 'paper', 'packaging',
            'glass', 'cement', 'fertilizer', 'plastic'
        ]
    },
    'utilities': {
        'tickers': ['NEE', 'DUK', 'SO', 'D', 'EXC', 'AEP', 'XEL', 'SRE', 'PEG', 'ED'],
        'etf': 'XLU',
        'keywords': [
            'utility', 'utilities', 'electric', 'electricity', 'power', 'grid',
            'water', 'natural gas', 'renewable energy', 'solar power', 'wind power'
        ]
    },
    'real_estate': {
        'tickers': ['AMT', 'PLD', 'CCI', 'EQIX', 'WELL', 'DLR', 'PSA', 'O', 'CBRE', 'AVB'],
        'etf': 'XLRE',
        'keywords': [
            'real estate', 'property', 'reit', 'housing', 'commercial', 'residential',
            'office', 'retail space', 'warehouse', 'data center', 'hotel',
            'apartment', 'mortgage', 'construction', 'development'
        ]
    },
    'communication': {
        'tickers': ['META', 'GOOGL', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'CHTR', 'TMUS', 'ATVI'],
        'etf': 'XLC',
        'keywords': [
            'communication', 'telecommunications', 'telecom', 'media', 'social media',
            'streaming', 'entertainment', 'content', 'gaming', 'wireless',
            'broadband', 'cable', 'satellite', 'internet service'
        ]
    }
}

class SectorSentimentAnalyzer:
    """
    Advanced sector-based sentiment analysis for market trend prediction
    """
    
    def __init__(self):
        self.sector_mappings = SECTOR_MAPPINGS
        self.sector_cache = {}
        
    def classify_article_by_sector(self, headline: str, summary: str = "", ticker: str = None) -> Dict:
        """
        Classify article by sector using multiple methods:
        1. Direct ticker mapping
        2. Keyword analysis
        3. FinBERT-enhanced content analysis
        """
        sectors_found = []
        confidence_scores = {}
        
        # Method 1: Direct ticker mapping
        if ticker:
            ticker_upper = ticker.upper()
            for sector, data in self.sector_mappings.items():
                if ticker_upper in data['tickers']:
                    sectors_found.append(sector)
                    confidence_scores[sector] = 1.0
                    break
        
        # Method 2: Keyword analysis
        content = f"{headline} {summary}".lower()
        for sector, data in self.sector_mappings.items():
            keyword_matches = sum(1 for keyword in data['keywords'] if keyword in content)
            if keyword_matches > 0:
                confidence = min(1.0, keyword_matches / len(data['keywords']) * 10)  # Scale up
                if confidence > 0.1:  # Minimum threshold
                    if sector not in sectors_found:
                        sectors_found.append(sector)
                    confidence_scores[sector] = max(confidence_scores.get(sector, 0), confidence)
        
        # Method 3: Enhanced detection for sector-specific terms
        sector_patterns = {
            'technology': r'\b(tech|software|app|platform|cloud|AI|chip|semiconductor)\b',
            'healthcare': r'\b(health|medical|pharma|drug|vaccine|clinical|FDA)\b',
            'financial': r'\b(bank|finance|credit|trading|investment|fintech)\b',
            'energy': r'\b(oil|gas|energy|solar|wind|nuclear|battery)\b'
        }
        
        for sector, pattern in sector_patterns.items():
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            if matches > 0:
                enhanced_confidence = min(1.0, matches * 0.3)
                if sector not in sectors_found and enhanced_confidence > 0.2:
                    sectors_found.append(sector)
                    confidence_scores[sector] = enhanced_confidence
                elif sector in confidence_scores:
                    confidence_scores[sector] = min(1.0, confidence_scores[sector] + enhanced_confidence * 0.5)
        
        # Return best match or general market if no specific sector found
        if sectors_found:
            best_sector = max(sectors_found, key=lambda s: confidence_scores.get(s, 0))
            return {
                'sector': best_sector,
                'confidence': confidence_scores[best_sector],
                'all_matches': {s: confidence_scores[s] for s in sectors_found},
                'method': 'ticker' if ticker and best_sector in [s for s, d in self.sector_mappings.items() if ticker.upper() in d['tickers']] else 'keyword'
            }
        
        return {
            'sector': 'general_market',
            'confidence': 0.5,
            'all_matches': {},
            'method': 'fallback'
        }
    
    def analyze_sector_sentiment(self, sector: str = None, days_back: int = 7) -> Dict:
        """
        Analyze sentiment for a specific sector or all sectors
        """
        print(f"🏭 Sector Sentiment Analysis: {sector or 'All Sectors'}")
        print("=" * 60)
        
        try:
            # Get general market news (we'll classify by sector)
            articles = get_general_market_news()
            
            # Classify articles by sector
            sector_articles = defaultdict(list)
            
            for article in articles:
                headline = article.get('headline', '')
                summary = article.get('summary', '')
                
                # Extract ticker if available from headline/summary
                ticker_match = re.search(r'\b([A-Z]{2,5})\b', f"{headline} {summary}")
                ticker = ticker_match.group(1) if ticker_match else None
                
                # Classify by sector
                sector_classification = self.classify_article_by_sector(headline, summary, ticker)
                article_sector = sector_classification['sector']
                
                # Add sector metadata to article
                article['sector_classification'] = sector_classification
                article['assigned_sector'] = article_sector
                
                # Add financial classification
                financial_classification = classify_financial_news_finbert(f"{headline} {summary}")
                article['financial_classification'] = financial_classification
                
                # Add time weight
                time_weight = calculate_time_decay_weight(article.get('publishedAt', ''))
                article['time_weight'] = time_weight
                
                # Group by sector
                sector_articles[article_sector].append(article)
            
            # Analyze sentiment for each sector
            sector_results = {}
            
            target_sectors = [sector] if sector else list(self.sector_mappings.keys()) + ['general_market']
            
            for target_sector in target_sectors:
                if target_sector in sector_articles:
                    articles_for_sector = sector_articles[target_sector]
                    sector_sentiment = self._calculate_sector_sentiment(articles_for_sector, target_sector)
                    sector_results[target_sector] = sector_sentiment
            
            # Generate sector rankings and recommendations
            sector_rankings = self._rank_sectors(sector_results)
            
            return {
                'sector_analysis': sector_results,
                'sector_rankings': sector_rankings,
                'total_articles_analyzed': len(articles),
                'articles_by_sector': {s: len(arts) for s, arts in sector_articles.items()},
                'analysis_timestamp': datetime.now().isoformat(),
                'methodology': 'sector_classification_with_sentiment'
            }
            
        except Exception as e:
            print(f"❌ Error in sector sentiment analysis: {e}")
            return {'error': str(e)}
    
    def _calculate_sector_sentiment(self, articles: List[Dict], sector: str) -> Dict:
        """
        Calculate comprehensive sentiment metrics for a sector
        """
        if not articles:
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'Neutral',
                'confidence': 0.0,
                'article_count': 0,
                'financial_articles': 0,
                'avg_time_weight': 0.0,
                'articles': []
            }
        
        total_score = 0.0
        total_weight = 0.0
        financial_count = 0
        time_weights = []
        processed_articles = []
        
        for article in articles:
            # Get or calculate sentiment score
            score = article.get('score', 0.0)
            if not score:
                # Simple sentiment calculation if not available
                headline = article.get('headline', '')
                positive_words = ['positive', 'growth', 'increase', 'rise', 'gain', 'strong', 'beat', 'exceed']
                negative_words = ['negative', 'decline', 'decrease', 'fall', 'loss', 'weak', 'miss', 'disappoint']
                
                pos_count = sum(1 for word in positive_words if word in headline.lower())
                neg_count = sum(1 for word in negative_words if word in headline.lower())
                score = (pos_count - neg_count) * 0.2  # Simple scoring
            
            # Apply time decay
            time_weight = article.get('time_weight', 1.0)
            weighted_score = score * time_weight
            
            # Check if financial
            is_financial = article.get('financial_classification', {}).get('is_financial', False)
            if is_financial:
                financial_count += 1
            
            total_score += weighted_score
            total_weight += time_weight
            time_weights.append(time_weight)
            
            processed_articles.append({
                'headline': article.get('headline', ''),
                'source': article.get('source', 'Unknown'),
                'score': score,
                'weighted_score': weighted_score,
                'time_weight': time_weight,
                'is_financial': is_financial,
                'sector_confidence': article.get('sector_classification', {}).get('confidence', 0.0)
            })
        
        # Calculate averages
        avg_sentiment = total_score / len(articles) if articles else 0.0
        avg_time_weight = sum(time_weights) / len(time_weights) if time_weights else 0.0
        financial_ratio = financial_count / len(articles) if articles else 0.0
        
        # Determine sentiment label
        if avg_sentiment > 0.1:
            sentiment_label = 'Positive'
        elif avg_sentiment < -0.1:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Neutral'
        
        # Calculate confidence based on article count and consistency
        confidence = min(1.0, len(articles) / 10.0)  # More articles = higher confidence
        
        return {
            'sentiment_score': round(avg_sentiment, 3),
            'sentiment_label': sentiment_label,
            'confidence': round(confidence, 3),
            'article_count': len(articles),
            'financial_articles': financial_count,
            'financial_ratio': round(financial_ratio, 3),
            'avg_time_weight': round(avg_time_weight, 3),
            'etf_ticker': self.sector_mappings.get(sector, {}).get('etf', 'N/A'),
            'articles': processed_articles[:5]  # Top 5 articles for review
        }
    
    def _rank_sectors(self, sector_results: Dict) -> Dict:
        """
        Rank sectors by sentiment and generate investment recommendations
        """
        # Filter out sectors with insufficient data
        valid_sectors = {
            sector: data for sector, data in sector_results.items() 
            if data.get('article_count', 0) >= 2 and sector != 'general_market'
        }
        
        if not valid_sectors:
            return {
                'rankings': [],
                'recommendations': {'overweight': [], 'neutral': [], 'underweight': []},
                'top_sectors': [],
                'bottom_sectors': []
            }
        
        # Sort by sentiment score (weighted by confidence)
        sorted_sectors = sorted(
            valid_sectors.items(),
            key=lambda x: x[1]['sentiment_score'] * x[1]['confidence'],
            reverse=True
        )
        
        rankings = []
        for i, (sector, data) in enumerate(sorted_sectors):
            rankings.append({
                'rank': i + 1,
                'sector': sector,
                'sentiment_score': data['sentiment_score'],
                'confidence': data['confidence'],
                'article_count': data['article_count'],
                'etf_ticker': data.get('etf_ticker', 'N/A'),
                'recommendation': self._get_sector_recommendation(data['sentiment_score'], data['confidence'])
            })
        
        # Generate investment recommendations
        num_sectors = len(rankings)
        top_third = max(1, num_sectors // 3)
        bottom_third = max(1, num_sectors // 3)
        
        recommendations = {
            'overweight': [r['sector'] for r in rankings[:top_third] if r['sentiment_score'] > 0.1],
            'neutral': [r['sector'] for r in rankings[top_third:-bottom_third] if rankings],
            'underweight': [r['sector'] for r in rankings[-bottom_third:] if r['sentiment_score'] < -0.1]
        }
        
        return {
            'rankings': rankings,
            'recommendations': recommendations,
            'top_sectors': rankings[:3],
            'bottom_sectors': rankings[-3:] if len(rankings) >= 3 else []
        }
    
    def _get_sector_recommendation(self, sentiment_score: float, confidence: float) -> str:
        """
        Generate investment recommendation based on sentiment and confidence
        """
        if confidence < 0.3:
            return 'HOLD - Low Confidence'
        
        if sentiment_score > 0.2:
            return 'BUY - Positive Sentiment'
        elif sentiment_score > 0.05:
            return 'MODERATE BUY'
        elif sentiment_score < -0.2:
            return 'SELL - Negative Sentiment'
        elif sentiment_score < -0.05:
            return 'MODERATE SELL'
        else:
            return 'HOLD - Neutral'
    
    def generate_sector_report(self, output_file: str = None) -> str:
        """
        Generate comprehensive sector analysis report
        """
        print("📊 Generating Comprehensive Sector Analysis Report")
        print("=" * 50)
        
        # Run analysis for all sectors
        results = self.analyze_sector_sentiment()
        
        if 'error' in results:
            return f"Error generating report: {results['error']}"
        
        # Generate report
        report_lines = []
        report_lines.append("🏭 SECTOR SENTIMENT ANALYSIS REPORT")
        report_lines.append("=" * 50)
        report_lines.append(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"📰 Total Articles Analyzed: {results['total_articles_analyzed']}")
        report_lines.append("")
        
        # Sector Rankings
        rankings = results['sector_rankings']['rankings']
        if rankings:
            report_lines.append("🏆 SECTOR RANKINGS (By Sentiment)")
            report_lines.append("-" * 40)
            for ranking in rankings:
                report_lines.append(
                    f"{ranking['rank']:2d}. {ranking['sector'].replace('_', ' ').title():20s} "
                    f"| Score: {ranking['sentiment_score']:6.3f} "
                    f"| Confidence: {ranking['confidence']:5.3f} "
                    f"| ETF: {ranking['etf_ticker']:6s} "
                    f"| {ranking['recommendation']}"
                )
            report_lines.append("")
        
        # Investment Recommendations
        recommendations = results['sector_rankings']['recommendations']
        report_lines.append("💰 INVESTMENT RECOMMENDATIONS")
        report_lines.append("-" * 30)
        
        if recommendations['overweight']:
            report_lines.append("🟢 OVERWEIGHT (Positive Sentiment):")
            for sector in recommendations['overweight']:
                etf = self.sector_mappings.get(sector, {}).get('etf', 'N/A')
                report_lines.append(f"   • {sector.replace('_', ' ').title()} (ETF: {etf})")
        
        if recommendations['underweight']:
            report_lines.append("🔴 UNDERWEIGHT (Negative Sentiment):")
            for sector in recommendations['underweight']:
                etf = self.sector_mappings.get(sector, {}).get('etf', 'N/A')
                report_lines.append(f"   • {sector.replace('_', ' ').title()} (ETF: {etf})")
        
        if recommendations['neutral']:
            report_lines.append("🟡 NEUTRAL (Hold Current Position):")
            for sector in recommendations['neutral']:
                etf = self.sector_mappings.get(sector, {}).get('etf', 'N/A')
                report_lines.append(f"   • {sector.replace('_', ' ').title()} (ETF: {etf})")
        
        report_lines.append("")
        
        # Detailed Analysis
        report_lines.append("📈 DETAILED SECTOR ANALYSIS")
        report_lines.append("-" * 30)
        
        for sector, data in results['sector_analysis'].items():
            if data['article_count'] > 0:
                report_lines.append(f"\n🏢 {sector.replace('_', ' ').title()}")
                report_lines.append(f"   Sentiment: {data['sentiment_label']} ({data['sentiment_score']:+.3f})")
                report_lines.append(f"   Articles: {data['article_count']} ({data['financial_articles']} financial)")
                report_lines.append(f"   Confidence: {data['confidence']:.3f}")
                report_lines.append(f"   ETF Ticker: {data.get('etf_ticker', 'N/A')}")
                report_lines.append(f"   Avg Time Weight: {data['avg_time_weight']:.3f}")
        
        report_content = "\n".join(report_lines)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_content)
            print(f"📄 Report saved to: {output_file}")
        
        # Print to console
        print(report_content)
        
        return report_content

# Main execution and testing
if __name__ == "__main__":
    analyzer = SectorSentimentAnalyzer()
    
    # Generate comprehensive sector report
    print("🚀 Starting Sector-Based Investment Analysis")
    print("=" * 60)
    
    report = analyzer.generate_sector_report('sector_analysis_report.txt')
    
    print("\n✅ Sector analysis completed!")
    print("💡 This analysis helps with:")
    print("   • Sector rotation strategies")
    print("   • ETF allocation decisions")  
    print("   • Risk management via diversification")
    print("   • Trend identification and timing")
