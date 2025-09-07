"""
Optimized News Sentiment Analysis Module
Core functions for comprehensive sentiment analysis with NewsAPI and MarketAux integration
"""

from src.data_processing.data_fetch import get_latest_headlines
from src.api_clients.marketaux_api import marketaux_api
from newsapi import NewsApiClient
from transformers import pipeline
import torch
from datetime import datetime, timedelta
import sys
import os
import re
from collections import defaultdict
import hashlib

# Set device for PyTorch
device = 0 if torch.cuda.is_available() else -1

# Initialize sentiment analyzers
try:
    print("Loading FinBERT sentiment analyzer...")
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model="ProsusAI/finbert",
        framework="pt",
        device=device
    )
    print("✅ FinBERT sentiment analyzer loaded successfully")
except Exception as e:
    print(f"❌ Error loading FinBERT: {e}")
    sentiment_analyzer = None

try:
    general_sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        framework="pt",
        device=device
    )
except Exception as e:
    print(f"❌ Error loading DistilBERT: {e}")
    general_sentiment_analyzer = None

# Configuration
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
FINANCIAL_KEYWORDS = [
    'earnings', 'revenue', 'profit', 'quarterly', 'dividend', 'stock', 'share',
    'market', 'trading', 'investment', 'financial', 'economy', 'price',
    'analyst', 'forecast', 'guidance', 'sec', 'ipo', 'merger', 'acquisition'
]

def classify_financial_news_finbert(text):
    """
    Enhanced financial news classification using keyword matching.
    """
    if not text:
        return {'is_financial': False, 'confidence': 0, 'type': False}
    
    text_lower = text.lower()
    
    # Count financial keyword matches
    matches = sum(1 for keyword in FINANCIAL_KEYWORDS if keyword in text_lower)
    
    # Calculate confidence score
    text_length = len(text.split())
    confidence = min(matches / max(text_length * 0.1, 1), 1.0)
    
    # Determine if financial
    is_financial = matches >= 2 or confidence > 0.2
    
    return {
        'is_financial': is_financial,
        'confidence': confidence,
        'type': is_financial,
        'keyword_matches': matches
    }

def calculate_time_decay_weight(published_at_str, max_age_hours=72):
    """
    Calculate time decay weight for news articles.
    Recent articles get higher weight.
    """
    if not published_at_str:
        return 1.0
    
    try:
        if 'T' in published_at_str:
            published_time = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
        else:
            published_time = datetime.strptime(published_at_str, '%Y-%m-%d %H:%M:%S')
        
        now = datetime.now(published_time.tzinfo) if published_time.tzinfo else datetime.now()
        time_diff = now - published_time
        hours_ago = time_diff.total_seconds() / 3600
        
        if hours_ago <= 0:
            return 1.0
        elif hours_ago >= max_age_hours:
            return 0.3
        else:
            return 1.0 - (hours_ago / max_age_hours) * 0.7
    except:
        return 1.0

def get_general_market_news():
    """
    Fetch general market news from both NewsAPI and MarketAux.
    """
    all_articles = []
    seen_urls = set()
    newsapi_count = 0
    marketaux_count = 0
    
    # NewsAPI
    if NEWS_API_KEY and NEWS_API_KEY != "YOUR_NEWSAPI_KEY":
        try:
            newsapi = NewsApiClient(api_key=NEWS_API_KEY)
            news_response = newsapi.get_everything(
                q="stock market OR financial markets OR economy",
                language="en",
                sort_by="publishedAt",
                page_size=30,
                domains="reuters.com,bloomberg.com,cnbc.com,wsj.com,ft.com,marketwatch.com"
            )
            
            for article in news_response['articles']:
                url = article.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_articles.append({
                        'headline': article.get('title', ''),
                        'summary': article.get('description', '') or article.get('content', '')[:200] + '...',
                        'source': f"NewsAPI-{article.get('source', {}).get('name', 'Unknown')}",
                        'url': url,
                        'publishedAt': article.get('publishedAt', ''),
                        'source_type': 'newsapi'
                    })
                    newsapi_count += 1
                    
        except Exception as e:
            print(f"Error fetching NewsAPI general news: {e}")
    
    # MarketAux
    try:
        marketaux_news = marketaux_api.get_market_news(
            symbols=[],
            limit=20
        )
        
        if marketaux_news and 'data' in marketaux_news:
            for article in marketaux_news['data']:
                url = article.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_articles.append({
                        'headline': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'source': f"MarketAux-{article.get('source', 'Unknown')}",
                        'url': url,
                        'publishedAt': article.get('published_at', ''),
                        'source_type': 'marketaux'
                    })
                    marketaux_count += 1
                    
    except Exception as e:
        print(f"Error fetching MarketAux general news: {e}")
    
    print(f"✅ NewsAPI: Retrieved {newsapi_count} articles")
    print(f"✅ MarketAux: Retrieved {marketaux_count} articles")
    print(f"📊 Total articles before deduplication: {newsapi_count + marketaux_count} (NewsAPI: {newsapi_count}, MarketAux: {marketaux_count})")
    
    # Deduplicate by content similarity
    final_articles = []
    seen_headlines = set()
    
    for article in all_articles:
        headline = article['headline'].lower().strip()
        headline_hash = hashlib.md5(headline.encode()).hexdigest()[:10]
        
        if headline_hash not in seen_headlines and len(headline) > 10:
            seen_headlines.add(headline_hash)
            final_articles.append(article)
    
    final_newsapi = sum(1 for a in final_articles if a['source_type'] == 'newsapi')
    final_marketaux = sum(1 for a in final_articles if a['source_type'] == 'marketaux')
    print(f"📈 Final unique articles: {len(final_articles)} (NewsAPI: {final_newsapi}, MarketAux: {final_marketaux})")
    
    return final_articles

def analyze_general_market_sentiment():
    """
    Analyze sentiment of general financial market news.
    """
    print("🌍 Fetching General Market News...")
    articles = get_general_market_news()
    
    sentiments = []
    for article in articles:
        try:
            headline = article['headline']
            summary = article['summary']
            
            # Enhanced financial classification
            classification_result = classify_financial_news_finbert(f"{headline} {summary}")
            news_type = classification_result['is_financial']
            classification_confidence = classification_result['confidence']
            
            # Calculate time decay weight
            time_weight = calculate_time_decay_weight(article.get('publishedAt', ''))
            
            # Combine headline and summary for analysis
            combined_text = f"{headline}. {summary}" if summary else headline
            
            # Sentiment analysis
            finbert_sentiment = sentiment_analyzer(combined_text)[0] if sentiment_analyzer else None
            general_sentiment = general_sentiment_analyzer(combined_text)[0] if general_sentiment_analyzer else None
            
            # Calculate final sentiment score
            finbert_score = finbert_sentiment['score'] if finbert_sentiment else 0
            general_score = general_sentiment['score'] if general_sentiment else 0
            final_score = (finbert_score * 0.7 + general_score * 0.3) if finbert_sentiment or general_sentiment else 0
            
            sentiments.append({
                "headline": headline,
                "summary": summary,
                "source": article.get('source', 'Unknown'),
                "url": article.get('url', ''),
                "score": final_score,
                "is_financial": news_type,
                "time_weight": time_weight,
                "news_classification": {
                    "type": news_type,
                    "confidence": classification_confidence
                },
                "combined_analysis": {
                    "finbert_sentiment": finbert_sentiment,
                    "general_sentiment": general_sentiment
                },
                "category": "general_market"
            })
        except Exception as e:
            print(f"Error analyzing article: {e}")
    
    return sentiments

def analyze_stock_specific_sentiment(ticker):
    """
    Analyze sentiment of news specific to a particular stock.
    """
    print(f"📈 Fetching {ticker}-Specific News...")
    
    stock_articles = []
    newsapi_count = 0
    marketaux_count = 0
    seen_urls = set()
    
    # NewsAPI
    if NEWS_API_KEY and NEWS_API_KEY != "YOUR_NEWSAPI_KEY":
        try:
            newsapi = NewsApiClient(api_key=NEWS_API_KEY)
            search_terms = [ticker, f"{ticker} stock", f"{ticker} earnings", f"{ticker} shares"]
            
            for term in search_terms:
                try:
                    news_response = newsapi.get_everything(
                        q=term,
                        language="en",
                        sort_by="publishedAt",
                        page_size=3,
                        domains="reuters.com,bloomberg.com,cnbc.com,wsj.com,ft.com,marketwatch.com"
                    )
                    for article in news_response['articles']:
                        url = article.get('url', '')
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            stock_articles.append({
                                'headline': article.get('title', ''),
                                'summary': article.get('description', '') or article.get('content', '')[:200] + '...',
                                'source': f"NewsAPI-{article.get('source', {}).get('name', 'Unknown')}",
                                'url': url,
                                'publishedAt': article.get('publishedAt', ''),
                                'source_type': 'newsapi'
                            })
                            newsapi_count += 1
                except Exception as e:
                    print(f"Error fetching NewsAPI term '{term}': {e}")
        except Exception as e:
            print(f"Error with NewsAPI: {e}")
    
    # MarketAux
    try:
        marketaux_news = marketaux_api.get_market_news(
            symbols=[ticker],
            limit=10
        )
        
        if marketaux_news and 'data' in marketaux_news:
            for article in marketaux_news['data']:
                url = article.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    stock_articles.append({
                        'headline': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'source': f"MarketAux-{article.get('source', 'Unknown')}",
                        'url': url,
                        'publishedAt': article.get('published_at', ''),
                        'source_type': 'marketaux'
                    })
                    marketaux_count += 1
    except Exception as e:
        print(f"Error fetching MarketAux stock news: {e}")
    
    print(f"✅ NewsAPI: Retrieved {newsapi_count} {ticker}-specific articles")
    print(f"✅ MarketAux: Retrieved {marketaux_count} {ticker}-specific articles")
    
    # Deduplicate
    final_articles = []
    seen_headlines = set()
    
    for article in stock_articles:
        headline = article['headline'].lower().strip()
        headline_hash = hashlib.md5(headline.encode()).hexdigest()[:10]
        
        if headline_hash not in seen_headlines and len(headline) > 10:
            seen_headlines.add(headline_hash)
            final_articles.append(article)
    
    final_newsapi = sum(1 for a in final_articles if a['source_type'] == 'newsapi')
    final_marketaux = sum(1 for a in final_articles if a['source_type'] == 'marketaux')
    print(f"📊 Total {ticker} articles before deduplication: {newsapi_count + marketaux_count} (NewsAPI: {newsapi_count}, MarketAux: {marketaux_count})")
    print(f"📈 Final unique {ticker} articles: {len(final_articles)} (NewsAPI: {final_newsapi}, MarketAux: {final_marketaux})")
    
    # Analyze sentiment for each article
    sentiments = []
    for article in final_articles:
        try:
            headline = article['headline']
            summary = article['summary']
            
            # Financial classification
            classification_result = classify_financial_news_finbert(f"{headline} {summary}")
            news_type = classification_result['is_financial']
            classification_confidence = classification_result['confidence']
            
            # Time decay weight
            time_weight = calculate_time_decay_weight(article.get('publishedAt', ''))
            
            # Sentiment analysis
            combined_text = f"{headline}. {summary}" if summary else headline
            finbert_sentiment = sentiment_analyzer(combined_text)[0] if sentiment_analyzer else None
            general_sentiment = general_sentiment_analyzer(combined_text)[0] if general_sentiment_analyzer else None
            
            # Calculate final score
            finbert_score = finbert_sentiment['score'] if finbert_sentiment else 0
            general_score = general_sentiment['score'] if general_sentiment else 0
            final_score = (finbert_score * 0.7 + general_score * 0.3) if finbert_sentiment or general_sentiment else 0
            
            sentiments.append({
                "headline": headline,
                "summary": summary,
                "source": article.get('source', 'Unknown'),
                "url": article.get('url', ''),
                "score": final_score,
                "is_financial": news_type,
                "time_weight": time_weight,
                "news_classification": {
                    "type": news_type,
                    "confidence": classification_confidence
                },
                "combined_analysis": {
                    "finbert_sentiment": finbert_sentiment,
                    "general_sentiment": general_sentiment
                },
                "category": "stock_specific"
            })
        except Exception as e:
            print(f"Error analyzing article: {e}")
    
    return sentiments

def analyze_comprehensive_news_sentiment_advanced(ticker_symbol):
    """
    Enhanced comprehensive news sentiment analysis with all advanced features.
    """
    print(f"\n🚀 Advanced News Sentiment Analysis for {ticker_symbol}")
    print("=" * 60)
    
    try:
        # Get general market and stock-specific sentiments
        general_sentiments = analyze_general_market_sentiment()
        stock_sentiments = analyze_stock_specific_sentiment(ticker_symbol)
        
        # Apply time decay weighting
        for item in general_sentiments:
            if 'publishedAt' in item:
                time_weight = calculate_time_decay_weight(item['publishedAt'])
                item['time_weight'] = time_weight
                item['weighted_score'] = item.get('score', 0) * time_weight
            else:
                item['time_weight'] = 1.0
                item['weighted_score'] = item.get('score', 0)
        
        for item in stock_sentiments:
            if 'publishedAt' in item:
                time_weight = calculate_time_decay_weight(item['publishedAt'])
                item['time_weight'] = time_weight
                item['weighted_score'] = item.get('score', 0) * time_weight
            else:
                item['time_weight'] = 1.0
                item['weighted_score'] = item.get('score', 0)
        
        # Calculate weighted averages
        general_weighted_avg = sum(item.get('weighted_score', 0) for item in general_sentiments) / max(len(general_sentiments), 1)
        stock_weighted_avg = sum(item.get('weighted_score', 0) for item in stock_sentiments) / max(len(stock_sentiments), 1)
        
        # Calculate average time weights
        general_avg_time_weight = sum(item.get('time_weight', 1.0) for item in general_sentiments) / max(len(general_sentiments), 1)
        stock_avg_time_weight = sum(item.get('time_weight', 1.0) for item in stock_sentiments) / max(len(stock_sentiments), 1)
        
        # Calculate final sentiment
        final_sentiment = (0.4 * general_weighted_avg) + (0.6 * stock_weighted_avg)
        
        # Determine sentiment label
        if final_sentiment > 0.1:
            sentiment_label = 'Positive'
        elif final_sentiment < -0.1:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Neutral'
        
        return {
            'ticker': ticker_symbol,
            'analysis_type': 'advanced_comprehensive',
            'sentiment_analysis': {
                'combined_sentiment_score': round(final_sentiment, 3),
                'sentiment_label': sentiment_label,
                'weights': {
                    'general_market_weight': 0.4,
                    'stock_specific_weight': 0.6
                },
                'component_analysis': {
                    'general_market': {
                        'average_sentiment': round(general_weighted_avg, 3),
                        'article_count': len(general_sentiments),
                        'financial_articles': sum(1 for item in general_sentiments if item.get('is_financial', False)),
                        'financial_ratio': sum(1 for item in general_sentiments if item.get('is_financial', False)) / max(len(general_sentiments), 1),
                        'avg_time_weight': round(general_avg_time_weight, 3)
                    },
                    'stock_specific': {
                        'average_sentiment': round(stock_weighted_avg, 3),
                        'article_count': len(stock_sentiments),
                        'financial_articles': sum(1 for item in stock_sentiments if item.get('is_financial', False)),
                        'financial_ratio': sum(1 for item in stock_sentiments if item.get('is_financial', False)) / max(len(stock_sentiments), 1),
                        'avg_time_weight': round(stock_avg_time_weight, 3)
                    }
                },
                'metadata': {
                    'time_decay_applied': True,
                    'analysis_timestamp': datetime.now().isoformat()
                }
            },
            'detailed_breakdown': {
                'general_market_articles': general_sentiments,
                'stock_specific_articles': stock_sentiments
            },
            'advanced_features': {
                'time_decay_weighting': True,
                'financial_classification': True,
                'multi_source_integration': True
            },
            'user_feedback_insights': {
                'total_feedback_entries': 0,
                'sentiment_corrections': 0,
                'classification_corrections': 0
            },
            'analysis_metadata': {
                'analysis_version': '2.0_optimized',
                'model_versions': {
                    'finbert': 'ProsusAI/finbert',
                    'general_sentiment': 'distilbert-base-uncased-finetuned-sst-2-english'
                },
                'data_sources': ['NewsAPI', 'MarketAux'],
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"⚠️ Error in advanced sentiment analysis: {e}")
        return {
            'ticker': ticker_symbol,
            'error': str(e),
            'analysis_type': 'failed'
        }

def get_feedback_insights():
    """
    Get user feedback insights (placeholder for future implementation).
    """
    return {
        'total_feedback_entries': 0,
        'sentiment_corrections': 0,
        'classification_corrections': 0,
        'accuracy_improvements': 0.0
    }

# Backward compatibility functions
def analyze_comprehensive_news_sentiment(ticker):
    """
    Backward compatibility wrapper.
    """
    result = analyze_comprehensive_news_sentiment_advanced(ticker)
    return result['sentiment_analysis'] if 'sentiment_analysis' in result else result

def analyze_news_sentiment(ticker):
    """
    Simple backward compatibility function.
    """
    return analyze_stock_specific_sentiment(ticker)

if __name__ == "__main__":
    # Test the optimized system
    print("🧪 Testing optimized news sentiment analysis...")
    result = analyze_comprehensive_news_sentiment_advanced("AAPL")
    
    if 'sentiment_analysis' in result:
        sentiment = result['sentiment_analysis']
        print(f"\n✅ Final sentiment: {sentiment['combined_sentiment_score']:.3f} ({sentiment['sentiment_label']})")
        
        comp = sentiment['component_analysis']
        general = comp['general_market']
        stock = comp['stock_specific']
        
        print(f"📊 General market: {general['average_sentiment']:.3f} ({general['article_count']} articles, {general['financial_articles']} financial)")
        print(f"📈 Stock-specific: {stock['average_sentiment']:.3f} ({stock['article_count']} articles, {stock['financial_articles']} financial)")
        print("\n🎉 Optimization test completed successfully!")
    else:
        print("❌ Test failed")
