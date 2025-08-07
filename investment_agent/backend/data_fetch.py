import yfinance as yf
from newsapi import NewsApiClient
from config import NEWS_API_KEY

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