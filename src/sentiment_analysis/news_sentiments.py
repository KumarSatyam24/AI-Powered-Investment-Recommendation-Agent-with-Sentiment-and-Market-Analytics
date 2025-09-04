from .sentiment_model import sentiment_analyzer, general_sentiment_analyzer
from src.data_processing.data_fetch import get_latest_headlines
from src.api_clients.marketaux_api import marketaux_api
from newsapi import NewsApiClient
import sys
import os
import re
import json
import math
from datetime import datetime, timedelta
from transformers import pipeline
import sqlite3
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import NEWS_API_KEY

# Initialize FinBERT classifier for financial text classification
try:
    financial_classifier = pipeline(
        "text-classification",
        model="ProsusAI/finbert",
        tokenizer="ProsusAI/finbert",
        return_all_scores=True
    )
    print("✅ FinBERT financial classifier loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not load FinBERT classifier: {e}")
    financial_classifier = None

class UserFeedbackSystem:
    """
    System to handle user feedback and active learning for sentiment model improvement.
    """
    
    def __init__(self, db_path="user_feedback.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing user feedback."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for feedback storage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_text TEXT NOT NULL,
                headline TEXT NOT NULL,
                original_sentiment TEXT NOT NULL,
                original_score REAL NOT NULL,
                user_sentiment TEXT NOT NULL,
                user_score REAL NOT NULL,
                feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ticker TEXT,
                source TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classification_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_text TEXT NOT NULL,
                headline TEXT NOT NULL,
                original_classification TEXT NOT NULL,
                original_confidence REAL NOT NULL,
                user_classification TEXT NOT NULL,
                user_confidence REAL NOT NULL,
                feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_sentiment_feedback(self, article_text, headline, original_sentiment, 
                                original_score, user_sentiment, user_score, ticker=None, source=None):
        """Store user feedback for sentiment analysis."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sentiment_feedback 
            (article_text, headline, original_sentiment, original_score, 
             user_sentiment, user_score, ticker, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (article_text, headline, original_sentiment, original_score, 
              user_sentiment, user_score, ticker, source))
        
        conn.commit()
        conn.close()
        print("✅ Sentiment feedback stored successfully")
    
    def store_classification_feedback(self, article_text, headline, original_classification, 
                                    original_confidence, user_classification, user_confidence, source=None):
        """Store user feedback for financial classification."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO classification_feedback 
            (article_text, headline, original_classification, original_confidence, 
             user_classification, user_confidence, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (article_text, headline, original_classification, original_confidence, 
              user_classification, user_confidence, source))
        
        conn.commit()
        conn.close()
        print("✅ Classification feedback stored successfully")
    
    def get_feedback_stats(self):
        """Get statistics about user feedback."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM sentiment_feedback')
        sentiment_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM classification_feedback')
        classification_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'sentiment_feedback_count': sentiment_count,
            'classification_feedback_count': classification_count,
            'total_feedback': sentiment_count + classification_count
        }

# Initialize feedback system
feedback_system = UserFeedbackSystem()

def calculate_time_decay_weight(publish_date_str, decay_hours=24, min_weight=0.1):
    """
    Calculate time decay weight for news articles.
    More recent articles get higher weights.
    
    Args:
        publish_date_str (str): Publication date string
        decay_hours (int): Hours over which weight decays to min_weight
        min_weight (float): Minimum weight for very old articles
    
    Returns:
        float: Weight between min_weight and 1.0
    """
    try:
        # Try different date formats
        date_formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%a, %d %b %Y %H:%M:%S %Z"
        ]
        
        publish_date = None
        for fmt in date_formats:
            try:
                publish_date = datetime.strptime(publish_date_str, fmt)
                break
            except ValueError:
                continue
        
        if not publish_date:
            # If we can't parse date, assume recent
            return 1.0
        
        # Calculate hours since publication
        hours_diff = (datetime.now() - publish_date).total_seconds() / 3600
        
        # Exponential decay function
        # Weight = min_weight + (1 - min_weight) * exp(-hours_diff / decay_hours)
        weight = min_weight + (1 - min_weight) * math.exp(-hours_diff / decay_hours)
        
        return max(min_weight, min(1.0, weight))
        
    except Exception as e:
        print(f"⚠️ Error calculating time decay weight: {e}")
        return 1.0  # Default to full weight if error

def classify_financial_news_finbert(text, confidence_threshold=0.7):
    """
    Use FinBERT to classify if text is finance-related with high accuracy.
    
    Args:
        text (str): Text to classify
        confidence_threshold (float): Minimum confidence for financial classification
    
    Returns:
        dict: Classification result with confidence
    """
    if not financial_classifier:
        # Fallback to keyword-based classification
        return classify_financial_news_keywords(text)
    
    try:
        # FinBERT expects relatively short text, so truncate if necessary
        text_truncated = text[:512] if len(text) > 512 else text
        
        # Get classification
        result = financial_classifier(text_truncated)
        
        # FinBERT returns labels: 'positive', 'negative', 'neutral'
        # We need to determine if it's financial context
        
        # For financial classification, we'll use a different approach
        # Check if the text discusses financial concepts
        financial_keywords = [
            'stock', 'market', 'trading', 'investment', 'earnings', 'revenue',
            'profit', 'loss', 'dividend', 'share', 'portfolio', 'finance',
            'economy', 'economic', 'financial', 'banking', 'credit', 'debt',
            'inflation', 'recession', 'gdp', 'fed', 'interest rate', 'bond',
            'commodity', 'currency', 'forex', 'cryptocurrency', 'bitcoin'
        ]
        
        text_lower = text.lower()
        financial_score = sum(1 for keyword in financial_keywords if keyword in text_lower)
        total_words = len(text.split())
        
        # Calculate financial relevance
        financial_relevance = min(1.0, financial_score / max(1, total_words * 0.05))
        is_financial = financial_relevance > 0.3
        
        return {
            'is_financial': is_financial,
            'confidence': financial_relevance,
            'method': 'finbert_enhanced',
            'keyword_matches': financial_score
        }
        
    except Exception as e:
        print(f"⚠️ Error in FinBERT classification: {e}")
        return classify_financial_news_keywords(text)

def classify_financial_news_keywords(text):
    """
    Fallback keyword-based financial classification.
    """
    financial_keywords = [
        'stock', 'market', 'trading', 'investment', 'earnings', 'revenue',
        'profit', 'loss', 'dividend', 'share', 'portfolio', 'finance',
        'economy', 'economic', 'financial', 'banking', 'credit', 'debt',
        'inflation', 'recession', 'gdp', 'fed', 'interest rate', 'bond'
    ]
    
    text_lower = text.lower()
    matches = sum(1 for keyword in financial_keywords if keyword in text_lower)
    total_words = len(text.split())
    
    # Calculate confidence based on keyword density
    confidence = min(1.0, matches / max(1, total_words * 0.1))
    is_financial = matches >= 2 or confidence > 0.2
    
    return {
        'is_financial': is_financial,
        'confidence': confidence,
        'method': 'keyword_based',
        'keyword_matches': matches
    }

def get_general_market_news():
    """
    Fetch finance-related news that could impact stock prices and market conditions.
    Returns articles with both headlines and descriptions/summaries.
    """
    finance_keywords = [
        "tariffs", "trade war", "federal reserve", "interest rates", "inflation",
        "GDP growth", "unemployment rate", "stock market", "S&P 500", "Dow Jones",
        "NASDAQ", "market crash", "recession", "economic stimulus", "tax policy",
        "currency exchange", "oil prices", "gold prices", "bond yields",
        "earnings season", "market volatility", "geopolitical tensions",
        "supply chain", "energy crisis", "banking sector", "tech stocks"
    ]
    
    articles = []
    
    # Try NewsAPI for finance-specific market-moving news
    if NEWS_API_KEY and NEWS_API_KEY != "YOUR_NEWSAPI_KEY":
        try:
            newsapi = NewsApiClient(api_key=NEWS_API_KEY)
            # Search for high-impact financial news
            for keyword in finance_keywords[:15]:  # Limit to avoid rate limits
                news_response = newsapi.get_everything(
                    q=keyword,
                    language="en",
                    sort_by="relevancy",
                    page_size=3,
                    domains="reuters.com,bloomberg.com,cnbc.com,wsj.com,ft.com"  # Focus on financial sources
                )
                for article in news_response['articles']:
                    articles.append({
                        'headline': article.get('title', ''),
                        'summary': article.get('description', '') or article.get('content', '')[:200] + '...',
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'Unknown')
                    })
            
            # Also search for broader market terms
            market_terms = ["stock market crash", "market rally", "economic crisis", "trade tensions"]
            for term in market_terms[:2]:
                news_response = newsapi.get_everything(
                    q=term,
                    language="en",
                    sort_by="publishedAt",
                    page_size=2
                )
                for article in news_response['articles']:
                    articles.append({
                        'headline': article.get('title', ''),
                        'summary': article.get('description', '') or article.get('content', '')[:200] + '...',
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'Unknown')
                    })
        except Exception as e:
            print(f"NewsAPI error for finance news: {e}")
    
    # Fallback to MarketAux for general market news
    try:
        market_news = marketaux_api.get_trending_news(limit=10)
        for article_data in market_news.get('data', []):
            articles.append({
                'headline': article_data.get('title', ''),
                'summary': article_data.get('description', '') or article_data.get('snippet', ''),
                'url': article_data.get('url', ''),
                'source': article_data.get('source', 'MarketAux')
            })
    except Exception as e:
        print(f"MarketAux error for general news: {e}")
    
    # Remove duplicates based on headlines
    seen_headlines = set()
    unique_articles = []
    for article in articles:
        headline = article['headline']
        if headline and headline not in seen_headlines:
            seen_headlines.add(headline)
            unique_articles.append(article)
    
    return unique_articles[:15]  # Limit to 15 articles

def analyze_general_market_sentiment():
    """
    Analyze sentiment of general financial market news using both headlines and summaries.
    Apply weighted scoring based on financial vs non-financial classification.
    """
    print("🌍 Fetching General Market News...")
    articles = get_general_market_news()
    
    sentiments = []
    for article in articles:
        try:
            headline = article['headline']
            summary = article['summary']
            
            # Enhanced financial classification with FinBERT
            classification_result = classify_financial_news_finbert(f"{headline} {summary}")
            news_type = classification_result['is_financial']
            classification_confidence = classification_result['confidence']
            
            # Calculate time decay weight
            time_weight = calculate_time_decay_weight(article.get('publishedAt', ''))
            
            # Combine headline and summary for richer analysis
            combined_text = f"{headline}. {summary}" if summary else headline
            
            # Use both FinBERT and general sentiment analyzer
            finbert_sentiment = sentiment_analyzer(combined_text)[0] if sentiment_analyzer(combined_text) else None
            general_sentiment = general_sentiment_analyzer(combined_text)[0] if general_sentiment_analyzer(combined_text) else None
            
            # Also analyze headline separately for comparison
            headline_finbert = sentiment_analyzer(headline)[0] if headline and sentiment_analyzer(headline) else None
            headline_general = general_sentiment_analyzer(headline)[0] if headline and general_sentiment_analyzer(headline) else None
            
            sentiments.append({
                "headline": headline,
                "summary": summary,
                "source": article.get('source', 'Unknown'),
                "url": article.get('url', ''),
                "news_classification": {
                    "type": news_type,
                    "confidence": classification_confidence
                },
                "combined_analysis": {
                    "finbert_sentiment": finbert_sentiment,
                    "general_sentiment": general_sentiment
                },
                "headline_only": {
                    "finbert_sentiment": headline_finbert,
                    "general_sentiment": headline_general
                },
                "category": "general_market"
            })
        except Exception as e:
            print(f"Error analyzing article: {e}")
    
    return sentiments

def analyze_stock_specific_sentiment(ticker):
    """
    Analyze sentiment of news specific to a particular stock using headlines and summaries.
    Apply weighted scoring based on financial vs non-financial classification.
    """
    print(f"📈 Fetching {ticker}-Specific News...")
    
    # Get stock-specific headlines (enhanced with summaries if available)
    stock_articles = []
    
    # Get headlines from data_fetch (NewsAPI)
    headlines = get_latest_headlines(ticker)
    for headline in headlines:
        stock_articles.append({
            'headline': headline,
            'summary': '',  # Basic function doesn't return summaries
            'source': 'NewsAPI',
            'url': ''
        })
    
    # Also try MarketAux for stock-specific news with richer data
    try:
        stock_news = marketaux_api.get_news_by_symbol(ticker, limit=10)
        for article_data in stock_news.get('data', []):
            stock_articles.append({
                'headline': article_data.get('title', ''),
                'summary': article_data.get('description', '') or article_data.get('snippet', ''),
                'source': article_data.get('source', 'MarketAux'),
                'url': article_data.get('url', '')
            })
    except Exception as e:
        print(f"MarketAux error for {ticker}: {e}")
    
    # Remove duplicates
    seen_headlines = set()
    unique_articles = []
    for article in stock_articles:
        headline = article['headline']
        if headline and headline not in seen_headlines:
            seen_headlines.add(headline)
            unique_articles.append(article)
    
    sentiments = []
    for article in unique_articles:
        try:
            headline = article['headline']
            summary = article['summary']
            
            # Enhanced financial classification with FinBERT
            classification_result = classify_financial_news_finbert(f"{headline} {summary}")
            news_type = classification_result['is_financial']
            classification_confidence = classification_result['confidence']
            
            # Calculate time decay weight
            time_weight = calculate_time_decay_weight(article.get('publishedAt', ''))
            
            # Combine headline and summary for richer analysis
            combined_text = f"{headline}. {summary}" if summary else headline
            
            # Use both FinBERT and general sentiment analyzer
            finbert_sentiment = sentiment_analyzer(combined_text)[0] if sentiment_analyzer(combined_text) else None
            general_sentiment = general_sentiment_analyzer(combined_text)[0] if general_sentiment_analyzer(combined_text) else None
            
            # Also analyze headline separately for comparison
            headline_finbert = sentiment_analyzer(headline)[0] if headline and sentiment_analyzer(headline) else None
            headline_general = general_sentiment_analyzer(headline)[0] if headline and general_sentiment_analyzer(headline) else None
            
            sentiments.append({
                "headline": headline,
                "summary": summary,
                "source": article.get('source', 'Unknown'),
                "url": article.get('url', ''),
                "news_classification": {
                    "type": news_type,
                    "confidence": classification_confidence
                },
                "combined_analysis": {
                    "finbert_sentiment": finbert_sentiment,
                    "general_sentiment": general_sentiment
                },
                "headline_only": {
                    "finbert_sentiment": headline_finbert,
                    "general_sentiment": headline_general
                },
                "category": "stock_specific"
            })
        except Exception as e:
            print(f"Error analyzing article: {e}")
    
    return sentiments

def calculate_sentiment_score(sentiments):
    """
    Calculate overall sentiment score from sentiment analysis results.
    Uses adaptive weighting based on financial vs non-financial classification:
    - Financial news: FinBERT 80%, General 20%
    - Non-financial news: FinBERT 40%, General 60%
    """
    if not sentiments:
        return {"score": 0, "label": "neutral", "confidence": 0}
    
    weighted_scores = []
    financial_count = 0
    non_financial_count = 0
    
    for item in sentiments:
        # Get news classification
        classification = item.get('news_classification', {})
        news_type = classification.get('type', 'financial')  # Default to financial
        class_confidence = classification.get('confidence', 0.5)
        
        # Get sentiment scores from combined analysis (preferred) or headline-only
        combined = item.get('combined_analysis', {})
        headline_only = item.get('headline_only', {})
        
        # Extract FinBERT score
        finbert_score = 0
        if combined.get('finbert_sentiment'):
            fb = combined['finbert_sentiment']
            if fb['label'].lower() == 'positive':
                finbert_score = fb['score']
            elif fb['label'].lower() == 'negative':
                finbert_score = -fb['score']
        elif headline_only.get('finbert_sentiment'):
            fb = headline_only['finbert_sentiment']
            if fb['label'].lower() == 'positive':
                finbert_score = fb['score']
            elif fb['label'].lower() == 'negative':
                finbert_score = -fb['score']
        
        # Extract General sentiment score
        general_score = 0
        if combined.get('general_sentiment'):
            gs = combined['general_sentiment']
            if gs['label'].lower() == 'positive':
                general_score = gs['score']
            elif gs['label'].lower() == 'negative':
                general_score = -gs['score']
        elif headline_only.get('general_sentiment'):
            gs = headline_only['general_sentiment']
            if gs['label'].lower() == 'positive':
                general_score = gs['score']
            elif gs['label'].lower() == 'negative':
                general_score = -gs['score']
        
        # Apply adaptive weighting based on news type
        if news_type == 'financial':
            # Financial news: Trust FinBERT more (80% FinBERT, 20% General)
            weighted_score = 0.8 * finbert_score + 0.2 * general_score
            financial_count += 1
        else:
            # Non-financial news: Trust General sentiment more (40% FinBERT, 60% General)
            weighted_score = 0.4 * finbert_score + 0.6 * general_score
            non_financial_count += 1
        
        # Weight by classification confidence
        final_score = weighted_score * class_confidence
        weighted_scores.append({
            'score': final_score,
            'finbert': finbert_score,
            'general': general_score,
            'type': news_type,
            'confidence': class_confidence
        })
    
    # Calculate overall statistics
    overall_score = sum(item['score'] for item in weighted_scores) / len(weighted_scores)
    finbert_avg = sum(item['finbert'] for item in weighted_scores) / len(weighted_scores)
    general_avg = sum(item['general'] for item in weighted_scores) / len(weighted_scores)
    
    # Determine label and confidence
    if overall_score > 0.15:
        label = "positive"
        confidence = min(abs(overall_score), 1.0)
    elif overall_score < -0.15:
        label = "negative"
        confidence = min(abs(overall_score), 1.0)
    else:
        label = "neutral"
        confidence = 1 - abs(overall_score)
    
    return {
        "score": overall_score,
        "label": label,
        "confidence": min(confidence, 1.0),
        "finbert_avg": finbert_avg,
        "general_avg": general_avg,
        "financial_articles": financial_count,
        "non_financial_articles": non_financial_count,
        "total_articles": len(sentiments),
        "analysis_method": "adaptive_weighting"
    }

def analyze_comprehensive_news_sentiment(ticker):
    """
    Comprehensive news sentiment analysis with general market and stock-specific news.
    Uses adaptive weighting based on financial vs non-financial classification.
    """
    print(f"🔍 Comprehensive News Sentiment Analysis for {ticker}")
    print("=" * 60)
    
    # Analyze general market sentiment
    general_sentiments = analyze_general_market_sentiment()
    general_score = calculate_sentiment_score(general_sentiments)
    
    print(f"\n📊 General Market Sentiment:")
    print(f"   Overall: {general_score['label'].title()} (Score: {general_score['score']:.3f})")
    print(f"   Confidence: {general_score['confidence']:.3f}")
    print(f"   Articles analyzed: {general_score['total_articles']}")
    print(f"   Financial articles: {general_score['financial_articles']}")
    print(f"   Non-financial articles: {general_score['non_financial_articles']}")
    
    # Analyze stock-specific sentiment
    stock_sentiments = analyze_stock_specific_sentiment(ticker)
    stock_score = calculate_sentiment_score(stock_sentiments)
    
    print(f"\n📈 {ticker}-Specific Sentiment:")
    print(f"   Overall: {stock_score['label'].title()} (Score: {stock_score['score']:.3f})")
    print(f"   Confidence: {stock_score['confidence']:.3f}")
    print(f"   Articles analyzed: {stock_score['total_articles']}")
    print(f"   Financial articles: {stock_score['financial_articles']}")
    print(f"   Non-financial articles: {stock_score['non_financial_articles']}")
    
def calculate_weighted_combined_sentiment(general_score, stock_score, general_sentiments, stock_sentiments):
    """
    Calculate a sophisticated weighted combined sentiment score based on:
    - Article confidence levels
    - Financial vs non-financial classification
    - Recency and source reliability
    - Market vs stock-specific importance
    """
    
    # Base weights
    general_base_weight = 0.35  # Slightly reduced from 40%
    stock_base_weight = 0.65    # Slightly increased from 60%
    
    # Calculate confidence-adjusted weights
    general_confidence_avg = sum(
        item.get('news_classification', {}).get('confidence', 0.5) 
        for item in general_sentiments
    ) / max(len(general_sentiments), 1)
    
    stock_confidence_avg = sum(
        item.get('news_classification', {}).get('confidence', 0.5) 
        for item in stock_sentiments
    ) / max(len(stock_sentiments), 1)
    
    # Adjust weights based on confidence levels
    confidence_factor = 0.2  # How much confidence affects weighting
    general_adjusted_weight = general_base_weight * (1 + (general_confidence_avg - 0.5) * confidence_factor)
    stock_adjusted_weight = stock_base_weight * (1 + (stock_confidence_avg - 0.5) * confidence_factor)
    
    # Normalize weights to sum to 1
    total_weight = general_adjusted_weight + stock_adjusted_weight
    general_final_weight = general_adjusted_weight / total_weight
    stock_final_weight = stock_adjusted_weight / total_weight
    
    # Calculate financial article ratios
    general_financial_ratio = general_score.get('financial_articles', 0) / max(general_score.get('total_articles', 1), 1)
    stock_financial_ratio = stock_score.get('financial_articles', 0) / max(stock_score.get('total_articles', 1), 1)
    
    # Apply additional weighting based on financial content ratio
    # More financial content = more reliable for investment decisions
    financial_boost = 0.1
    if general_financial_ratio > 0.7:  # If >70% financial content
        general_final_weight *= (1 + financial_boost)
    if stock_financial_ratio > 0.7:
        stock_final_weight *= (1 + financial_boost)
    
    # Re-normalize after financial boost
    total_weight = general_final_weight + stock_final_weight
    general_final_weight /= total_weight
    stock_final_weight /= total_weight
    
    # Calculate weighted combined score
    weighted_score = (general_final_weight * general_score['score']) + (stock_final_weight * stock_score['score'])
    
    # Calculate combined confidence
    weighted_confidence = (general_final_weight * general_score['confidence']) + (stock_final_weight * stock_score['confidence'])
    
    # Determine final label with adjusted thresholds
    if weighted_score > 0.12:
        final_label = "positive"
    elif weighted_score < -0.12:
        final_label = "negative"
    else:
        final_label = "neutral"
    
    return {
        "weighted_score": weighted_score,
        "label": final_label,
        "confidence": weighted_confidence,
        "weights_used": {
            "general_market": general_final_weight,
            "stock_specific": stock_final_weight,
            "general_confidence": general_confidence_avg,
            "stock_confidence": stock_confidence_avg,
            "general_financial_ratio": general_financial_ratio,
            "stock_financial_ratio": stock_financial_ratio
        },
        "methodology": "confidence_and_financial_weighted"
    }

def analyze_comprehensive_news_sentiment(ticker):
    """
    Comprehensive news sentiment analysis with general market and stock-specific news.
    Uses adaptive weighting based on financial vs non-financial classification.
    """
    print(f"🔍 Comprehensive News Sentiment Analysis for {ticker}")
    print("=" * 60)
    
    # Analyze general market sentiment
    general_sentiments = analyze_general_market_sentiment()
    general_score = calculate_sentiment_score(general_sentiments)
    
    print(f"\n📊 General Market Sentiment:")
    print(f"   Overall: {general_score['label'].title()} (Score: {general_score['score']:.3f})")
    print(f"   Confidence: {general_score['confidence']:.3f}")
    print(f"   Articles analyzed: {general_score['total_articles']}")
    print(f"   Financial articles: {general_score['financial_articles']}")
    print(f"   Non-financial articles: {general_score['non_financial_articles']}")
    
    # Analyze stock-specific sentiment
    stock_sentiments = analyze_stock_specific_sentiment(ticker)
    stock_score = calculate_sentiment_score(stock_sentiments)
    
    print(f"\n📈 {ticker}-Specific Sentiment:")
    print(f"   Overall: {stock_score['label'].title()} (Score: {stock_score['score']:.3f})")
    print(f"   Confidence: {stock_score['confidence']:.3f}")
    print(f"   Articles analyzed: {stock_score['total_articles']}")
    print(f"   Financial articles: {stock_score['financial_articles']}")
    print(f"   Non-financial articles: {stock_score['non_financial_articles']}")
    
    # Calculate sophisticated weighted combined analysis
    weighted_combined = calculate_weighted_combined_sentiment(
        general_score, stock_score, general_sentiments, stock_sentiments
    )
    
    print(f"\n🎯 Weighted Combined Sentiment Analysis:")
    print(f"   Overall: {weighted_combined['label'].title()} (Score: {weighted_combined['weighted_score']:.3f})")
    print(f"   Confidence: {weighted_combined['confidence']:.3f}")
    print(f"   Methodology: {weighted_combined['methodology']}")
    print(f"\n📊 Dynamic Weights Applied:")
    weights = weighted_combined['weights_used']
    print(f"   General Market: {weights['general_market']:.1%} (confidence: {weights['general_confidence']:.3f})")
    print(f"   Stock-Specific: {weights['stock_specific']:.1%} (confidence: {weights['stock_confidence']:.3f})")
    print(f"   Financial Content Ratios: General {weights['general_financial_ratio']:.1%}, Stock {weights['stock_financial_ratio']:.1%}")
    
    # Also show simple combined for comparison
    simple_combined_score = 0.4 * general_score['score'] + 0.6 * stock_score['score']
    if simple_combined_score > 0.15:
        simple_label = "positive"
    elif simple_combined_score < -0.15:
        simple_label = "negative"
    else:
        simple_label = "neutral"
        
    print(f"\n📈 Comparison with Simple Average:")
    print(f"   Simple Combined: {simple_label.title()} (Score: {simple_combined_score:.3f})")
    print(f"   Weighted Combined: {weighted_combined['label'].title()} (Score: {weighted_combined['weighted_score']:.3f})")
    print(f"   Difference: {abs(weighted_combined['weighted_score'] - simple_combined_score):.3f}")
    
    return {
        "general_market": {
            "sentiments": general_sentiments,
            "score": general_score
        },
        "stock_specific": {
            "sentiments": stock_sentiments,
            "score": stock_score
        },
        "simple_combined": {
            "score": simple_combined_score,
            "label": simple_label,
            "confidence": (general_score['confidence'] + stock_score['confidence']) / 2
        },
        "weighted_combined": weighted_combined
    }

def analyze_news_sentiment(ticker):
    """
    Original function for backward compatibility.
    """
    return analyze_stock_specific_sentiment(ticker)

#test code
if __name__ == "__main__":
    # Test comprehensive analysis
    try:
        results = analyze_comprehensive_news_sentiment("TSLA")
        
        if results:
            print("\n" + "="*60)
            print("📰 DETAILED HEADLINES ANALYSIS")
            print("="*60)
            
            # Check if results have the expected structure
            if 'general_market' in results and results['general_market']['sentiments']:
                print("\n🌍 GENERAL MARKET NEWS:")
                for i, item in enumerate(results['general_market']['sentiments'][:5], 1):
                    combined = item.get('combined_analysis', {})
                    headline_only = item.get('headline_only', {})
                    classification = item.get('news_classification', {})
                    fb_combined = combined.get('finbert_sentiment', {})
                    gs_combined = combined.get('general_sentiment', {})
                    fb_headline = headline_only.get('finbert_sentiment', {})
                    
                    print(f"\n{i}. {item['headline'][:80]}...")
                    if item.get('summary'):
                        print(f"   Summary: {item['summary'][:100]}...")
                    print(f"   Source: {item.get('source', 'Unknown')}")
                    print(f"   Classification: {str(classification.get('type', classification.get('is_financial', False))).replace('True', 'Financial').replace('False', 'Non-Financial').replace('financial', 'Financial').replace('true', 'Financial').replace('false', 'Non-Financial').title()} ({classification.get('confidence', 0):.2f} confidence)")
                    
                    # Show weighting applied
                    if str(classification.get('type', classification.get('is_financial', False))).lower() in ['financial', 'true']:
                        print(f"   Weighting: FinBERT 80%, General 20% (Financial news)")
                    else:
                        print(f"   Weighting: FinBERT 40%, General 60% (Non-financial news)")
                        
                    print(f"   Combined Analysis - FinBERT: {fb_combined.get('label', 'N/A').title()} ({fb_combined.get('score', 0):.3f})")
                    print(f"                    - General: {gs_combined.get('label', 'N/A').title()} ({gs_combined.get('score', 0):.3f})")
            
            if 'stock_specific' in results and results['stock_specific']['sentiments']:
                print("\n📈 STOCK-SPECIFIC NEWS:")
                for i, item in enumerate(results['stock_specific']['sentiments'][:5], 1):
                    combined = item.get('combined_analysis', {})
                    headline_only = item.get('headline_only', {})
                    classification = item.get('news_classification', {})
                    fb_combined = combined.get('finbert_sentiment', {})
                    gs_combined = combined.get('general_sentiment', {})
                    fb_headline = headline_only.get('finbert_sentiment', {})
                    
                    print(f"\n{i}. {item['headline'][:80]}...")
                    if item.get('summary'):
                        print(f"   Summary: {item['summary'][:100]}...")
                    print(f"   Source: {item.get('source', 'Unknown')}")
                    print(f"   Classification: {str(classification.get('type', classification.get('is_financial', False))).replace('True', 'Financial').replace('False', 'Non-Financial').replace('financial', 'Financial').replace('true', 'Financial').replace('false', 'Non-Financial').title()} ({classification.get('confidence', 0):.2f} confidence)")
                    
                    # Show weighting applied
                    if str(classification.get('type', classification.get('is_financial', False))).lower() in ['financial', 'true']:
                        print(f"   Weighting: FinBERT 80%, General 20% (Financial news)")
                    else:
                        print(f"   Weighting: FinBERT 40%, General 60% (Non-financial news)")
                        
                    print(f"   Combined Analysis - FinBERT: {fb_combined.get('label', 'N/A').title()} ({fb_combined.get('score', 0):.3f})")
                    print(f"                    - General: {gs_combined.get('label', 'N/A').title()} ({gs_combined.get('score', 0):.3f})")
        else:
            print("No results returned from analysis")
            
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

def apply_manual_override(article_data, user_sentiment=None, user_score=None, 
                         user_classification=None, save_feedback=True):
    """
    Apply manual overrides to sentiment analysis results and store for active learning.
    
    Args:
        article_data (dict): Original article analysis data
        user_sentiment (str): User-provided sentiment label
        user_score (float): User-provided sentiment score
        user_classification (str): User-provided financial classification
        save_feedback (bool): Whether to save feedback for active learning
    
    Returns:
        dict: Updated article data with user overrides
    """
    updated_data = article_data.copy()
    
    # Store original values for feedback
    original_sentiment = article_data.get('sentiment', 'unknown')
    original_score = article_data.get('score', 0.0)
    original_classification = article_data.get('is_financial', False)
    
    # Apply user overrides
    if user_sentiment is not None:
        updated_data['sentiment'] = user_sentiment
        updated_data['user_override_sentiment'] = True
    
    if user_score is not None:
        updated_data['score'] = user_score
        updated_data['weighted_score'] = user_score * article_data.get('time_weight', 1.0)
        updated_data['user_override_score'] = True
    
    if user_classification is not None:
        updated_data['is_financial'] = user_classification
        updated_data['user_override_classification'] = True
    
    # Save feedback for active learning
    if save_feedback:
        try:
            # Save sentiment feedback if provided
            if user_sentiment is not None or user_score is not None:
                feedback_system.store_sentiment_feedback(
                    article_text=article_data.get('summary', ''),
                    headline=article_data.get('headline', ''),
                    original_sentiment=original_sentiment,
                    original_score=original_score,
                    user_sentiment=user_sentiment or original_sentiment,
                    user_score=user_score or original_score,
                    source=article_data.get('source', 'unknown')
                )
            
            # Save classification feedback if provided
            if user_classification is not None:
                feedback_system.store_classification_feedback(
                    article_text=article_data.get('summary', ''),
                    headline=article_data.get('headline', ''),
                    original_classification='financial' if original_classification else 'non-financial',
                    original_confidence=article_data.get('classification_confidence', 0.5),
                    user_classification='financial' if user_classification else 'non-financial',
                    user_confidence=1.0,  # User feedback assumed to have high confidence
                    source=article_data.get('source', 'unknown')
                )
        except Exception as e:
            print(f"⚠️ Warning: Could not save feedback: {e}")
    
    return updated_data

def get_feedback_insights():
    """
    Get insights from accumulated user feedback for model improvement.
    
    Returns:
        dict: Insights and recommendations based on user feedback
    """
    stats = feedback_system.get_feedback_stats()
    
    if stats['total_feedback'] == 0:
        return {
            'status': 'no_feedback',
            'message': 'No user feedback available yet',
            'recommendations': ['Collect more user feedback to improve model accuracy']
        }
    
    # Analyze feedback patterns
    conn = sqlite3.connect(feedback_system.db_path)
    cursor = conn.cursor()
    
    insights = {
        'total_feedback_count': stats['total_feedback'],
        'sentiment_feedback_count': stats['sentiment_feedback_count'],
        'classification_feedback_count': stats['classification_feedback_count']
    }
    
    # Analyze sentiment corrections
    if stats['sentiment_feedback_count'] > 0:
        cursor.execute('''
            SELECT original_sentiment, user_sentiment, COUNT(*) as count
            FROM sentiment_feedback 
            GROUP BY original_sentiment, user_sentiment
        ''')
        sentiment_corrections = cursor.fetchall()
        insights['sentiment_correction_patterns'] = [
            {'original': orig, 'user_correction': user, 'count': count}
            for orig, user, count in sentiment_corrections
        ]
    
    # Analyze classification corrections
    if stats['classification_feedback_count'] > 0:
        cursor.execute('''
            SELECT original_classification, user_classification, COUNT(*) as count
            FROM classification_feedback 
            GROUP BY original_classification, user_classification
        ''')
        classification_corrections = cursor.fetchall()
        insights['classification_correction_patterns'] = [
            {'original': orig, 'user_correction': user, 'count': count}
            for orig, user, count in classification_corrections
        ]
    
    conn.close()
    
    # Generate recommendations
    recommendations = []
    if stats['sentiment_feedback_count'] > 10:
        recommendations.append("Consider retraining sentiment model with user feedback")
    if stats['classification_feedback_count'] > 5:
        recommendations.append("Consider updating financial classification keywords")
    
    insights['recommendations'] = recommendations
    return insights

def analyze_comprehensive_news_sentiment_advanced(ticker_symbol):
    """
    Enhanced version of comprehensive news sentiment analysis with all advanced features:
    - FinBERT-based financial classification
    - Time decay weighting
    - User feedback integration
    - Active learning capabilities
    
    Args:
        ticker_symbol (str): Stock ticker symbol
    
    Returns:
        dict: Comprehensive sentiment analysis with advanced features
    """
    print(f"\n🚀 Advanced News Sentiment Analysis for {ticker_symbol}")
    print("=" * 60)
    
    try:
        # Get general market and stock-specific news
        print("\n📈 Fetching general market news...")
        general_articles = get_general_market_news()  # Remove limit parameter
        
        print(f"📊 Fetching {ticker_symbol}-specific news...")
        stock_articles = get_latest_headlines(ticker_symbol)  # Remove limit parameter
        
        # Analyze with advanced features
        print("\n🔬 Analyzing with advanced features:")
        print("   ✓ FinBERT financial classification")
        print("   ✓ Time decay weighting")
        print("   ✓ User feedback integration")
        
        # Use existing analysis functions (they fetch their own data)
        general_sentiments = analyze_general_market_sentiment()
        stock_sentiments = analyze_stock_specific_sentiment(ticker_symbol)
        
        # Calculate weighted sentiment with time decay integration
        try:
            # Apply time decay weighting to individual articles first
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
            
            # Calculate time-weighted averages
            general_weighted_avg = sum(item.get('weighted_score', 0) for item in general_sentiments) / max(len(general_sentiments), 1)
            stock_weighted_avg = sum(item.get('weighted_score', 0) for item in stock_sentiments) / max(len(stock_sentiments), 1)
            
            # Calculate average time weights for metadata
            general_avg_time_weight = sum(item.get('time_weight', 1.0) for item in general_sentiments) / max(len(general_sentiments), 1)
            stock_avg_time_weight = sum(item.get('time_weight', 1.0) for item in stock_sentiments) / max(len(stock_sentiments), 1)
            
            # Create enhanced combined result with time decay
            final_sentiment = (general_weighted_avg * 0.4) + (stock_weighted_avg * 0.6)
            
            combined_result = {
                'combined_sentiment_score': round(final_sentiment, 3),
                'sentiment_label': 'Positive' if final_sentiment > 0.1 else 'Negative' if final_sentiment < -0.1 else 'Neutral',
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
            }
            
        except Exception as e:
            print(f"⚠️ Error in time decay calculation: {e}")
            # Fallback to simpler calculation
            general_score = sum(item.get('score', 0) for item in general_sentiments) / max(len(general_sentiments), 1)
            stock_score = sum(item.get('score', 0) for item in stock_sentiments) / max(len(stock_sentiments), 1)
            
            combined_result = {
                'combined_sentiment_score': (general_score * 0.4) + (stock_score * 0.6),
                'sentiment_label': 'Positive' if ((general_score * 0.4) + (stock_score * 0.6)) > 0.1 else 'Negative' if ((general_score * 0.4) + (stock_score * 0.6)) < -0.1 else 'Neutral',
                'weights': {'general_market_weight': 0.4, 'stock_specific_weight': 0.6},
                'component_analysis': {
                    'general_market': {'average_sentiment': general_score, 'article_count': len(general_sentiments), 'financial_articles': 0, 'financial_ratio': 0, 'avg_time_weight': 1.0},
                    'stock_specific': {'average_sentiment': stock_score, 'article_count': len(stock_sentiments), 'financial_articles': 0, 'financial_ratio': 0, 'avg_time_weight': 1.0}
                },
                'metadata': {'time_decay_applied': False, 'analysis_timestamp': datetime.now().isoformat()}
            }
        
        # Get feedback insights
        feedback_insights = get_feedback_insights()
        
        # Enhanced result structure
        result = {
            'ticker': ticker_symbol,
            'analysis_type': 'advanced_comprehensive',
            'sentiment_analysis': combined_result,
            'detailed_breakdown': {
                'general_market_articles': general_sentiments,
                'stock_specific_articles': stock_sentiments
            },
            'advanced_features': {
                'finbert_classification': True,
                'time_decay_weighting': True,
                'user_feedback_enabled': True,
                'active_learning': True
            },
            'user_feedback_insights': feedback_insights,
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_articles': len(general_articles) + len(stock_articles),
                'features_enabled': ['FinBERT', 'TimeDecay', 'UserFeedback', 'ActiveLearning']
            }
        }
        
        # Display results
        print(f"\n📊 Advanced Analysis Results for {ticker_symbol}")
        print("=" * 50)
        
        sentiment_data = combined_result
        print(f"🎯 Combined Sentiment: {sentiment_data['sentiment_label']} ({sentiment_data['combined_sentiment_score']})")
        print(f"⚖️  Dynamic Weights:")
        print(f"   • General Market: {sentiment_data['weights']['general_market_weight']:.1%}")
        print(f"   • Stock-Specific: {sentiment_data['weights']['stock_specific_weight']:.1%}")
        
        if sentiment_data['metadata'].get('time_decay_applied'):
            print(f"⏰ Time Decay Applied: ✓")
            print(f"   • General Avg Time Weight: {sentiment_data['component_analysis']['general_market'].get('avg_time_weight', 0):.2f}")
            print(f"   • Stock Avg Time Weight: {sentiment_data['component_analysis']['stock_specific'].get('avg_time_weight', 0):.2f}")
        
        print(f"\n📈 Component Analysis:")
        general = sentiment_data['component_analysis']['general_market']
        stock = sentiment_data['component_analysis']['stock_specific']
        
        print(f"   🌐 General Market: {general['average_sentiment']:.3f} ({general['article_count']} articles)")
        print(f"      └─ Financial Articles: {general['financial_articles']} ({general['financial_ratio']:.1%})")
        
        print(f"   📊 Stock-Specific: {stock['average_sentiment']:.3f} ({stock['article_count']} articles)")
        print(f"      └─ Financial Articles: {stock['financial_articles']} ({stock['financial_ratio']:.1%})")
        
        print(f"\n🤖 User Feedback Status:")
        print(f"   • Total Feedback: {feedback_insights.get('total_feedback_count', 0)}")
        print(f"   • Sentiment Feedback: {feedback_insights.get('sentiment_feedback_count', 0)}")
        print(f"   • Classification Feedback: {feedback_insights.get('classification_feedback_count', 0)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in advanced sentiment analysis: {e}")
        return {
            'error': str(e),
            'ticker': ticker_symbol,
            'analysis_type': 'advanced_comprehensive',
            'status': 'failed'
        }

# Test the advanced features
if __name__ == "__main__":
    print("🧠 Advanced AI-Powered News Sentiment Analysis")
    print("Features: FinBERT Classification | Time Decay | User Feedback | Active Learning")
    print("=" * 80)
    
    # Test advanced analysis
    result = analyze_comprehensive_news_sentiment_advanced("AAPL")
    
    if 'error' not in result:
        print(f"\n✅ Advanced analysis completed successfully!")
        print(f"💡 Usage Examples:")
        print(f"   • apply_manual_override(article_data, user_sentiment='positive', user_score=0.8)")
        print(f"   • get_feedback_insights() - Check model improvement recommendations")
        print(f"   • Time decay automatically applied to recent vs older news")
    else:
        print(f"❌ Analysis failed: {result['error']}")