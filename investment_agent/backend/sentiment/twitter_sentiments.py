from backend.sentiment.sentiment_model import sentiment_analyzer
from backend.data_fetch import get_tweets

def analyze_twitter_sentiment(ticker):
    """
    Fetches recent tweets for the given ticker and returns sentiment scores.
    """
    tweets = get_tweets(ticker)
    sentiments = []
    for tweet in tweets:
        sentiment = sentiment_analyzer(tweet)
        sentiments.append({
            "tweet": tweet,
            "sentiment": sentiment
        })
    return sentiments