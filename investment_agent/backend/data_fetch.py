import yfinance as yf
from newsapi import NewsApiClient
from config import NEWS_API_KEY
import praw
from config import REDDIT_CLIENT_ID, REDDIT_SECRET, REDDIT_USER_AGENT

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    info = stock.info
    return {
        "price": round(data['Close'][-1], 2),
        "pe_ratio": info.get("trailingPE"),
        "eps": info.get("trailingEps"),
        "volume": int(data['Volume'][-1])
    }

def get_latest_headlines(query):
    if not NEWS_API_KEY or NEWS_API_KEY == "YOUR_NEWSAPI_KEY":
        return [
            "Sample positive news about the market.",
            "Market outlook improves as investors gain confidence.",
            "Tech stocks rally amid strong earnings.",
            "Some negative sentiment arises due to inflation fears."
        ]
    
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    articles = newsapi.get_everything(q=query, language="en", page_size=5)
    return [a['title'] for a in articles['articles']]





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