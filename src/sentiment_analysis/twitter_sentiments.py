from langdetect import detect
import emoji
from .sentiment_model import sentiment_analyzer, general_sentiment_analyzer
from src.data_processing.data_fetch import get_tweets
import re

# Contractions dictionary for expansion
CONTRACTIONS = {
    "don't": "do not",
    "can't": "cannot",
    "won't": "will not",
    "i'm": "i am",
    "it's": "it is",
    "you're": "you are",
    "they're": "they are",
    "we're": "we are",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "didn't": "did not",
    "hasn't": "has not",
    "haven't": "have not",
    "couldn't": "could not",
    "shouldn't": "should not",
    "wouldn't": "would not",
    "there's": "there is",
    "let's": "let us",
    "that's": "that is"
}

INFLUENTIAL_PEOPLE = [
    "elonmusk",
    "tim_cook",
    "sundarpichai",
    "satyanadella",
    "marybarra",
    "warrenbuffett",
    "jeffbezos",
    "billgates",
    "larrypage",
    "sergeybrin"
]


# Helper function: Map emojis to words
def map_emojis_to_words(text):
    # emoji.demojize replaces emojis with :word:; we convert to space+word+space
    text = emoji.demojize(text, delimiters=(" ", " "))
    # Remove colons and underscores, and collapse multiple spaces
    text = re.sub(r':', '', text)
    text = re.sub(r'_', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

# Helper function: Expand contractions using CONTRACTIONS dict
def expand_contractions(text):
    def replace(match):
        return CONTRACTIONS[match.group(0)]
    # Build regex pattern from keys
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in CONTRACTIONS.keys()) + r')\b')
    return pattern.sub(replace, text)

def preprocess_tweet(tweet):
    # Map emojis to words first
    tweet = map_emojis_to_words(tweet)
    tweet = tweet.lower()
    # Expand contractions
    tweet = expand_contractions(tweet)
    # Detect language; skip if not English
    try:
        lang = detect(tweet)
        if lang != "en":
            return ""
    except Exception:
        return ""
    tweet = re.sub(r'http\S+|www\S+', '', tweet)
    tweet = re.sub(r'[@#]\w+', '', tweet)
    tweet = re.sub(r'[^a-z\s]', '', tweet)
    tweet = re.sub(r'\s+', ' ', tweet).strip()
    tokens = tweet.split()
    return ' '.join(tokens)


def analyze_twitter_sentiment(ticker, use_general=False):
    """
    Fetches recent tweets for the given ticker and from influential people, then returns sentiment scores.
    If use_general is True, uses general_sentiment_analyzer (DistilBERT); otherwise uses sentiment_analyzer (FinBERT).
    """
    tweets = []
    # Fetch tweets for ticker
    for t in get_tweets(ticker):
        # Assume get_tweets returns a list of tweet objects or strings
        # If string, wrap in dict with text field only, else fetch metadata
        if isinstance(t, dict):
            tweet_dict = {
                "text": t.get("text", ""),
                "created_at": t.get("created_at", None),
                "likes": t.get("like_count", 0),
                "retweets": t.get("retweet_count", 0)
            }
        else:
            tweet_dict = {
                "text": t,
                "created_at": None,
                "likes": 0,
                "retweets": 0
            }
        tweets.append(tweet_dict)
    # Fetch tweets from influential people
    for person in INFLUENTIAL_PEOPLE:
        for t in get_tweets(person):
            if isinstance(t, dict):
                tweet_dict = {
                    "text": t.get("text", ""),
                    "created_at": t.get("created_at", None),
                    "likes": t.get("like_count", 0),
                    "retweets": t.get("retweet_count", 0)
                }
            else:
                tweet_dict = {
                    "text": t,
                    "created_at": None,
                    "likes": 0,
                    "retweets": 0
                }
            tweets.append(tweet_dict)
    # Remove duplicates by text
    seen_texts = set()
    unique_tweets = []
    for tweet in tweets:
        text = tweet.get("text", "")
        if text not in seen_texts:
            seen_texts.add(text)
            unique_tweets.append(tweet)
    sentiments = []
    for tweet in unique_tweets:
        original_text = tweet.get("text", "")
        cleaned_tweet = preprocess_tweet(original_text)
        if not cleaned_tweet:
            continue
        if use_general:
            sentiment = general_sentiment_analyzer(cleaned_tweet)
        else:
            sentiment = sentiment_analyzer(cleaned_tweet)
        sentiments.append({
            "tweet": cleaned_tweet,
            "sentiment": sentiment,
            "created_at": tweet.get("created_at"),
            "likes": tweet.get("likes"),
            "retweets": tweet.get("retweets")
        })
    return sentiments

if __name__ == "__main__":
    print("Using general_sentiment_analyzer (DistilBERT):")
    results_general = analyze_twitter_sentiment("MSFT", use_general=True)
    for idx, res in enumerate(results_general, 1):
        print(f"Tweet {idx}:")
        print(f"  Text: {res['tweet']}")
        print(f"  Sentiment: {res['sentiment']}")
        print(f"  Date: {res['created_at']}")
        print(f"  Likes: {res['likes']}")
        print(f"  Retweets: {res['retweets']}")
        print()
    print("Using sentiment_analyzer (FinBERT):")
    results_finbert = analyze_twitter_sentiment("MSFT", use_general=False)
    for idx, res in enumerate(results_finbert, 1):
        print(f"Tweet {idx}:")
        print(f"  Text: {res['tweet']}")
        print(f"  Sentiment: {res['sentiment']}")
        print(f"  Date: {res['created_at']}")
        print(f"  Likes: {res['likes']}")
        print(f"  Retweets: {res['retweets']}")
        print()