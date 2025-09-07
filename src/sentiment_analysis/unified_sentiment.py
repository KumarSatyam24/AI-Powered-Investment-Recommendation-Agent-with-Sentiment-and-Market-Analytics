"""
Unified Sentiment Analysis Interface
====================================

Combines Twitter, Reddit, and News sentiment analysis with configurable weightings
to provide a comprehensive sentiment score for any stock ticker.
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

# Import individual sentiment analyzers
from .twitter_sentiments import analyze_twitter_sentiment
from .reddit_sentiments import analyze_reddit_sentiment
from .news_sentiments import analyze_comprehensive_news_sentiment_advanced

@dataclass
class SentimentWeights:
    """Configuration for sentiment source weights"""
    twitter: float = 0.3
    reddit: float = 0.3
    news: float = 0.4
    
    def __post_init__(self):
        """Normalize weights to sum to 1.0"""
        total = self.twitter + self.reddit + self.news
        if total != 1.0:
            self.twitter /= total
            self.reddit /= total
            self.news /= total

@dataclass
class SentimentResult:
    """Structured sentiment analysis result"""
    source: str
    overall_sentiment: str
    score: float
    confidence: float
    raw_data: Dict
    articles_count: int = 0
    posts_count: int = 0
    tweets_count: int = 0

@dataclass
class CombinedSentimentResult:
    """Final combined sentiment analysis result"""
    ticker: str
    timestamp: datetime
    overall_sentiment: str
    combined_score: float
    confidence: float
    weights_used: SentimentWeights
    individual_results: Dict[str, SentimentResult]
    summary: Dict

class UnifiedSentimentAnalyzer:
    """
    Unified interface for comprehensive sentiment analysis
    """
    
    def __init__(self, weights: Optional[SentimentWeights] = None):
        """
        Initialize with custom weights or defaults
        
        Args:
            weights: Custom weights for different sentiment sources
        """
        self.weights = weights or SentimentWeights()
        self.sentiment_mapping = {
            'positive': 1.0,
            'neutral': 0.0,
            'negative': -1.0,
            'POSITIVE': 1.0,
            'NEUTRAL': 0.0,
            'NEGATIVE': -1.0
        }
    
    def analyze_comprehensive_sentiment(
        self, 
        ticker: str,
        use_grok_fallback: bool = True,
        include_twitter: bool = True,
        include_reddit: bool = True,
        include_news: bool = True
    ) -> CombinedSentimentResult:
        """
        Perform comprehensive sentiment analysis across all sources
        
        Args:
            ticker: Stock ticker symbol
            use_grok_fallback: Whether to use Grok when APIs fail
            include_twitter: Include Twitter sentiment analysis
            include_reddit: Include Reddit sentiment analysis
            include_news: Include news sentiment analysis
            
        Returns:
            CombinedSentimentResult with weighted sentiment analysis
        """
        print(f"🔍 Comprehensive Sentiment Analysis for {ticker.upper()}")
        print("=" * 80)
        
        individual_results = {}
        
        # Twitter Sentiment Analysis
        if include_twitter:
            try:
                print("\n🐦 Analyzing Twitter Sentiment...")
                twitter_result = self._analyze_twitter_sentiment(ticker, use_grok_fallback)
                individual_results['twitter'] = twitter_result
                print(f"   ✅ Twitter: {twitter_result.overall_sentiment} (Score: {twitter_result.score:.3f})")
            except Exception as e:
                print(f"   ❌ Twitter analysis failed: {e}")
                individual_results['twitter'] = SentimentResult(
                    source="twitter", overall_sentiment="neutral", score=0.0, 
                    confidence=0.0, raw_data={}, tweets_count=0
                )
        
        # Reddit Sentiment Analysis
        if include_reddit:
            try:
                print("\n📱 Analyzing Reddit Sentiment...")
                reddit_result = self._analyze_reddit_sentiment(ticker, use_grok_fallback)
                individual_results['reddit'] = reddit_result
                print(f"   ✅ Reddit: {reddit_result.overall_sentiment} (Score: {reddit_result.score:.3f})")
            except Exception as e:
                print(f"   ❌ Reddit analysis failed: {e}")
                individual_results['reddit'] = SentimentResult(
                    source="reddit", overall_sentiment="neutral", score=0.0,
                    confidence=0.0, raw_data={}, posts_count=0
                )
        
        # News Sentiment Analysis
        if include_news:
            try:
                print("\n📰 Analyzing News Sentiment...")
                news_result = self._analyze_news_sentiment(ticker)
                individual_results['news'] = news_result
                print(f"   ✅ News: {news_result.overall_sentiment} (Score: {news_result.score:.3f})")
            except Exception as e:
                print(f"   ❌ News analysis failed: {e}")
                individual_results['news'] = SentimentResult(
                    source="news", overall_sentiment="neutral", score=0.0,
                    confidence=0.0, raw_data={}, articles_count=0
                )
        
        # Combine results with weights
        combined_result = self._combine_sentiments(ticker, individual_results)
        
        # Display results
        self._display_results(combined_result)
        
        return combined_result
    
    def _analyze_twitter_sentiment(self, ticker: str, use_grok_fallback: bool) -> SentimentResult:
        """Analyze Twitter sentiment and convert to standard format"""
        # Run both FinBERT and general analysis
        finbert_results = analyze_twitter_sentiment(ticker, use_general=False, use_grok_fallback=use_grok_fallback)
        general_results = analyze_twitter_sentiment(ticker, use_general=True, use_grok_fallback=use_grok_fallback)
        
        if not finbert_results:
            return SentimentResult(
                source="twitter", overall_sentiment="neutral", score=0.0,
                confidence=0.0, raw_data={}, tweets_count=0
            )
        
        # Calculate weighted average sentiment
        total_score = 0.0
        total_confidence = 0.0
        tweet_count = len(finbert_results)
        
        for i, result in enumerate(finbert_results):
            # Get FinBERT sentiment (financial focus)
            finbert_sentiment = result.get('sentiment', [{}])
            if isinstance(finbert_sentiment, list) and finbert_sentiment:
                finbert_sentiment = finbert_sentiment[0]
            
            finbert_score = finbert_sentiment.get('score', 0.0) if finbert_sentiment else 0.0
            finbert_label = finbert_sentiment.get('label', 'neutral').lower() if finbert_sentiment else 'neutral'
            
            # Convert to numeric score
            sentiment_value = self.sentiment_mapping.get(finbert_label, 0.0)
            total_score += sentiment_value * finbert_score
            total_confidence += finbert_score
        
        # Calculate averages
        avg_score = total_score / tweet_count if tweet_count > 0 else 0.0
        avg_confidence = total_confidence / tweet_count if tweet_count > 0 else 0.0
        
        # Determine overall sentiment
        if avg_score > 0.1:
            overall_sentiment = "positive"
        elif avg_score < -0.1:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        return SentimentResult(
            source="twitter",
            overall_sentiment=overall_sentiment,
            score=avg_score,
            confidence=avg_confidence,
            raw_data={"finbert": finbert_results, "general": general_results},
            tweets_count=tweet_count
        )
    
    def _analyze_reddit_sentiment(self, ticker: str, use_grok_fallback: bool) -> SentimentResult:
        """Analyze Reddit sentiment and convert to standard format"""
        results = analyze_reddit_sentiment(ticker, use_grok_fallback=use_grok_fallback)
        
        if not results:
            return SentimentResult(
                source="reddit", overall_sentiment="neutral", score=0.0,
                confidence=0.0, raw_data={}, posts_count=0
            )
        
        # Calculate weighted sentiment (posts have 2x weight vs comments)
        total_score = 0.0
        total_weight = 0.0
        total_confidence = 0.0
        post_count = 0
        
        for result in results:
            # Get FinBERT sentiment (financial focus)
            finbert_sentiment = result.get('finbert_sentiment', [{}])
            if isinstance(finbert_sentiment, list) and finbert_sentiment:
                finbert_sentiment = finbert_sentiment[0]
            
            score = finbert_sentiment.get('score', 0.0) if finbert_sentiment else 0.0
            label = finbert_sentiment.get('label', 'neutral').lower() if finbert_sentiment else 'neutral'
            
            # Weight posts higher than comments
            weight = 2.0 if result.get('type') == 'post' else 1.0
            
            sentiment_value = self.sentiment_mapping.get(label, 0.0)
            total_score += sentiment_value * score * weight
            total_weight += weight
            total_confidence += score
            
            if result.get('type') == 'post':
                post_count += 1
        
        # Calculate averages
        avg_score = total_score / total_weight if total_weight > 0 else 0.0
        avg_confidence = total_confidence / len(results) if results else 0.0
        
        # Determine overall sentiment
        if avg_score > 0.1:
            overall_sentiment = "positive"
        elif avg_score < -0.1:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        return SentimentResult(
            source="reddit",
            overall_sentiment=overall_sentiment,
            score=avg_score,
            confidence=avg_confidence,
            raw_data={"results": results},
            posts_count=post_count
        )
    
    def _analyze_news_sentiment(self, ticker: str) -> SentimentResult:
        """Analyze news sentiment and convert to standard format"""
        result = analyze_comprehensive_news_sentiment_advanced(ticker)
        
        if 'error' in result:
            return SentimentResult(
                source="news", overall_sentiment="neutral", score=0.0,
                confidence=0.0, raw_data={"error": result['error']}, articles_count=0
            )
        
        # Extract sentiment information
        combined_score = result.get('combined_sentiment', {}).get('score', 0.0)
        confidence = result.get('combined_sentiment', {}).get('confidence', 0.0)
        
        # Get article counts
        general_count = result.get('general_market', {}).get('articles_analyzed', 0)
        stock_count = result.get('stock_specific', {}).get('articles_analyzed', 0)
        total_articles = general_count + stock_count
        
        # Determine overall sentiment
        if combined_score > 0.1:
            overall_sentiment = "positive"
        elif combined_score < -0.1:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        return SentimentResult(
            source="news",
            overall_sentiment=overall_sentiment,
            score=combined_score,
            confidence=confidence,
            raw_data=result,
            articles_count=total_articles
        )
    
    def _combine_sentiments(self, ticker: str, individual_results: Dict[str, SentimentResult]) -> CombinedSentimentResult:
        """Combine individual sentiment results using weighted average"""
        
        # Calculate weighted score and confidence
        total_weighted_score = 0.0
        total_weighted_confidence = 0.0
        total_weight = 0.0
        
        active_weights = {}
        
        # Apply weights only to available results
        if 'twitter' in individual_results:
            weight = self.weights.twitter
            result = individual_results['twitter']
            total_weighted_score += result.score * weight
            total_weighted_confidence += result.confidence * weight
            total_weight += weight
            active_weights['twitter'] = weight
        
        if 'reddit' in individual_results:
            weight = self.weights.reddit
            result = individual_results['reddit']
            total_weighted_score += result.score * weight
            total_weighted_confidence += result.confidence * weight
            total_weight += weight
            active_weights['reddit'] = weight
        
        if 'news' in individual_results:
            weight = self.weights.news
            result = individual_results['news']
            total_weighted_score += result.score * weight
            total_weighted_confidence += result.confidence * weight
            total_weight += weight
            active_weights['news'] = weight
        
        # Normalize by total active weight
        combined_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        combined_confidence = total_weighted_confidence / total_weight if total_weight > 0 else 0.0
        
        # Determine overall sentiment
        if combined_score > 0.1:
            overall_sentiment = "positive"
        elif combined_score < -0.1:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        # Create summary
        summary = {
            'total_articles': sum(r.articles_count for r in individual_results.values()),
            'total_posts': sum(r.posts_count for r in individual_results.values()),
            'total_tweets': sum(r.tweets_count for r in individual_results.values()),
            'active_sources': list(individual_results.keys()),
            'weights_applied': active_weights
        }
        
        return CombinedSentimentResult(
            ticker=ticker,
            timestamp=datetime.now(),
            overall_sentiment=overall_sentiment,
            combined_score=combined_score,
            confidence=combined_confidence,
            weights_used=self.weights,
            individual_results=individual_results,
            summary=summary
        )
    
    def _display_results(self, result: CombinedSentimentResult):
        """Display comprehensive results in a formatted way"""
        print(f"\n🎯 COMBINED SENTIMENT ANALYSIS RESULTS")
        print("=" * 80)
        print(f"📊 Ticker: {result.ticker.upper()}")
        print(f"⏰ Analyzed: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Overall Sentiment: {result.overall_sentiment.upper()}")
        print(f"📈 Combined Score: {result.combined_score:.3f}")
        print(f"🔮 Confidence: {result.confidence:.3f}")
        
        print(f"\n⚖️  WEIGHTS APPLIED:")
        print(f"   🐦 Twitter: {self.weights.twitter:.1%}")
        print(f"   📱 Reddit: {self.weights.reddit:.1%}")
        print(f"   📰 News: {self.weights.news:.1%}")
        
        print(f"\n📊 DATA SUMMARY:")
        print(f"   📰 Articles Analyzed: {result.summary['total_articles']}")
        print(f"   📱 Reddit Posts: {result.summary['total_posts']}")
        print(f"   🐦 Tweets: {result.summary['total_tweets']}")
        print(f"   🔗 Active Sources: {', '.join(result.summary['active_sources'])}")
        
        print(f"\n📈 INDIVIDUAL RESULTS:")
        for source, res in result.individual_results.items():
            emoji = {"twitter": "🐦", "reddit": "📱", "news": "📰"}.get(source, "📊")
            print(f"   {emoji} {source.title()}: {res.overall_sentiment.upper()} "
                  f"(Score: {res.score:.3f}, Confidence: {res.confidence:.3f})")

# Convenience functions for easy usage
def analyze_stock_sentiment(
    ticker: str,
    twitter_weight: float = 0.3,
    reddit_weight: float = 0.3,
    news_weight: float = 0.4,
    use_grok_fallback: bool = True
) -> CombinedSentimentResult:
    """
    Quick sentiment analysis with custom weights
    
    Args:
        ticker: Stock ticker symbol
        twitter_weight: Weight for Twitter sentiment (0.0 to 1.0)
        reddit_weight: Weight for Reddit sentiment (0.0 to 1.0)
        news_weight: Weight for News sentiment (0.0 to 1.0)
        use_grok_fallback: Use Grok when APIs fail
        
    Returns:
        Combined sentiment analysis result
    """
    weights = SentimentWeights(
        twitter=twitter_weight,
        reddit=reddit_weight,
        news=news_weight
    )
    
    analyzer = UnifiedSentimentAnalyzer(weights)
    return analyzer.analyze_comprehensive_sentiment(
        ticker=ticker,
        use_grok_fallback=use_grok_fallback
    )

def quick_sentiment_check(ticker: str) -> str:
    """
    Quick sentiment check returning just the overall sentiment
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        'positive', 'negative', or 'neutral'
    """
    result = analyze_stock_sentiment(ticker)
    return result.overall_sentiment

# Test the unified system
if __name__ == "__main__":
    print("🚀 Unified Sentiment Analysis System")
    print("Combining Twitter, Reddit, and News sentiment with configurable weights")
    print("=" * 80)
    
    # Test with default weights
    ticker = "AAPL"
    result = analyze_stock_sentiment(ticker)
    
    print(f"\n💡 Quick sentiment check for {ticker}: {quick_sentiment_check(ticker)}")
    
    # Test with custom weights (more emphasis on news)
    print(f"\n🔄 Testing with custom weights (News-heavy)...")
    custom_result = analyze_stock_sentiment(
        ticker=ticker,
        twitter_weight=0.2,
        reddit_weight=0.2,
        news_weight=0.6
    )
