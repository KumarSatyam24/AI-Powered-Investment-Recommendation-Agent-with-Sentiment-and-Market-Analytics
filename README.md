# 💼 AI-Powered Investment Recommendation Agent with Sentiment and Market Analytics

The Stocks Recommendation System is a software project designed to analyze stock market data and provide actionable recommendations for investors. It leverages data science, machine learning, and financial analysis techniques to identify promising stocks based on historical trends, technical indicators, and predictive modeling.
---

> **Note:** This project is under active development. Features and documentation may change frequently.

## 🚀 Features
- 📈 Real-time stock and market data (price, volume, PE ratio, EPS)
- 📰 Multi-source sentiment analysis (NewsAPI, Reddit, Twitter/X, StockTwits)
- 🧠 Fine-tuned Hugging Face model for sentiment classification
- 🧩 LangChain-based recommendation agent
- 💾 Dual database architecture: SQLite + QuestDB
- 🌐 Streamlit-based interactive dashboard

---

## 🛠️ Technologies Used
- Python 3.11+
- Transformers (Hugging Face)
- LangChain
- Streamlit
- yfinance, NewsAPI, praw (Reddit), Tweepy (Twitter)
- SQLite + QuestDB
- Docker (optional for deployment)

---

## 🧪 Installation

1. Clone the repository:
```bash
git clone https://github.com/KumarSatyam24/AI-Powered-Investment-Recommendation-Agent-with-Sentiment-and-Market-Analytics.git
cd AI-Powered-Investment-Recommendation-Agent-with-Sentiment-and-Market-Analytics
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API keys in `config.py`:
```python
NEWS_API_KEY = "your_newsapi_key"
REDDIT_CLIENT_ID = "your_reddit_client_id"
REDDIT_SECRET = "your_reddit_secret"
TWITTER_BEARER_TOKEN = "your_twitter_token"
STOCKTWITS_TOKEN = "your_stocktwits_token"
MODEL_NAME = "your-finetuned-model"
```

> ⚠️ If you face errors with Keras 3, run:
> ```bash
> pip uninstall keras && pip install tf-keras
> ```

---

## 🚦 Usage

1. Start the dashboard:
```bash
streamlit run investment_agent/frontend/dashboard.py
```

2. Open in browser at:
```
http://localhost:8501
```

---

## 📁 Folder Structure
```
investment_agent/
├── backend/
│   ├── data_fetch.py
│   ├── recommender.py
│   ├── database_manager.py
│   └── sentiment_engine/
│       ├── news_sentiment.py
│       ├── reddit_sentiment.py
│       ├── twitter_sentiment.py
│       ├── stocktwits_sentiment.py
│       ├── fusion.py
│       └── sentiment_model.py
├── frontend/
│   └── dashboard.py
├── config.py
├── requirements.txt
└── README.md
```

---

## 👤 Author
**Satyam Kumar**  
[GitHub](https://github.com/KumarSatyam24)

## 📄 License
This project is licensed under the MIT License.

