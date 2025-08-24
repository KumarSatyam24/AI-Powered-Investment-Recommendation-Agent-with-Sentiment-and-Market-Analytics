import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import MARKETAUX_API_KEY

class MarketAuxAPI:
    """MarketAux API client for financial news and market data."""
    
    BASE_URL = "https://api.marketaux.com/v1"
    
    def __init__(self):
        self.api_key = MARKETAUX_API_KEY
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request to MarketAux."""
        if not self.api_key or self.api_key == "YOUR_MARKETAUX_API_KEY":
            print("MarketAux API key not configured. Using mock data.")
            return None
        
        params['api_token'] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making MarketAux API request: {e}")
            return None
    
    def get_market_news(self, symbols: List[str] = None, limit: int = 10, 
                       languages: str = 'en', filter_entities: bool = True) -> Dict:
        """
        Get latest financial news.
        
        Args:
            symbols: List of stock symbols to filter news (e.g., ['AAPL', 'TSLA'])
            limit: Number of articles to retrieve (max 100)
            languages: Language code (default: 'en')
            filter_entities: Whether to filter by entity relevance
        """
        params = {
            'limit': min(limit, 100),
            'language': languages,
            'filter_entities': str(filter_entities).lower()
        }
        
        if symbols:
            params['symbols'] = ','.join(symbols)
        
        data = self._make_request('news/all', params)
        if not data:
            return self._get_mock_news(symbols)
        
        try:
            articles = data.get('data', [])
            processed_articles = []
            
            for article in articles:
                processed_article = {
                    'uuid': article.get('uuid'),
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'snippet': article.get('snippet'),
                    'url': article.get('url'),
                    'image_url': article.get('image_url'),
                    'language': article.get('language'),
                    'published_at': article.get('published_at'),
                    'source': article.get('source'),
                    'relevance_score': article.get('relevance_score'),
                    'entities': self._process_entities(article.get('entities', [])),
                    'similar_articles': len(article.get('similar', [])),
                    'sentiment': self._extract_sentiment(article)
                }
                processed_articles.append(processed_article)
            
            return {
                'data': processed_articles,
                'meta': data.get('meta', {}),
                'total_articles': len(processed_articles),
                'symbols_mentioned': self._get_mentioned_symbols(processed_articles),
                'sentiment_summary': self._analyze_sentiment_summary(processed_articles)
            }
        except Exception as e:
            print(f"Error processing MarketAux news data: {e}")
            return self._get_mock_news(symbols)
    
    def get_news_by_symbol(self, symbol: str, limit: int = 20) -> Dict:
        """Get news specifically for a stock symbol."""
        return self.get_market_news(symbols=[symbol], limit=limit)
    
    def get_trending_news(self, limit: int = 15) -> Dict:
        """Get trending financial news without symbol filtering."""
        return self.get_market_news(symbols=None, limit=limit)
    
    def get_news_sentiment_analysis(self, symbols: List[str], days: int = 7) -> Dict:
        """
        Get sentiment analysis for news about specific symbols over a time period.
        
        Args:
            symbols: List of stock symbols
            days: Number of days to look back
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'symbols': ','.join(symbols),
            'published_after': start_date.strftime('%Y-%m-%dT00:00:00'),
            'published_before': end_date.strftime('%Y-%m-%dT23:59:59'),
            'limit': 100,
            'language': 'en',
            'filter_entities': 'true'
        }
        
        data = self._make_request('news/all', params)
        if not data:
            return self._get_mock_sentiment_analysis(symbols)
        
        try:
            articles = data.get('data', [])
            
            # Analyze sentiment
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            symbol_sentiments = {symbol: {'positive': 0, 'negative': 0, 'neutral': 0} 
                               for symbol in symbols}
            
            for article in articles:
                sentiment = self._extract_sentiment(article)
                sentiment_counts[sentiment] += 1
                
                # Count sentiment per symbol mentioned in entities
                for entity in article.get('entities', []):
                    if entity.get('symbol') in symbols:
                        symbol_sentiments[entity['symbol']][sentiment] += 1
            
            total_articles = len(articles)
            overall_sentiment = self._calculate_overall_sentiment(sentiment_counts)
            
            return {
                'symbols': symbols,
                'period_days': days,
                'total_articles': total_articles,
                'overall_sentiment': overall_sentiment,
                'sentiment_distribution': {
                    'positive': sentiment_counts['positive'] / max(total_articles, 1) * 100,
                    'negative': sentiment_counts['negative'] / max(total_articles, 1) * 100,
                    'neutral': sentiment_counts['neutral'] / max(total_articles, 1) * 100
                },
                'symbol_sentiments': symbol_sentiments,
                'articles': articles[:10]  # Sample articles
            }
        except Exception as e:
            print(f"Error analyzing news sentiment: {e}")
            return self._get_mock_sentiment_analysis(symbols)
    
    def get_market_movers_news(self, limit: int = 20) -> Dict:
        """Get news about market movers and trending stocks."""
        params = {
            'limit': limit,
            'language': 'en',
            'must_have_entities': 'true',
            'filter_entities': 'true'
        }
        
        data = self._make_request('news/all', params)
        if not data:
            return self._get_mock_movers_news()
        
        try:
            articles = data.get('data', [])
            
            # Extract stocks mentioned most frequently
            symbol_mentions = {}
            for article in articles:
                for entity in article.get('entities', []):
                    if entity.get('symbol'):
                        symbol = entity['symbol']
                        if symbol not in symbol_mentions:
                            symbol_mentions[symbol] = {
                                'count': 0,
                                'sentiment_scores': [],
                                'articles': []
                            }
                        symbol_mentions[symbol]['count'] += 1
                        symbol_mentions[symbol]['articles'].append(article.get('title'))
                        
                        # Add sentiment if available
                        sentiment = self._extract_sentiment(article)
                        sentiment_score = 1 if sentiment == 'positive' else -1 if sentiment == 'negative' else 0
                        symbol_mentions[symbol]['sentiment_scores'].append(sentiment_score)
            
            # Sort by mention count
            trending_symbols = sorted(symbol_mentions.items(), 
                                    key=lambda x: x[1]['count'], reverse=True)[:10]
            
            return {
                'trending_symbols': [
                    {
                        'symbol': symbol,
                        'mention_count': data['count'],
                        'avg_sentiment': sum(data['sentiment_scores']) / len(data['sentiment_scores']) 
                                       if data['sentiment_scores'] else 0,
                        'sample_headlines': data['articles'][:3]
                    }
                    for symbol, data in trending_symbols
                ],
                'total_articles_analyzed': len(articles),
                'raw_articles': articles[:5]  # Sample raw articles
            }
        except Exception as e:
            print(f"Error processing market movers news: {e}")
            return self._get_mock_movers_news()
    
    def _process_entities(self, entities: List[Dict]) -> List[Dict]:
        """Process and clean entity data."""
        processed = []
        for entity in entities:
            processed.append({
                'symbol': entity.get('symbol'),
                'name': entity.get('name'),
                'exchange': entity.get('exchange'),
                'country': entity.get('country'),
                'type': entity.get('type'),
                'industry': entity.get('industry'),
                'match_score': entity.get('match_score')
            })
        return processed
    
    def _extract_sentiment(self, article: Dict) -> str:
        """Extract or infer sentiment from article."""
        # MarketAux doesn't always provide sentiment, so we'll use simple keyword analysis
        title = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        
        positive_keywords = ['gain', 'rise', 'up', 'bull', 'surge', 'rally', 'boost', 'strong', 
                           'growth', 'profit', 'beat', 'upgrade', 'positive', 'soar']
        negative_keywords = ['fall', 'drop', 'down', 'bear', 'crash', 'decline', 'loss', 'weak',
                           'cut', 'miss', 'downgrade', 'negative', 'plunge', 'sell']
        
        positive_count = sum(1 for word in positive_keywords if word in title)
        negative_count = sum(1 for word in negative_keywords if word in title)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _get_mentioned_symbols(self, articles: List[Dict]) -> List[str]:
        """Extract unique symbols mentioned across articles."""
        symbols = set()
        for article in articles:
            for entity in article.get('entities', []):
                if entity.get('symbol'):
                    symbols.add(entity['symbol'])
        return list(symbols)
    
    def _analyze_sentiment_summary(self, articles: List[Dict]) -> Dict:
        """Analyze overall sentiment distribution."""
        sentiments = [article.get('sentiment', 'neutral') for article in articles]
        total = len(sentiments)
        
        if total == 0:
            return {'positive': 0, 'negative': 0, 'neutral': 0}
        
        return {
            'positive': sentiments.count('positive') / total * 100,
            'negative': sentiments.count('negative') / total * 100,
            'neutral': sentiments.count('neutral') / total * 100
        }
    
    def _calculate_overall_sentiment(self, sentiment_counts: Dict) -> str:
        """Calculate overall market sentiment."""
        total = sum(sentiment_counts.values())
        if total == 0:
            return 'neutral'
        
        positive_pct = sentiment_counts['positive'] / total
        negative_pct = sentiment_counts['negative'] / total
        
        if positive_pct > 0.6:
            return 'bullish'
        elif negative_pct > 0.6:
            return 'bearish'
        elif positive_pct > negative_pct:
            return 'slightly_positive'
        elif negative_pct > positive_pct:
            return 'slightly_negative'
        else:
            return 'neutral'
    
    def _get_mock_news(self, symbols: List[str] = None) -> Dict:
        """Return mock news data when API is not available."""
        mock_articles = [
            {
                'title': 'Market rallies on positive economic data',
                'description': 'Stocks surge as inflation data comes in better than expected',
                'sentiment': 'positive',
                'entities': [{'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF'}] if not symbols else [{'symbol': symbols[0]}],
                'published_at': '2025-08-25T10:00:00Z'
            },
            {
                'title': 'Tech stocks face headwinds from regulatory concerns',
                'description': 'Technology sector under pressure from new regulations',
                'sentiment': 'negative',
                'entities': [{'symbol': 'AAPL', 'name': 'Apple Inc.'}],
                'published_at': '2025-08-25T09:00:00Z'
            }
        ]
        
        return {
            'data': mock_articles,
            'total_articles': len(mock_articles),
            'symbols_mentioned': symbols or ['SPY', 'AAPL'],
            'sentiment_summary': {'positive': 50.0, 'negative': 50.0, 'neutral': 0.0}
        }
    
    def _get_mock_sentiment_analysis(self, symbols: List[str]) -> Dict:
        """Return mock sentiment analysis when API is not available."""
        return {
            'symbols': symbols,
            'period_days': 7,
            'total_articles': 10,
            'overall_sentiment': 'slightly_positive',
            'sentiment_distribution': {'positive': 45.0, 'negative': 35.0, 'neutral': 20.0},
            'symbol_sentiments': {symbol: {'positive': 3, 'negative': 2, 'neutral': 1} for symbol in symbols}
        }
    
    def _get_mock_movers_news(self) -> Dict:
        """Return mock market movers news when API is not available."""
        return {
            'trending_symbols': [
                {
                    'symbol': 'TSLA',
                    'mention_count': 5,
                    'avg_sentiment': 0.2,
                    'sample_headlines': ['Tesla reports strong Q3 earnings', 'TSLA stock jumps on delivery numbers']
                },
                {
                    'symbol': 'AAPL',
                    'mention_count': 4,
                    'avg_sentiment': -0.1,
                    'sample_headlines': ['Apple faces iPhone sales pressure', 'AAPL dividend announcement']
                }
            ],
            'total_articles_analyzed': 20
        }

# Global instance
marketaux_api = MarketAuxAPI()
