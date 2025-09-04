#!/usr/bin/env python3
"""
AI-Powered Investment Recommendation System
Main entry point for the application

Usage:
    python main.py              # Run CLI analysis
    python main.py --ui          # Start Streamlit web interface
    python main.py --help        # Show help
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="AI-Powered Investment Recommendation System")
    parser.add_argument("--ui", action="store_true", help="Start Streamlit web interface")
    parser.add_argument("--portfolio", type=float, default=100000, help="Portfolio size in USD (default: 100000)")
    parser.add_argument("--risk", choices=["conservative", "moderate", "aggressive"], default="moderate", help="Risk tolerance (default: moderate)")
    parser.add_argument("--tickers", nargs="*", help="Specific tickers to analyze (e.g., AAPL MSFT)")
    
    args = parser.parse_args()
    
    print("🚀 AI-Powered Investment Recommendation System")
    print("=" * 60)
    
    if args.ui:
        print("🌐 Starting Streamlit web interface...")
        print("📍 URL: http://localhost:8501")
        try:
            os.system("streamlit run src/ui/streamlit_app.py")
        except KeyboardInterrupt:
            print("\n👋 Streamlit server stopped")
        return
    
    # CLI Analysis
    print("💻 Running CLI analysis...")
    print(f"� Portfolio: ${args.portfolio:,.0f}")
    print(f"⚡ Risk: {args.risk}")
    if args.tickers:
        print(f"🎯 Focus tickers: {', '.join(args.tickers)}")
    print()
    
    try:
        from ui.investment_dashboard import InvestmentDashboard
        
        dashboard = InvestmentDashboard()
        results = dashboard.generate_comprehensive_analysis(
            portfolio_size=args.portfolio,
            risk_tolerance=args.risk,
            focus_tickers=args.tickers or []
        )
        
        print("\n✅ Analysis complete!")
        print("💡 Tip: Use --ui flag for interactive web interface")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Check your .env file and API keys")

if __name__ == "__main__":
    main()
