"""
Enhanced Streamlit-based UI for the AI Investment Recommendation System
Features comprehensive visualizations, interactive charts, and detailed analysis displays.
Allows users to analyze portfolios with visual insights instead of raw JSON output.

Run: streamlit run src/ui/streamlit_app.py
"""

from typing import List, Dict, Any
import json
import io
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

try:
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.figure_factory as ff
except Exception:
    st = None

# Ensure the `src` directory is on sys.path so imports like
# `analysis_engine.*` and `ui.*` work when running from the repo root.
SRC_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)

# Add both src directory and project root to Python path
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Delay importing heavy or project-local modules until runtime to avoid circular imports
# We'll import `HybridRecommendationEngine` and `InvestmentDashboard` inside the button handler.

APP_TITLE = "AI Investment Recommendation - Interactive UI"


def parse_tickers_input(text: str) -> List[str]:
    if not text:
        return []
    # Split by comma/newline and normalize
    parts = [p.strip().upper() for p in text.replace('\n', ',').split(',')]
    return [p for p in parts if p]


def display_sector_analysis(sector_data: Dict[str, Any]):
    """Display sector analysis with interactive visualizations"""
    st.header("📊 Sector Analysis")
    
    if 'error' in sector_data:
        st.error(f"Sector analysis error: {sector_data['error']}")
        return
    
    if 'sector_rankings' not in sector_data:
        st.warning("No sector rankings data available")
        return
    
    rankings = sector_data['sector_rankings'].get('rankings', [])
    if not rankings:
        st.warning("No sector rankings found")
        return
    
    # Create sector performance chart
    sectors_df = pd.DataFrame(rankings)
    sectors_df['sector_name'] = sectors_df['sector'].str.replace('_', ' ').str.title()
    
    # Sector sentiment scores
    fig_sentiment = px.bar(
        sectors_df,
        x='sector_name',
        y='sentiment_score',
        color='sentiment_score',
        color_continuous_scale='RdYlGn',
        title="Sector Sentiment Scores",
        labels={'sentiment_score': 'Sentiment Score', 'sector_name': 'Sector'}
    )
    fig_sentiment.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig_sentiment, width='stretch')
    
    # Top 3 sectors
    col1, col2, col3 = st.columns(3)
    for i, (col, sector) in enumerate(zip([col1, col2, col3], rankings[:3])):
        with col:
            st.metric(
                label=f"#{i+1} {sector['sector'].replace('_', ' ').title()}",
                value=f"{sector['sentiment_score']:+.3f}",
                delta=sector['etf_ticker']
            )
    
    # Recommendations
    recommendations = sector_data['sector_rankings'].get('recommendations', {})
    if recommendations:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🟢 Overweight Recommendations")
            overweight = recommendations.get('overweight', [])
            for sector in overweight:
                st.success(f"• {sector.replace('_', ' ').title()}")
        
        with col2:
            st.subheader("🔴 Underweight Recommendations")
            underweight = recommendations.get('underweight', [])
            for sector in underweight:
                st.error(f"• {sector.replace('_', ' ').title()}")


def display_portfolio_allocation(hybrid_data: Dict[str, Any]):
    """Display portfolio allocation with pie charts and allocation tables"""
    st.header("💼 Portfolio Recommendations")
    
    if 'error' in hybrid_data:
        st.error(f"Portfolio analysis error: {hybrid_data['error']}")
        return
    
    # Portfolio summary metrics
    if 'portfolio_summary' in hybrid_data:
        summary = hybrid_data['portfolio_summary']
        risk_assessment = hybrid_data.get('risk_assessment', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Positions", summary.get('total_positions', 0))
        with col2:
            st.metric("Sectors Selected", summary.get('sectors_selected', 0))
        with col3:
            st.metric("Risk Level", risk_assessment.get('risk_level', 'Unknown'))
        with col4:
            st.metric("Diversification Score", f"{risk_assessment.get('diversification_score', 0):.0f}/100")
    
    # Portfolio allocation pie chart
    if 'portfolio_allocation' in hybrid_data:
        allocation = hybrid_data['portfolio_allocation']
        
        # Prepare data for pie chart
        sectors = []
        percentages = []
        amounts = []
        
        for sector, data in allocation.items():
            sectors.append(sector.replace('_', ' ').title())
            percentages.append(data['sector_percentage'])
            amounts.append(data['sector_allocation'])
        
        # Pie chart for allocation
        fig_pie = px.pie(
            values=percentages,
            names=sectors,
            title="Portfolio Allocation by Sector",
            hover_data=[amounts]
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, width='stretch')
        
        # Detailed allocation table
        st.subheader("Detailed Allocation")
        allocation_df = pd.DataFrame([
            {
                'Sector': sector.replace('_', ' ').title(),
                'Percentage': f"{data['sector_percentage']:.1f}%",
                'Amount': f"${data['sector_allocation']:,.0f}",
                'Stocks': len(data.get('stocks', []))
            }
            for sector, data in allocation.items()
        ])
        st.dataframe(allocation_df, width='stretch')
        
        # Individual stock recommendations
        st.subheader("Stock Recommendations by Sector")
        for sector, data in allocation.items():
            with st.expander(f"{sector.replace('_', ' ').title()} - ${data['sector_allocation']:,.0f} ({data['sector_percentage']:.1f}%)"):
                stocks = data.get('stocks', [])
                if stocks:
                    stocks_df = pd.DataFrame(stocks)
                    if not stocks_df.empty:
                        st.dataframe(stocks_df, width='stretch')
                else:
                    st.info("No specific stock recommendations available for this sector")


def display_single_stock_analysis(ticker: str, data: Dict[str, Any]):
    """Display analysis for a single stock"""
    if 'error' in data:
        st.error(f"Error analyzing {ticker}: {data['error']}")
        return
    
    st.subheader(f"📊 {ticker} Analysis")
    
    # Stock metrics
    col1, col2, col3 = st.columns(3)
    
    sentiment_analysis = data.get('sentiment_analysis', {})
    
    with col1:
        sentiment_score = sentiment_analysis.get('combined_sentiment_score', 0)
        sentiment_label = sentiment_analysis.get('sentiment_label', 'Neutral')
        st.metric(
            "Sentiment Score", 
            f"{sentiment_score:+.3f}",
            delta=sentiment_label
        )
    
    with col2:
        confidence = sentiment_analysis.get('confidence_score', 0)
        st.metric("Confidence", f"{confidence:.1f}%")
    
    with col3:
        news_count = len(data.get('news_articles', []))
        st.metric("News Articles", news_count)
    
    # Sentiment breakdown
    if 'sentiment_breakdown' in sentiment_analysis:
        breakdown = sentiment_analysis['sentiment_breakdown']
        
        # Sentiment distribution pie chart
        sentiments = ['Positive', 'Negative', 'Neutral']
        values = [
            breakdown.get('positive', 0),
            breakdown.get('negative', 0),
            breakdown.get('neutral', 0)
        ]
        
        if sum(values) > 0:
            fig_sentiment_dist = px.pie(
                values=values,
                names=sentiments,
                title=f"{ticker} Sentiment Distribution",
                color_discrete_map={
                    'Positive': '#00CC96',
                    'Negative': '#EF553B',
                    'Neutral': '#FFA15A'
                }
            )
            st.plotly_chart(fig_sentiment_dist, width='stretch')
    
    # News articles summary
    news_articles = data.get('news_articles', [])
    if news_articles:
        st.subheader("Recent News")
        for i, article in enumerate(news_articles[:5]):  # Show top 5
            with st.expander(f"📰 {article.get('title', 'No title')[:100]}..."):
                st.write(f"**Source:** {article.get('source', 'Unknown')}")
                st.write(f"**Date:** {article.get('date', 'Unknown')}")
                st.write(f"**Sentiment:** {article.get('sentiment', 'Unknown')}")
                if 'summary' in article:
                    st.write(f"**Summary:** {article['summary']}")


def display_individual_stocks(stocks_data: Dict[str, Any], focus_tickers: List[str] = None):
    """Display individual stock analysis with sentiment and metrics"""
    st.header("📈 Individual Stock Analysis")
    
    if not stocks_data:
        st.info("No individual stock analysis data available")
        return
    
    # Filter stocks if focus_tickers is provided
    if focus_tickers:
        # Only show stocks that are in the focus list
        filtered_stocks = {ticker: data for ticker, data in stocks_data.items() 
                          if ticker in focus_tickers}
        if not filtered_stocks:
            st.warning("None of the focus stocks have detailed analysis data available.")
            st.info(f"Focus stocks: {', '.join(focus_tickers)}")
            st.info(f"Available analysis: {', '.join(stocks_data.keys())}")
            return
        stocks_to_display = filtered_stocks
        st.info(f"Showing analysis for focus stocks: {', '.join(filtered_stocks.keys())}")
    else:
        stocks_to_display = stocks_data
    
    # Create tabs for each stock
    if len(stocks_to_display) == 1:
        # Single stock - no tabs needed
        ticker, data = list(stocks_to_display.items())[0]
        display_single_stock_analysis(ticker, data)
    else:
        # Multiple stocks - use tabs
        stock_tabs = st.tabs(list(stocks_to_display.keys()))
        
        for tab, (ticker, data) in zip(stock_tabs, stocks_to_display.items()):
            with tab:
                display_single_stock_analysis(ticker, data)



def display_ai_insights(ai_data: Dict[str, Any]):
    """Display AI insights and learning metrics"""
    st.header("🤖 AI System Intelligence")
    
    if 'error' in ai_data:
        st.error(f"AI insights error: {ai_data['error']}")
        return
    
    # AI metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_feedback = ai_data.get('total_feedback_count', 0)
        st.metric("Total AI Feedback", total_feedback)
    
    with col2:
        sentiment_feedback = ai_data.get('sentiment_feedback_count', 0)
        st.metric("Sentiment Corrections", sentiment_feedback)
    
    with col3:
        classification_feedback = ai_data.get('classification_feedback_count', 0)
        st.metric("Classification Corrections", classification_feedback)
    
    # AI recommendations
    recommendations = ai_data.get('recommendations', [])
    if recommendations:
        st.subheader("AI Improvement Recommendations")
        for rec in recommendations:
            st.info(f"💡 {rec}")
    else:
        st.info("💡 Collect user feedback to improve AI accuracy over time")


def display_executive_summary(results: Dict[str, Any]):
    """Display executive summary with key insights"""
    st.header("📋 Executive Summary")
    
    metadata = results.get('metadata', {})
    portfolio_size = metadata.get('portfolio_size', 0)
    risk_tolerance = metadata.get('risk_tolerance', 'Unknown')
    
    # Key metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Portfolio Overview")
        st.write(f"**Portfolio Size:** ${portfolio_size:,.0f}")
        st.write(f"**Risk Tolerance:** {risk_tolerance.title()}")
        st.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        st.subheader("Analysis Coverage")
        components = []
        if 'sector_analysis' in results:
            components.append("✅ Sector Analysis")
        if 'hybrid_recommendations' in results:
            components.append("✅ Portfolio Recommendations")
        if 'individual_stocks' in results:
            components.append("✅ Individual Stock Analysis")
        if 'ai_insights' in results:
            components.append("✅ AI Intelligence")
        
        for component in components:
            st.write(component)
    
    # Key insights
    st.subheader("Key Insights")
    
    # Focus stocks summary
    focus_tickers = metadata.get('focus_tickers', [])
    if focus_tickers:
        st.info(f"🎯 **Focus Stocks:** {', '.join(focus_tickers)}")
        
        # Show focus stock sentiments if available
        individual_stocks = results.get('individual_stocks', {})
        if individual_stocks:
            focus_sentiments = []
            for ticker in focus_tickers[:3]:  # Show top 3
                if ticker in individual_stocks:
                    stock_data = individual_stocks[ticker]
                    if 'sentiment_analysis' in stock_data:
                        sentiment = stock_data['sentiment_analysis']
                        score = sentiment.get('combined_sentiment_score', 0)
                        label = sentiment.get('sentiment_label', 'Neutral')
                        focus_sentiments.append(f"{ticker}: {label} ({score:+.3f})")
            
            if focus_sentiments:
                st.write("**Focus Stock Sentiments:**")
                for sentiment_info in focus_sentiments:
                    st.write(f"  • {sentiment_info}")
    
    # Top sector recommendation
    sector_analysis = results.get('sector_analysis', {})
    if 'sector_rankings' in sector_analysis:
        rankings = sector_analysis['sector_rankings'].get('rankings', [])
        if rankings:
            top_sector = rankings[0]
            st.success(f"🏆 **Top Sector:** {top_sector['sector'].replace('_', ' ').title()} "
                      f"(Score: {top_sector['sentiment_score']:+.3f})")
    
    # Risk assessment
    hybrid_recs = results.get('hybrid_recommendations', {})
    if 'risk_assessment' in hybrid_recs:
        risk_assessment = hybrid_recs['risk_assessment']
        risk_level = risk_assessment.get('risk_level', 'Unknown')
        diversification = risk_assessment.get('diversification_score', 0)
        
        if risk_level == 'High':
            st.warning(f"⚠️ **Risk Level:** {risk_level} - Consider reducing concentration")
        else:
            st.info(f"⚡ **Risk Level:** {risk_level}")
        
        st.info(f"📊 **Diversification Score:** {diversification:.0f}/100")


def run_streamlit_app():
    if st is None:
        print("Streamlit is not installed. Please install streamlit and run `streamlit run src/ui/streamlit_app.py`.")
        return

    st.set_page_config(
        page_title="AI Investment Recommendation System",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main title with styling
    st.markdown("""
    <h1 style='text-align: center; color: #1f77b4;'>
    📈 AI Investment Recommendation System
    </h1>
    <p style='text-align: center; color: #666;'>
    Advanced portfolio analysis with AI-powered insights and visualizations
    </p>
    """, unsafe_allow_html=True)

    # Sidebar for inputs
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys section
        with st.expander("🔐 API Keys (Optional)"):
            av_key = st.text_input("Alpha Vantage API Key", type="password")
            marketaux_key = st.text_input("MarketAux API Key", type="password")
            fred_key = st.text_input("FRED API Key", type="password")
            
            if st.button("💾 Save API Keys"):
                if av_key:
                    os.environ['ALPHA_VANTAGE_API_KEY'] = av_key
                if marketaux_key:
                    os.environ['MARKETAUX_API_KEY'] = marketaux_key
                if fred_key:
                    os.environ['FRED_API_KEY'] = fred_key
                st.success("API keys saved!")

        # Portfolio Configuration
        st.subheader("💼 Portfolio Configuration")
        portfolio_size = st.number_input(
            "Portfolio Size (USD)", 
            min_value=1000.0, 
            value=100000.0, 
            step=1000.0, 
            format="%.0f"
        )
        
        risk_tolerance = st.selectbox(
            "Risk Tolerance", 
            options=["conservative", "moderate", "aggressive"], 
            index=1
        )
        
        max_sectors = st.slider("Max Sectors", min_value=1, max_value=10, value=4)
        stocks_per_sector = st.slider("Stocks per Sector", min_value=1, max_value=10, value=3)

        # Stock Selection
        st.subheader("📊 Focus Stocks")
        tickers_text = st.text_area(
            "Enter stock tickers (comma or newline separated)",
            placeholder="AAPL, MSFT, GOOGL\nTSLA\nNVDA",
            height=100
        )

        uploaded_file = st.file_uploader("📁 Or upload CSV with tickers", type=["csv"])

        # Advanced Options
        st.subheader("🔧 Advanced Options")
        use_dashboard = st.checkbox("Use Investment Dashboard (AI insights)", value=True)
        focus_only = st.checkbox("Show only focus stocks in analysis", value=True, 
                                help="When enabled, individual stock analysis will show only the focus stocks you specified above")
        auto_refresh = st.checkbox("Auto-refresh data", value=False)
        save_reports = st.checkbox("Enable report downloads", value=True)

    # Process ticker input
    tickers = parse_tickers_input(tickers_text)
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if 'ticker' in df.columns:
                tickers_from_csv = df['ticker'].astype(str).str.upper().tolist()
            else:
                tickers_from_csv = df.iloc[:, 0].astype(str).str.upper().tolist()
            tickers = list(dict.fromkeys(tickers + tickers_from_csv))
        except Exception as e:
            st.error(f"Failed to parse uploaded CSV: {e}")

    # Display selected tickers
    if tickers:
        st.info(f"**Selected Tickers:** {', '.join(tickers[:15])}" + 
                (f" and {len(tickers) - 15} more..." if len(tickers) > 15 else ""))

    # Main analysis button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_analysis = st.button(
            "🚀 Run Comprehensive Analysis", 
            type="primary",
            width='stretch'
        )

    # Run analysis
    if run_analysis:
        with st.spinner("🔄 Running comprehensive analysis... This may take a few minutes."):
            try:
                # Import modules
                try:
                    from analysis_engine.hybrid_recommendations import HybridRecommendationEngine
                    from ui.investment_dashboard import InvestmentDashboard
                except ImportError:
                    from src.analysis_engine.hybrid_recommendations import HybridRecommendationEngine
                    from src.ui.investment_dashboard import InvestmentDashboard

                # Run analysis
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

                # Display results with visualizations
                st.success("✅ Analysis completed successfully!")
                
                # Create tabs for different sections
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    "📋 Executive Summary",
                    "📊 Sector Analysis", 
                    "💼 Portfolio Allocation",
                    "📈 Individual Stocks",
                    "🤖 AI Insights",
                    "📄 Raw Data"
                ])
                
                with tab1:
                    display_executive_summary(results)
                
                with tab2:
                    if 'sector_analysis' in results:
                        display_sector_analysis(results['sector_analysis'])
                    else:
                        st.info("No sector analysis data available")
                
                with tab3:
                    if 'hybrid_recommendations' in results:
                        display_portfolio_allocation(results['hybrid_recommendations'])
                    else:
                        st.info("No portfolio recommendations available")
                
                with tab4:
                    if 'individual_stocks' in results:
                        # Get focus tickers from metadata if focus_only is enabled
                        focus_tickers_to_show = None
                        if focus_only:
                            focus_tickers_to_show = results.get('metadata', {}).get('focus_tickers', [])
                        display_individual_stocks(results['individual_stocks'], focus_tickers_to_show)
                    else:
                        st.info("No individual stock analysis available")
                
                with tab5:
                    if 'ai_insights' in results:
                        display_ai_insights(results['ai_insights'])
                    else:
                        st.info("No AI insights available")
                
                with tab6:
                    st.json(results)

                # Download options
                if save_reports:
                    st.divider()
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # JSON download
                        json_str = json.dumps(results, indent=2, default=str)
                        st.download_button(
                            "📄 Download JSON Report",
                            data=json_str,
                            file_name=f"investment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        # CSV download for portfolio allocation
                        if 'hybrid_recommendations' in results and 'portfolio_allocation' in results['hybrid_recommendations']:
                            allocation = results['hybrid_recommendations']['portfolio_allocation']
                            allocation_df = pd.DataFrame([
                                {
                                    'Sector': sector.replace('_', ' ').title(),
                                    'Percentage': data['sector_percentage'],
                                    'Amount': data['sector_allocation']
                                }
                                for sector, data in allocation.items()
                            ])
                            csv_data = allocation_df.to_csv(index=False)
                            st.download_button(
                                "📊 Download Portfolio CSV",
                                data=csv_data,
                                file_name=f"portfolio_allocation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )

            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.error("Please check your API keys and try again.")
                
                # Show error details in expander
                with st.expander("🔍 Error Details"):
                    st.exception(e)


if __name__ == "__main__":
    # If Streamlit is available and this file is run with `streamlit run`, Streamlit will execute the script normally.
    # If running directly with `python -m src.ui.streamlit_app` provide a quick CLI fallback demo.
    if st is None:
        print("Streamlit not detected — running a quick CLI fallback demo")
        try:
            try:
                from ui.investment_dashboard import InvestmentDashboard
            except ImportError:
                from src.ui.investment_dashboard import InvestmentDashboard
            
            dash = InvestmentDashboard()
            demo = dash.generate_comprehensive_analysis(portfolio_size=50000, risk_tolerance='moderate', focus_tickers=['AAPL','MSFT'])
            print(json.dumps(demo, indent=2, default=str))
        except Exception as e:
            print(f"Demo failed: {e}")
    else:
        run_streamlit_app()
