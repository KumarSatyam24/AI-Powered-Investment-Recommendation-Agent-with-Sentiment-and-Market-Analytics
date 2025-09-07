from collections import Counter
import torch

SENTIMENT_SCORE = {
    "POSITIVE": 1,
    "NEUTRAL": 0,
    "NEGATIVE": -1
}
from src.data_processing.data_fetch import get_reddit_posts
from src.api_clients.grok_api import GrokTwitterClient
from transformers import pipeline
from datetime import datetime, timedelta

# Initialize sentiment analyzer
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

def contains_financial_facts(text):
    keywords = [
        "EPS", "revenue", "profit", "loss", "quarter", "guidance",
        "forecast", "dividend", "$", "%", "market cap", "earnings", "growth"
    ]
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False

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

def analyze_reddit_sentiment(ticker, use_grok_fallback=True):
    # Try to get Reddit posts from API first
    posts = get_reddit_posts(ticker)
    reddit_api_failed = False
    
    # Check if Reddit API failed (empty result often indicates API issues)
    if not posts:
        reddit_api_failed = True
        print(f"Reddit API returned no posts for {ticker}")
    
    # If Reddit API failed and Grok fallback is enabled, use Grok
    if reddit_api_failed and use_grok_fallback:
        print(f"Using Grok fallback to generate Reddit posts for {ticker}")
        try:
            grok_client = GrokTwitterClient()
            grok_posts = grok_client.get_reddit_posts_from_grok(ticker, limit=10)
            # Convert Grok posts to expected format
            posts = []
            import time
            current_time = int(time.time())  # Current timestamp
            for grok_post in grok_posts:
                posts.append({
                    "title": grok_post.get("title", ""),
                    "comments": grok_post.get("comments", []),
                    "created_utc": current_time - 3600,  # 1 hour ago (recent)
                    "score": grok_post.get("score", 10)
                })
            print(f"Generated {len(posts)} Reddit posts using Grok")
        except Exception as e:
            print(f"Grok fallback also failed: {e}")
            posts = []
    
    max_age = datetime.utcnow() - timedelta(days=20)    # Filter posts older than 20 days

    texts = []
    types = []
    post_indices = []
    comment_indices = []

    for post_data in posts:
        post_time = datetime.utcfromtimestamp(post_data.get("created_utc", 0))
        if post_time < max_age:
            continue
        title = post_data["title"]
        texts.append(title)
        types.append("post")
        post_indices.append(len(texts)-1)
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
            texts.append(comment)
            types.append("comment")
            comment_indices.append(len(texts)-1)

    if not texts:
        return [{
            "type": "post",
            "text": f"No recent posts or comments found for {ticker}",
            "finbert_sentiment": [{"label": "NEUTRAL", "score": 1.0}],
            "general_sentiment": [{"label": "NEUTRAL", "score": 1.0}]
        }]

    finance_texts = []
    finance_indices = []
    general_texts = []
    general_indices = []

    for i, text in enumerate(texts):
        if contains_financial_facts(text):
            finance_texts.append(text)
            finance_indices.append(i)
        else:
            general_texts.append(text)
            general_indices.append(i)

    finbert_results = sentiment_analyzer(finance_texts, truncation=True) if finance_texts else []
    general_results = general_sentiment_analyzer(general_texts, truncation=True) if general_texts else []

    # Prepare neutral placeholder
    neutral_placeholder = [{"label": "NEUTRAL", "score": 1.0}]

    sentiments = [None] * len(texts)
    for idx, fin_idx in enumerate(finance_indices):
        sentiments[fin_idx] = {
            "type": types[fin_idx],
            "text": texts[fin_idx],
            "finbert_sentiment": [finbert_results[idx]] if isinstance(finbert_results[idx], dict) else finbert_results[idx],
            "general_sentiment": neutral_placeholder
        }
    for idx, gen_idx in enumerate(general_indices):
        sentiments[gen_idx] = {
            "type": types[gen_idx],
            "text": texts[gen_idx],
            "finbert_sentiment": neutral_placeholder,
            "general_sentiment": [general_results[idx]] if isinstance(general_results[idx], dict) else general_results[idx]
        }
    return sentiments



def summarize_sentiment(results):
    summary = Counter()
    for item in results:
        agg = aggregate_sentiment(item["finbert_sentiment"][0], item["general_sentiment"][0])
        weight = 2 if item["type"] == "post" else 1
        summary[agg] += weight
    return summary

# Test code
if __name__ == "__main__":
    print("Testing Reddit Sentiment Analysis with Grok Fallback")
    print("=" * 60)
    
    results = analyze_reddit_sentiment("aapl", use_grok_fallback=True)
    
    print(f"\nAnalyzed {len(results)} Reddit posts/comments:")
    for i, item in enumerate(results, 1):
        fb = item["finbert_sentiment"][0]
        gen = item["general_sentiment"][0]
        prefix = "POST" if item["type"] == "post" else "COMMENT"
        print(f"\n[{i}] [{prefix}] FinBERT: {fb['label'].upper()} ({fb['score']:.2f}) | General: {gen['label'].upper()} ({gen['score']:.2f})")
        print(f"Text: {item['text'][:200]}{'...' if len(item['text']) > 200 else ''}")

    summary = summarize_sentiment(results)
    print("\n" + "="*60)
    print("AGGREGATED SENTIMENT SUMMARY")
    print("="*60)
    for label, count in summary.items():
        print(f"{label}: {count}")
