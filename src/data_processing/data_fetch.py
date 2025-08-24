import yfinance as yf
from newsapi import NewsApiClient
import praw
import tweepy
import sys
import os

# Add paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import NEWS_API_KEY, TWITTER_BEARER_TOKEN, REDDIT_CLIENT_ID, REDDIT_SECRET, REDDIT_USER_AGENT

# Import new API modules
from src.api_clients.alpha_vantage_api import alpha_vantage
from src.api_clients.fred_api import fred_api
from src.api_clients.marketaux_api import marketaux_api

def get_stock_data(ticker):
    """Get stock data - enhanced with Alpha Vantage fallback."""
    try:
        # Try yfinance first (free but rate limited)
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        info = stock.info
        
        if data.empty:
            # Fallback to Alpha Vantage
            av_quote = alpha_vantage.get_stock_quote(ticker)
            av_overview = alpha_vantage.get_company_overview(ticker)
            
            return {
                "price": av_quote.get('price', 0),
                "pe_ratio": av_overview.get('pe_ratio', 'N/A'),
                "eps": av_overview.get('eps', 'N/A'),
                "volume": av_quote.get('volume', 0),
                "change": av_quote.get('change', 0),
                "change_percent": av_quote.get('change_percent', '0%'),
                "data_source": "Alpha Vantage"
            }
        else:
            return {
                "price": round(data['Close'].iloc[-1], 2),
                "pe_ratio": info.get("trailingPE"),
                "eps": info.get("trailingEps"),
                "volume": int(data['Volume'].iloc[-1]),
                "change": round(data['Close'].iloc[-1] - data['Open'].iloc[-1], 2),
                "change_percent": f"{((data['Close'].iloc[-1] - data['Open'].iloc[-1]) / data['Open'].iloc[-1] * 100):.2f}%",
                "data_source": "yfinance"
            }
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        # Final fallback to Alpha Vantage
        av_quote = alpha_vantage.get_stock_quote(ticker)
        av_overview = alpha_vantage.get_company_overview(ticker)
        
        return {
            "price": av_quote.get('price', 0),
            "pe_ratio": av_overview.get('pe_ratio', 'N/A'),
            "eps": av_overview.get('eps', 'N/A'),
            "volume": av_quote.get('volume', 0),
            "change": av_quote.get('change', 0),
            "change_percent": av_quote.get('change_percent', '0%'),
            "data_source": "Alpha Vantage (fallback)"
        }

def get_enhanced_stock_data(ticker):
    """Get comprehensive stock data using Alpha Vantage."""
    basic_data = get_stock_data(ticker)
    company_overview = alpha_vantage.get_company_overview(ticker)
    
    # Get technical indicators
    sma_data = alpha_vantage.get_technical_indicators(ticker, 'SMA', 20)
    rsi_data = alpha_vantage.get_technical_indicators(ticker, 'RSI', 14)
    
    return {
        **basic_data,
        'company_overview': company_overview,
        'technical_indicators': {
            'sma_20': sma_data,
            'rsi_14': rsi_data
        }
    }

def get_market_conditions():
    """Get comprehensive market conditions using FRED economic data."""
    market_summary = fred_api.get_market_indicators_summary()
    
    return {
        'economic_indicators': market_summary['summary'],
        'market_condition': market_summary['market_condition'],
        'detailed_data': {
            'vix': market_summary['summary'].get('vix', {}).get('value', 'N/A'),
            'unemployment': market_summary['summary'].get('unemployment', {}).get('value', 'N/A'),
            'inflation': market_summary['summary'].get('inflation', {}).get('value', 'N/A'),
            'fed_funds_rate': market_summary['summary'].get('fed_funds_rate', {}).get('value', 'N/A'),
            'treasury_10y': market_summary['summary'].get('treasury_10y', {}).get('value', 'N/A'),
            'consumer_sentiment': market_summary['summary'].get('consumer_sentiment', {}).get('value', 'N/A')
        }
    }

def get_latest_headlines(query):
    """Get latest headlines - enhanced with MarketAux fallback."""
    # Try NewsAPI first
    if NEWS_API_KEY and NEWS_API_KEY != "YOUR_NEWSAPI_KEY":
        try:
            newsapi = NewsApiClient(api_key=NEWS_API_KEY)
            articles = newsapi.get_everything(q=query, language="en", page_size=5)
            headlines = [a['title'] for a in articles['articles']]
            if headlines:
                return headlines
        except Exception as e:
            print(f"NewsAPI error: {e}")
    
    # Fallback to MarketAux
    try:
        if query.upper() in ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN']:  # If it's a stock symbol
            news_data = marketaux_api.get_news_by_symbol(query.upper(), limit=5)
        else:
            news_data = marketaux_api.get_trending_news(limit=5)
        
        headlines = [article['title'] for article in news_data.get('data', [])]
        if headlines:
            return headlines
    except Exception as e:
        print(f"MarketAux error: {e}")
    
    # Final fallback to sample data
    return [
        "Sample positive news about the market.",
        "Market outlook improves as investors gain confidence.",
        "Tech stocks rally amid strong earnings.",
        "Some negative sentiment arises due to inflation fears."
    ]

def get_enhanced_news_sentiment(symbol):
    """Get comprehensive news sentiment analysis."""
    try:
        # Get sentiment analysis from MarketAux
        sentiment_data = marketaux_api.get_news_sentiment_analysis([symbol], days=7)
        
        # Also get basic headlines
        headlines = get_latest_headlines(symbol)
        
        return {
            'headlines': headlines,
            'sentiment_analysis': sentiment_data,
            'overall_sentiment': sentiment_data.get('overall_sentiment', 'neutral'),
            'sentiment_distribution': sentiment_data.get('sentiment_distribution', {}),
            'total_articles': sentiment_data.get('total_articles', 0)
        }
    except Exception as e:
        print(f"Error getting enhanced news sentiment: {e}")
        return {
            'headlines': get_latest_headlines(symbol),
            'sentiment_analysis': {},
            'overall_sentiment': 'neutral',
            'sentiment_distribution': {'positive': 33.3, 'negative': 33.3, 'neutral': 33.3},
            'total_articles': 0
        }





reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# Function to fetch Reddit posts related to a stock ticker, including top comments
def get_reddit_posts(ticker, limit=10):
    """
    Fetches recent Reddit post titles and top-level comments related to a given stock ticker
    from popular finance subreddits.
    """
    posts = []
    try:
        for submission in reddit.subreddit("stocks+investing+wallstreetbets").search(ticker, limit=limit, sort="new"):
            if submission.stickied:
                continue
            if submission.score < 10:
                continue
            submission.comments.replace_more(limit=0)
            top_comments = [comment.body for comment in submission.comments[:3]]
            posts.append({
                "title": submission.title,
                "comments": top_comments
            })
    except Exception as e:
        print(f"Error fetching Reddit posts: {e}")
    return posts


twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
def get_tweets(query, limit=10):
    """
    Fetches recent tweets containing the given query.
    Returns a list of dictionaries with text, created_at, like_count, and retweet_count.
    """
    tweets = []
    try:
        response = twitter_client.search_recent_tweets(
            query=query + " -is:retweet lang:en",  # remove retweets, English only
            max_results=min(limit, 100),           # Twitter API allows up to 100
            tweet_fields=["created_at", "public_metrics"]
        )
        
        if response.data:
            for t in response.data:
                tweets.append({
                    "text": t.text,
                    "created_at": str(t.created_at),
                    "like_count": t.public_metrics.get("like_count", 0),
                    "retweet_count": t.public_metrics.get("retweet_count", 0),
                })
    except Exception as e:
        print(f"Error fetching tweets: {e}")
    
    return tweets