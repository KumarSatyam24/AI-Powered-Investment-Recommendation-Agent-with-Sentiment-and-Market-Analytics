from transformers import pipeline
from config import MODEL_NAME

# Force PyTorch instead of TensorFlow
sentiment_analyzer = pipeline("sentiment-analysis", model=MODEL_NAME, framework="pt")

def analyze_sentiment(headlines):
    sentiments = sentiment_analyzer(headlines)
    avg_score = sum([
        1 if s['label'].lower() == 'positive' else -1 if s['label'].lower() == 'negative' else 0
        for s in sentiments
    ]) / len(sentiments)
    return "Positive" if avg_score > 0 else "Negative" if avg_score < 0 else "Neutral"