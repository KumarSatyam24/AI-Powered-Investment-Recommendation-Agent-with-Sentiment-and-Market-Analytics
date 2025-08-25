from .sentiment_model import sentiment_analyzer
from src.data_processing.data_fetch import get_latest_headlines

def analyze_news_sentiment(ticker):
    """
    Fetches latest news headlines for the given ticker and returns sentiment scores.
    """
    headlines = get_latest_headlines(ticker)
    sentiments = []
    for headline in headlines:
        sentiment = sentiment_analyzer(headline)
        sentiments.append({
            "headline": headline,
            "sentiment": sentiment
        })
    return sentiments
#test code
if __name__ == "__main__":
    results = analyze_news_sentiment("AAPL")
    for item in results:
        print(item)