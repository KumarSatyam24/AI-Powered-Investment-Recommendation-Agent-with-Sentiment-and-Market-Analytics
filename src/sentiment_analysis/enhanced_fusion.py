"""
Enhanced Sentiment Fusion System
Combines legacy FinBERT sentiment analysis with new MarketAux API for comprehensive sentiment
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.sentiment_analysis.sentiment_model import analyze_sentiment as finbert_sentiment
from src.api_clients.marketaux_api import marketaux_api
from src.data_processing.data_fetch import get_latest_headlines, get_reddit_posts, get_tweets

def enhanced_sentiment_analysis(ticker, use_finbert=True, use_marketaux=True, use_social=True):
    """
    Enhanced sentiment analysis combining multiple sources and methods.
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        use_finbert: Use legacy FinBERT analysis
        use_marketaux: Use MarketAux API sentiment
        use_social: Include Reddit/Twitter sentiment
    
    Returns:
        Dict with comprehensive sentiment analysis
    """
    
    sentiment_data = {
        'overall_sentiment': 'neutral',
        'confidence_score': 0.0,
        'sources': {},
        'analysis_details': {}
    }
    
    scores = []
    weights = []
    
    # 1. MarketAux News Sentiment (High weight - professional news)
    if use_marketaux:
        try:
            marketaux_data = marketaux_api.get_news_sentiment_analysis([ticker], days=7)
            if marketaux_data.get('total_articles', 0) > 0:
                sentiment_dist = marketaux_data.get('sentiment_distribution', {})
                
                # Convert percentage to score (-1 to 1)
                positive_pct = sentiment_dist.get('positive', 0) / 100
                negative_pct = sentiment_dist.get('negative', 0) / 100
                marketaux_score = positive_pct - negative_pct
                
                scores.append(marketaux_score)
                weights.append(0.4)  # 40% weight for professional news
                
                sentiment_data['sources']['marketaux'] = {
                    'score': marketaux_score,
                    'articles_count': marketaux_data.get('total_articles', 0),
                    'sentiment_distribution': sentiment_dist,
                    'overall': marketaux_data.get('overall_sentiment', 'neutral')
                }
        except Exception as e:
            print(f"MarketAux sentiment error: {e}")
    
    # 2. FinBERT Analysis on Recent Headlines (Medium weight - AI analysis)
    if use_finbert:
        try:
            headlines = get_latest_headlines(ticker)
            if headlines:
                finbert_result = finbert_sentiment(headlines)
                
                # Convert to score
                finbert_score = 0.7 if finbert_result == "Positive" else -0.7 if finbert_result == "Negative" else 0.0
                
                scores.append(finbert_score)
                weights.append(0.3)  # 30% weight for FinBERT analysis
                
                sentiment_data['sources']['finbert'] = {
                    'score': finbert_score,
                    'result': finbert_result,
                    'headlines_analyzed': len(headlines),
                    'sample_headlines': headlines[:3]
                }
        except Exception as e:
            print(f"FinBERT sentiment error: {e}")
    
    # 3. Social Media Sentiment (Lower weight - more volatile)
    if use_social:
        try:
            # Reddit sentiment
            reddit_posts = get_reddit_posts(ticker, limit=5)
            reddit_texts = []
            for post in reddit_posts:
                reddit_texts.append(post.get('title', ''))
                reddit_texts.extend(post.get('comments', [])[:2])  # Top 2 comments per post
            
            if reddit_texts:
                reddit_sentiment = finbert_sentiment([text for text in reddit_texts if text])
                reddit_score = 0.5 if reddit_sentiment == "Positive" else -0.5 if reddit_sentiment == "Negative" else 0.0
                
                scores.append(reddit_score)
                weights.append(0.2)  # 20% weight for social sentiment
                
                sentiment_data['sources']['reddit'] = {
                    'score': reddit_score,
                    'result': reddit_sentiment,
                    'posts_analyzed': len(reddit_posts),
                    'texts_count': len(reddit_texts)
                }
        except Exception as e:
            print(f"Reddit sentiment error: {e}")
        
        try:
            # Twitter sentiment
            tweets = get_tweets(ticker, limit=10)
            tweet_texts = [tweet.get('text', '') for tweet in tweets]
            
            if tweet_texts:
                twitter_sentiment = finbert_sentiment(tweet_texts)
                twitter_score = 0.4 if twitter_sentiment == "Positive" else -0.4 if twitter_sentiment == "Negative" else 0.0
                
                scores.append(twitter_score)
                weights.append(0.1)  # 10% weight for Twitter
                
                sentiment_data['sources']['twitter'] = {
                    'score': twitter_score,
                    'result': twitter_sentiment,
                    'tweets_analyzed': len(tweets)
                }
        except Exception as e:
            print(f"Twitter sentiment error: {e}")
    
    # Calculate weighted average
    if scores and weights:
        weighted_score = sum(score * weight for score, weight in zip(scores, weights)) / sum(weights)
        
        # Convert score to sentiment
        if weighted_score > 0.2:
            overall_sentiment = "bullish"
        elif weighted_score > 0.05:
            overall_sentiment = "slightly_positive"
        elif weighted_score < -0.2:
            overall_sentiment = "bearish"
        elif weighted_score < -0.05:
            overall_sentiment = "slightly_negative"
        else:
            overall_sentiment = "neutral"
        
        sentiment_data['overall_sentiment'] = overall_sentiment
        sentiment_data['confidence_score'] = abs(weighted_score)
        sentiment_data['weighted_score'] = weighted_score
    
    # Add analysis summary
    sentiment_data['analysis_details'] = {
        'total_sources': len(scores),
        'methodology': 'Weighted fusion of professional news, AI analysis, and social sentiment',
        'weights_used': {
            'professional_news': '40%',
            'finbert_analysis': '30%',
            'social_media': '30%'
        }
    }
    
    return sentiment_data

def get_sentiment_summary(ticker):
    """Quick sentiment summary for dashboard display."""
    analysis = enhanced_sentiment_analysis(ticker)
    
    return {
        'sentiment': analysis['overall_sentiment'],
        'confidence': analysis['confidence_score'],
        'sources_count': analysis['analysis_details']['total_sources'],
        'details': analysis['sources']
    }

# Legacy compatibility functions
def fuse_sentiments(news_headlines, reddit_posts, twitter_posts):
    """Legacy function for backward compatibility."""
    from src.sentiment_analysis.sentiment_model import analyze_sentiment
    
    news_sentiment = analyze_sentiment(news_headlines)
    reddit_sentiment = analyze_sentiment([post.get('title', '') for post in reddit_posts])
    twitter_sentiment = analyze_sentiment([tweet.get('text', '') for tweet in twitter_posts])

    votes = [news_sentiment, reddit_sentiment, twitter_sentiment]

    pos = votes.count("Positive")
    neg = votes.count("Negative")
    neu = votes.count("Neutral")

    if pos > neg and pos > neu:
        return "Positive"
    elif neg > pos and neg > neu:
        return "Negative"
    else:
        return "Neutral"
