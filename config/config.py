"""
Configuration module for loading environment variables and API keys.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys for Financial Data
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'YOUR_ALPHA_VANTAGE_KEY')
FRED_API_KEY = os.getenv('FRED_API_KEY', 'YOUR_FRED_API_KEY')
MARKETAUX_API_KEY = os.getenv('MARKETAUX_API_KEY', 'YOUR_MARKETAUX_API_KEY')

# API Keys for News and Headlines
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'YOUR_NEWSAPI_KEY')

# API Keys for Social Media Sentiment Analysis
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', 'YOUR_TWITTER_BEARER_TOKEN')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', 'YOUR_TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', 'YOUR_TWITTER_API_SECRET')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', 'YOUR_REDDIT_CLIENT_ID')
REDDIT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', 'YOUR_REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'YOUR_REDDIT_USER_AGENT')

# Additional Social Media APIs
STOCKTWITS_TOKEN = os.getenv('STOCKTWITS_TOKEN', 'YOUR_STOCKTWITS_TOKEN')

# Hugging Face Model Names for Sentiment Analysis
MODEL_NAME = os.getenv('MODEL_NAME', 'ProsusAI/finbert')
GENERAL_MODEL_NAME = os.getenv('GENERAL_MODEL_NAME', 'distilbert-base-uncased-finetuned-sst-2-english')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///investment_data.db')
QUESTDB_HOST = os.getenv('QUESTDB_HOST', 'localhost')
QUESTDB_PORT = os.getenv('QUESTDB_PORT', '9009')

# Other Configuration
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Print configuration status (for debugging)
if DEBUG:
    print("Configuration loaded:")
    print(f"Alpha Vantage API: {'✓' if ALPHA_VANTAGE_KEY != 'YOUR_ALPHA_VANTAGE_KEY' else '✗'}")
    print(f"FRED API: {'✓' if FRED_API_KEY != 'YOUR_FRED_API_KEY' else '✗'}")
    print(f"MarketAux API: {'✓' if MARKETAUX_API_KEY != 'YOUR_MARKETAUX_API_KEY' else '✗'}")
    print(f"News API: {'✓' if NEWS_API_KEY != 'YOUR_NEWSAPI_KEY' else '✗'}")
    print(f"Twitter API: {'✓' if TWITTER_BEARER_TOKEN != 'YOUR_TWITTER_BEARER_TOKEN' else '✗'}")
    print(f"Reddit API: {'✓' if REDDIT_CLIENT_ID != 'YOUR_REDDIT_CLIENT_ID' else '✗'}")
