"""
Streamlit-based UI for the Investment Recommendation project
Allows the user to provide required data (API keys, portfolio params, tickers or CSV)
and runs the hybrid recommendation engine or the investment dashboard.

Run: streamlit run src/ui/streamlit_app.py

This file is intentionally lightweight and defensive: it will fall back to a CLI demo
if Streamlit is not available or the app is run directly with Python.
"""

from typing import List
import json
import io
import os
import sys

try:
    import streamlit as st
except Exception:
    st = None

# Ensure the `src` directory is on sys.path so imports like
# `analysis_engine.*` and `ui.*` work when running from the repo root.
SRC_DIR = os.path.dirname(os.path.dirname(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Delay importing heavy or project-local modules until runtime to avoid circular imports
# We'll import `HybridRecommendationEngine` and `InvestmentDashboard` inside the button handler.

APP_TITLE = "AI Investment Recommendation - Interactive UI"


def parse_tickers_input(text: str) -> List[str]:
    if not text:
        return []
    # Split by comma/newline and normalize
    parts = [p.strip().upper() for p in text.replace('\n', ',').split(',')]
    return [p for p in parts if p]


def run_streamlit_app():
    if st is None:
        print("Streamlit is not installed. Please install streamlit and run `streamlit run src/ui/streamlit_app.py`.")
        return

    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)

    st.markdown("Provide API keys (optional) and portfolio inputs, then click Run to generate recommendations.")

    with st.expander("API Keys (optional)"):
        av_key = st.text_input("Alpha Vantage API Key", type="password")
        marketaux_key = st.text_input("MarketAux API Key", type="password")
        fred_key = st.text_input("FRED API Key", type="password")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Portfolio inputs")
        portfolio_size = st.number_input("Portfolio size (USD)", min_value=1000.0, value=100000.0, step=1000.0, format="%.2f")
        risk_tolerance = st.selectbox("Risk tolerance", options=["conservative", "moderate", "aggressive"], index=1)
        max_sectors = st.slider("Max sectors", min_value=1, max_value=10, value=4)
        stocks_per_sector = st.slider("Stocks per sector", min_value=1, max_value=10, value=3)

        st.subheader("Focus tickers")
        tickers_text = st.text_area("Enter tickers separated by commas or new lines (e.g. AAPL, MSFT)", height=80)

        uploaded_file = st.file_uploader("Or upload CSV with a column 'ticker'", type=["csv"])  

    with col2:
        st.subheader("Advanced options")
        use_dashboard = st.checkbox("Use Investment Dashboard flow (includes AI insights)", value=True)
        save_reports = st.checkbox("Save report JSON locally", value=True)

    tickers = parse_tickers_input(tickers_text)
    if uploaded_file is not None:
        try:
            import pandas as pd
            df = pd.read_csv(uploaded_file)
            if 'ticker' in df.columns:
                tickers_from_csv = df['ticker'].astype(str).str.upper().tolist()
            else:
                # try first column
                tickers_from_csv = df.iloc[:, 0].astype(str).str.upper().tolist()
            tickers = list(dict.fromkeys(tickers + tickers_from_csv))
        except Exception as e:
            st.error(f"Failed to parse uploaded CSV: {e}")

    st.write(f"Detected tickers: {', '.join(tickers[:25]) if tickers else 'None'}")

    run_button = st.button("Run Analysis")

    if run_button:
        # Save API keys to environment for downstream clients (optional)
        if av_key:
            os.environ['ALPHA_VANTAGE_API_KEY'] = av_key
        if marketaux_key:
            os.environ['MARKETAUX_API_KEY'] = marketaux_key
        if fred_key:
            os.environ['FRED_API_KEY'] = fred_key

        with st.spinner("Running analysis — this may take a while depending on tickers and APIs..."):
            try:
                # Import heavy project modules lazily to avoid startup import cycles
                from analysis_engine.hybrid_recommendations import HybridRecommendationEngine
                from ui.investment_dashboard import InvestmentDashboard

                if use_dashboard:
                    dash = InvestmentDashboard()
                    results = dash.generate_comprehensive_analysis(
                        portfolio_size=portfolio_size,
                        risk_tolerance=risk_tolerance,
                        focus_tickers=tickers
                    )
                else:
                    engine = HybridRecommendationEngine()
                    results = engine.generate_investment_recommendations(
                        portfolio_size=portfolio_size,
                        risk_tolerance=risk_tolerance,
                        max_sectors=max_sectors,
                        stocks_per_sector=stocks_per_sector
                    )

                st.success("Analysis complete — results below")

                st.json(results)

                if save_reports:
                    # Offer to save JSON and download
                    filename = f"recommendation_report_{int(os.times().system)}.json"
                    json_str = json.dumps(results, indent=2, default=str)

                    st.download_button("Download JSON report", data=json_str, file_name=filename, mime="application/json")

            except Exception as e:
                st.error(f"Error running analysis: {e}")


if __name__ == "__main__":
    # If Streamlit is available and this file is run with `streamlit run`, Streamlit will execute the script normally.
    # If running directly with `python -m src.ui.streamlit_app` provide a quick CLI fallback demo.
    if st is None:
        print("Streamlit not detected — running a quick CLI demo")
        try:
            from ui.investment_dashboard import InvestmentDashboard
            dash = InvestmentDashboard()
            demo = dash.generate_comprehensive_analysis(portfolio_size=50000, risk_tolerance='moderate', focus_tickers=['AAPL','MSFT'])
            print(json.dumps(demo, indent=2, default=str))
        except Exception as e:
            print(f"Demo failed: {e}")
    else:
        run_streamlit_app()
