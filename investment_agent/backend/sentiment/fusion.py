from backend.sentiment.sentiment_model import analyze_sentiment

def fuse_sentiments(news_headlines, reddit_posts, twitter_posts):
    news_sentiment = analyze_sentiment(news_headlines)
    reddit_sentiment = analyze_sentiment(reddit_posts)
    twitter_sentiment = analyze_sentiment(twitter_posts)

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