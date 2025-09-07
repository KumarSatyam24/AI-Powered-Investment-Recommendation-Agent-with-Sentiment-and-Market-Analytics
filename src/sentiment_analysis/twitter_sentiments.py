from langdetect import detect
import emoji
from transformers import pipeline
import torch
from src.data_processing.data_fetch import get_tweets
from src.api_clients.grok_api import GrokTwitterClient
import re
import os

# Initialize sentiment analyzers
device = 0 if torch.cuda.is_available() else -1

try:
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model="ProsusAI/finbert",
        framework="pt",
        device=device
    )
except:
    sentiment_analyzer = None

try:
    general_sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        framework="pt",
        device=device
    )
except:
    general_sentiment_analyzer = None

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


def analyze_twitter_sentiment(ticker, use_general=False, use_grok_fallback=True):
    """
    Fetches recent tweets for the given ticker and from influential people, then returns sentiment scores.
    If use_general is True, uses general_sentiment_analyzer (DistilBERT); otherwise uses sentiment_analyzer (FinBERT).
    If Twitter API fails due to rate limits, falls back to Grok-generated tweets.
    """
    tweets = []
    twitter_api_failed = False
    
    # Try to fetch tweets for ticker using Twitter API
    try:
        twitter_tweets = get_tweets(ticker)
        if not twitter_tweets:  # Empty result might indicate API issues
            twitter_api_failed = True
        else:
            for t in twitter_tweets:
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
    except Exception as e:
        print(f"Twitter API failed for ticker {ticker}: {e}")
        twitter_api_failed = True
    
    # Try to fetch tweets from influential people
    if not twitter_api_failed:
        for person in INFLUENTIAL_PEOPLE:
            try:
                person_tweets = get_tweets(person)
                for t in person_tweets:
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
            except Exception as e:
                print(f"Twitter API failed for {person}: {e}")
                twitter_api_failed = True
                break
    
    # Fallback to Grok if Twitter API failed and fallback is enabled
    if twitter_api_failed and use_grok_fallback:
        print(f"Using Grok fallback to generate tweets for {ticker}")
        try:
            grok_client = GrokTwitterClient()
            grok_tweets = grok_client.get_tweets_from_influencers(ticker, limit=15)
            for tweet in grok_tweets:
                tweets.append({
                    "text": tweet.get("text", ""),
                    "created_at": tweet.get("created_at", None),
                    "likes": tweet.get("like_count", 0),
                    "retweets": tweet.get("retweet_count", 0)
                })
            print(f"Generated {len(grok_tweets)} tweets using Grok")
        except Exception as e:
            print(f"Grok fallback also failed: {e}")
            return []
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
    print("Testing Twitter Sentiment Analysis with Grok Fallback")
    print("=" * 60)
    
    print("\nUsing general_sentiment_analyzer (DistilBERT):")
    results_general = analyze_twitter_sentiment("MSFT", use_general=True, use_grok_fallback=True)
    for idx, res in enumerate(results_general, 1):
        print(f"Tweet {idx}:")
        print(f"  Text: {res['tweet']}")
        print(f"  Sentiment: {res['sentiment']}")
        print(f"  Date: {res['created_at']}")
        print(f"  Likes: {res['likes']}")
        print(f"  Retweets: {res['retweets']}")
        print()
    
    print("\nUsing sentiment_analyzer (FinBERT):")
    results_finbert = analyze_twitter_sentiment("MSFT", use_general=False, use_grok_fallback=True)
    for idx, res in enumerate(results_finbert, 1):
        print(f"Tweet {idx}:")
        print(f"  Text: {res['tweet']}")
        print(f"  Sentiment: {res['sentiment']}")
        print(f"  Date: {res['created_at']}")
        print(f"  Likes: {res['likes']}")
        print(f"  Retweets: {res['retweets']}")
        print()