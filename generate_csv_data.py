#!/usr/bin/env python3
"""
CSV Data Generator Script
Easy-to-use script for generating comprehensive stock data CSV files

This script provides a command-line interface for exporting stock data
including sentiment scores for predictive modeling.

Usage:
    python generate_csv_data.py AAPL                    # Single stock
    python generate_csv_data.py AAPL MSFT GOOGL         # Multiple stocks
    python generate_csv_data.py --batch tech_stocks.txt # From file
    python generate_csv_data.py AAPL --days 60          # Custom timeframe
"""

import os
import sys
import argparse
from datetime import datetime
from typing import List

# Add project paths
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from src.data_export.stock_data_exporter import StockDataExporter
except ImportError:
    from data_export.stock_data_exporter import StockDataExporter


class CSVDataGenerator:
    """Command-line interface for generating stock CSV data"""
    
    def __init__(self):
        self.exporter = StockDataExporter()
        self.popular_stocks = {
            'tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX'],
            'finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK'],
            'healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'LLY'],
            'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'PSX', 'VLO'],
            'consumer': ['PG', 'KO', 'PEP', 'WMT', 'HD', 'MCD', 'NKE', 'SBUX']
        }
    
    def generate_single_stock(self, ticker: str, days: int = 30, 
                             include_news: bool = True, include_technical: bool = True) -> str:
        """Generate CSV for a single stock"""
        print(f"🎯 Generating CSV data for {ticker}")
        print(f"   📅 Timeframe: {days} days")
        print(f"   📰 Include news: {include_news}")
        print(f"   📊 Include technical: {include_technical}")
        print("-" * 50)
        
        csv_file = self.exporter.export_stock_data(
            ticker=ticker,
            days=days,
            include_news=include_news,
            include_technical=include_technical
        )
        
        if csv_file:
            self._display_file_info(csv_file)
        
        return csv_file
    
    def generate_multiple_stocks(self, tickers: List[str], days: int = 30) -> List[str]:
        """Generate CSV for multiple stocks"""
        print(f"🎯 Generating CSV data for {len(tickers)} stocks")
        print(f"   📊 Stocks: {', '.join(tickers)}")
        print(f"   📅 Timeframe: {days} days")
        print("-" * 50)
        
        csv_files = self.exporter.export_multiple_stocks(tickers, days)
        
        for csv_file in csv_files:
            if csv_file:
                self._display_file_info(csv_file)
        
        return csv_files
    
    def generate_sector_data(self, sector: str, days: int = 30) -> List[str]:
        """Generate CSV for stocks in a specific sector"""
        if sector.lower() not in self.popular_stocks:
            print(f"❌ Unknown sector: {sector}")
            print(f"Available sectors: {', '.join(self.popular_stocks.keys())}")
            return []
        
        tickers = self.popular_stocks[sector.lower()]
        print(f"🎯 Generating {sector.upper()} sector data")
        
        return self.generate_multiple_stocks(tickers, days)
    
    def generate_from_file(self, filename: str, days: int = 30) -> List[str]:
        """Generate CSV for tickers listed in a file"""
        try:
            with open(filename, 'r') as f:
                tickers = [line.strip().upper() for line in f if line.strip()]
            
            print(f"📄 Loading tickers from {filename}")
            return self.generate_multiple_stocks(tickers, days)
            
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
            return []
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return []
    
    def create_sample_datasets(self) -> List[str]:
        """Create sample datasets for common use cases"""
        print("🎯 Creating sample datasets for machine learning")
        print("-" * 50)
        
        sample_sets = [
            {
                'name': 'Tech Giants',
                'tickers': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
                'description': 'Major technology companies'
            },
            {
                'name': 'Market Leaders',
                'tickers': ['AAPL', 'MSFT', 'JPM', 'JNJ', 'XOM'],
                'description': 'Leading companies across sectors'
            },
            {
                'name': 'High Volatility',
                'tickers': ['TSLA', 'GME', 'AMC', 'NVDA', 'COIN'],
                'description': 'Stocks with high price volatility'
            }
        ]
        
        all_csv_files = []
        
        for sample_set in sample_sets:
            print(f"\n📊 Creating {sample_set['name']} dataset...")
            print(f"   {sample_set['description']}")
            
            csv_files = self.generate_multiple_stocks(sample_set['tickers'], days=30)
            all_csv_files.extend(csv_files)
        
        return all_csv_files
    
    def _display_file_info(self, csv_file: str):
        """Display information about generated CSV file"""
        if not csv_file or not os.path.exists(csv_file):
            return
        
        try:
            import pandas as pd
            df = pd.read_csv(csv_file)
            
            print(f"✅ Generated: {os.path.basename(csv_file)}")
            print(f"   📊 Records: {len(df)}")
            print(f"   📋 Columns: {len(df.columns)}")
            print(f"   💾 Size: {self._get_file_size(csv_file)}")
            
            # Show key columns for ML
            ml_columns = [col for col in df.columns if any(keyword in col.lower() 
                         for keyword in ['sentiment', 'price', 'volume', 'rsi', 'sma', 'momentum'])]
            
            if ml_columns:
                print(f"   🤖 ML Features: {len(ml_columns)} columns")
                print(f"      Key features: {', '.join(ml_columns[:5])}")
            
            print()
            
        except Exception as e:
            print(f"   ⚠️ Could not analyze file: {e}")
    
    def _get_file_size(self, filepath: str) -> str:
        """Get human-readable file size"""
        try:
            size_bytes = os.path.getsize(filepath)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except:
            return "Unknown"
    
    def display_usage_examples(self):
        """Display usage examples"""
        print("📚 CSV Data Generator - Usage Examples")
        print("=" * 60)
        
        examples = [
            {
                'title': 'Single Stock Analysis',
                'command': 'python generate_csv_data.py AAPL',
                'description': 'Generate comprehensive data for Apple stock'
            },
            {
                'title': 'Multiple Stocks',
                'command': 'python generate_csv_data.py AAPL MSFT GOOGL',
                'description': 'Generate data for multiple stocks'
            },
            {
                'title': 'Extended Timeframe',
                'command': 'python generate_csv_data.py AAPL --days 90',
                'description': 'Generate 90 days of historical data'
            },
            {
                'title': 'Sector Analysis',
                'command': 'python generate_csv_data.py --sector tech',
                'description': 'Generate data for tech sector stocks'
            },
            {
                'title': 'From File',
                'command': 'python generate_csv_data.py --batch my_stocks.txt',
                'description': 'Generate data for stocks listed in file'
            },
            {
                'title': 'Sample datasets',
                'command': 'python generate_csv_data.py --samples',
                'description': 'Create sample datasets for ML experiments'
            }
        ]
        
        for example in examples:
            print(f"\n🔸 {example['title']}")
            print(f"   Command: {example['command']}")
            print(f"   Description: {example['description']}")
        
        print(f"\n📁 Output Directory: {self.exporter.export_directory}")
        print("\n💡 Generated files include:")
        print("   - CSV file with comprehensive stock data")
        print("   - JSON metadata file with column descriptions")
        print("   - Combined dataset when processing multiple stocks")
    
    def display_ml_guide(self):
        """Display machine learning usage guide"""
        print("🤖 Machine Learning Usage Guide")
        print("=" * 50)
        
        print("\n📊 Dataset Features:")
        feature_categories = {
            'Price Data': ['current_price', 'change', 'change_percent', 'volume'],
            'Technical Indicators': ['sma_20', 'sma_50', 'rsi_14', 'price_momentum'],
            'Sentiment Scores': ['combined_sentiment_score', 'news_sentiment_score', 'confidence_score'],
            'Fundamental Data': ['pe_ratio', 'beta', 'market_cap', 'sector'],
            'Market Context': ['vix_level', 'market_condition', 'unemployment_rate'],
            'Derived Features': ['risk_score', 'sentiment_momentum', 'valuation_category']
        }
        
        for category, features in feature_categories.items():
            print(f"\n🔹 {category}:")
            for feature in features:
                print(f"   - {feature}")
        
        print("\n🎯 ML Model Suggestions:")
        
        ml_approaches = [
            {
                'type': 'Price Prediction',
                'target': 'future_price or price_momentum',
                'algorithm': 'Random Forest, XGBoost, LSTM',
                'features': 'Technical indicators + sentiment scores'
            },
            {
                'type': 'Sentiment Classification',
                'target': 'sentiment_label',
                'algorithm': 'SVM, Naive Bayes, Neural Networks',
                'features': 'News data + market context'
            },
            {
                'type': 'Risk Assessment',
                'target': 'risk_score',
                'algorithm': 'Logistic Regression, Ensemble Methods',
                'features': 'Volatility + fundamental + market data'
            },
            {
                'type': 'Time Series Forecasting',
                'target': 'price_series',
                'algorithm': 'ARIMA, Prophet, LSTM',
                'features': 'Historical prices + sentiment trends'
            }
        ]
        
        for approach in ml_approaches:
            print(f"\n🔸 {approach['type']}")
            print(f"   Target: {approach['target']}")
            print(f"   Algorithms: {approach['algorithm']}")
            print(f"   Key Features: {approach['features']}")
        
        print("\n📝 Quick Start Python Code:")
        print("""
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Load your generated CSV
df = pd.read_csv('AAPL_comprehensive_data_YYYYMMDD_HHMMSS.csv')

# Select features for price prediction
features = ['rsi_14', 'combined_sentiment_score', 'volume', 
           'sma_20', 'market_cap', 'vix_level']

X = df[features].fillna(0)
y = df['price_momentum']  # Target variable

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f'Model accuracy: {score:.3f}')
        """)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive stock data CSV files for predictive modeling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_csv_data.py AAPL                    # Single stock
  python generate_csv_data.py AAPL MSFT GOOGL         # Multiple stocks
  python generate_csv_data.py --sector tech           # Tech sector
  python generate_csv_data.py --batch stocks.txt      # From file
  python generate_csv_data.py --samples               # Sample datasets
  python generate_csv_data.py --examples              # Show examples
        """
    )
    
    parser.add_argument('tickers', nargs='*', help='Stock ticker symbols (e.g., AAPL MSFT)')
    parser.add_argument('--days', type=int, default=30, help='Number of days of data (default: 30)')
    parser.add_argument('--sector', choices=['tech', 'finance', 'healthcare', 'energy', 'consumer'],
                       help='Generate data for entire sector')
    parser.add_argument('--batch', help='File containing list of tickers (one per line)')
    parser.add_argument('--samples', action='store_true', help='Create sample datasets')
    parser.add_argument('--examples', action='store_true', help='Show usage examples')
    parser.add_argument('--ml-guide', action='store_true', help='Show ML usage guide')
    parser.add_argument('--no-news', action='store_true', help='Exclude news sentiment data')
    parser.add_argument('--no-technical', action='store_true', help='Exclude technical indicators')
    
    return parser.parse_args()


def main():
    """Main function"""
    args = parse_arguments()
    generator = CSVDataGenerator()
    
    # Handle special actions
    if args.examples:
        generator.display_usage_examples()
        return
    
    if args.ml_guide:
        generator.display_ml_guide()
        return
    
    # Configuration
    include_news = not args.no_news
    include_technical = not args.no_technical
    
    csv_files = []
    
    try:
        # Generate data based on arguments
        if args.samples:
            csv_files = generator.create_sample_datasets()
            
        elif args.sector:
            csv_files = generator.generate_sector_data(args.sector, args.days)
            
        elif args.batch:
            csv_files = generator.generate_from_file(args.batch, args.days)
            
        elif args.tickers:
            if len(args.tickers) == 1:
                csv_file = generator.generate_single_stock(
                    args.tickers[0], args.days, include_news, include_technical
                )
                csv_files = [csv_file] if csv_file else []
            else:
                csv_files = generator.generate_multiple_stocks(args.tickers, args.days)
        else:
            print("❌ No tickers specified. Use --help for usage information.")
            print("💡 Quick start: python generate_csv_data.py AAPL")
            return
        
        # Summary
        successful_files = [f for f in csv_files if f and os.path.exists(f)]
        
        print("\n" + "=" * 60)
        print(f"✅ CSV Generation Complete!")
        print(f"📊 Generated {len(successful_files)} files")
        print(f"📁 Output directory: {generator.exporter.export_directory}")
        
        if successful_files:
            print(f"\n📄 Generated Files:")
            for csv_file in successful_files:
                print(f"  - {os.path.basename(csv_file)}")
            
            print(f"\n🤖 Ready for machine learning!")
            print(f"💡 Use --ml-guide to see ML usage examples")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"💡 Use --help for usage information")


if __name__ == "__main__":
    main()
