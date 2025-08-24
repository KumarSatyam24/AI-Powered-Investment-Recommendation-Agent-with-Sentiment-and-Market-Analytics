import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from backend.sentiment.fusion import fuse_sentiments
from backend.data_fetch import get_latest_headlines
from backend.sentiment.reddit_sentiments import get_reddit_posts
from backend.sentiment.twitter_sentiments import get_tweets


st.set_page_config(page_title="AI Investment Advisor", layout="wide")
st.title("📈 AI-Powered Investment Recommendation Agent")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TCS.NS)", "AAPL")
risk_level = st.selectbox("Select Risk Profile", ["Low", "Moderate", "High"])

if st.button("Analyze"):
    with st.spinner("Fetching data..."):
        stock_data = get_stock_data(ticker)
        headlines = get_latest_headlines(ticker)
        sentiment = analyze_sentiment(headlines)
        recommendation = generate_recommendation(sentiment, risk_level)

    st.subheader(f"📊 Stock Data for {ticker}")
    st.write(stock_data)

    st.subheader("📰 Latest Headlines")
    for h in headlines:
        st.write(f"- {h}")

    st.subheader("💡 Sentiment Analysis")
    st.write(f"Overall Sentiment: **{sentiment}**")

    st.subheader("✅ Final Recommendation")
    st.success(f"{recommendation}")