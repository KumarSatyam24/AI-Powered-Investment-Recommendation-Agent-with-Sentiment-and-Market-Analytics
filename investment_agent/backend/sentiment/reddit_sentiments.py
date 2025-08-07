SENTIMENT_SCORE = {
    "POSITIVE": 1,
    "NEUTRAL": 0,
    "NEGATIVE": -1
}
from backend.data_fetch import get_reddit_posts
from backend.sentiment.sentiment_model import sentiment_analyzer
from transformers import pipeline
from datetime import datetime, timedelta

def aggregate_sentiment(finbert, general):
    f_label = finbert["label"].upper()
    g_label = general["label"].upper()
    
    f_score = SENTIMENT_SCORE.get(f_label, 0)
    g_score = SENTIMENT_SCORE.get(g_label, 0)
    
    agg_score = 0.3 * f_score + 0.7 * g_score

    if agg_score > 0.5:
        return "POSITIVE"
    elif agg_score < -0.5:
        return "NEGATIVE"
    else:
        return "NEUTRAL"

general_sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_reddit_sentiment(ticker):
    posts = get_reddit_posts(ticker)  # now returns list of dicts with "title" and "comments"
    max_age = datetime.utcnow() - timedelta(days=100)    # Filter posts older than 40 days
    sentiments = []
    for post_data in posts:
        post_time = datetime.utcfromtimestamp(post_data.get("created_utc", 0))
        if post_time < max_age:
            continue
        title = post_data["title"]
        finbert_result = sentiment_analyzer(title, truncation=True)
        general_result = general_sentiment_analyzer(title, truncation=True)
        sentiments.append({
            "type": "post",
            "text": title,
            "finbert_sentiment": finbert_result,
            "general_sentiment": general_result
        })
        for comment in post_data.get("comments", []):
            if (
                not comment.strip()
                or "Join WSB Discord" in comment
                or comment.startswith("http")
                or "User Report" in comment
                or "[**" in comment  # link-markdown
                or "youtu.be" in comment or "youtube.com" in comment
                or len(comment.strip()) < 10
            ):
                continue
            finbert_result = sentiment_analyzer(comment, truncation=True)
            general_result = general_sentiment_analyzer(comment, truncation=True)
            sentiments.append({
                "type": "comment",
                "text": comment,
                "finbert_sentiment": finbert_result,
                "general_sentiment": general_result
            })
    if not sentiments:
        sentiments.append({
            "type": "post",
            "text": f"No recent posts or comments found for {ticker}",
            "finbert_sentiment": [{"label": "NEUTRAL", "score": 1.0}],
            "general_sentiment": [{"label": "NEUTRAL", "score": 1.0}]
        })
    return sentiments

from collections import Counter

def summarize_sentiment(results):
    summary = Counter()
    for item in results:
        agg = aggregate_sentiment(item["finbert_sentiment"][0], item["general_sentiment"][0])
        summary[agg] += 1
    return summary

# Test code
if __name__ == "__main__":
    results = analyze_reddit_sentiment("nvdia")
    for item in results:
        fb = item["finbert_sentiment"][0]
        gen = item["general_sentiment"][0]
        prefix = "POST" if item["type"] == "post" else "COMMENT"
        print(f"[{prefix}] FinBERT: {fb['label'].upper()} ({fb['score']:.2f}) | General: {gen['label'].upper()} ({gen['score']:.2f})")
        print(f"Text: {item['text']}\n")

    summary = summarize_sentiment(results)
    print("\n--- Aggregated Sentiment Summary ---")
    for label, count in summary.items():
        print(f"{label}: {count}")
