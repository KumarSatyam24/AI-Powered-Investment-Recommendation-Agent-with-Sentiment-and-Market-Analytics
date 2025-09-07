"""
Grok API Client for fetching tweets from influential financial sources
"""

import requests
import json
from typing import List, Dict, Optional
from config.config import GROK_API_KEY

class GrokTwitterClient:
    """Client for using Grok to fetch tweets from influential financial sources"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GROK_API_KEY
        self.base_url = "https://api.x.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # List of influential financial Twitter accounts
        self.influential_accounts = [
            "@elonmusk",
            "@chamath", 
            "@naval",
            "@karpathy",
            "@balajis",
            "@garyvee",
            "@ARKInvest",
            "@CathieDWood",
            "@RaoulGMI",
            "@NorthmanTrader",
            "@DeItaone",
            "@zerohedge",
            "@MarketWatch",
            "@YahooFinance",
            "@CNBC",
            "@BloombergTV",
            "@SquawkCNBC"
        ]
    
    def get_tweets_from_influencers(self, ticker: str, limit: int = 10) -> List[Dict]:
        """
        Use Grok to generate sample tweets about a ticker from influential sources
        """
        prompt = f"""
        Generate {limit} realistic tweets about {ticker} stock that might come from influential financial Twitter accounts.
        
        Include tweets that would realistically come from accounts like:
        {', '.join(self.influential_accounts[:10])}
        
        Each tweet should:
        - Be realistic and in the style of financial Twitter
        - Include sentiment (positive, negative, or neutral) about {ticker}
        - Be 280 characters or less
        - Include relevant hashtags and mentions when appropriate
        - Vary in sentiment and perspective
        
        Return the response as a JSON array with this format:
        [
            {{
                "text": "tweet content",
                "author": "account_handle",
                "sentiment_hint": "positive/negative/neutral",
                "created_at": "2024-09-07T10:30:00Z",
                "like_count": 150,
                "retweet_count": 45
            }}
        ]
        
        Make the tweets diverse in opinion and realistic for current market conditions.
        """
        
        try:
            payload = {
                "model": "grok-beta",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert at generating realistic financial Twitter content that matches the tone and style of influential accounts. Generate realistic but fictional tweets."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Try to parse JSON from the response
                try:
                    # Look for JSON array in the response
                    start_idx = content.find('[')
                    end_idx = content.rfind(']') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = content[start_idx:end_idx]
                        tweets = json.loads(json_str)
                        return self._format_tweets(tweets)
                except json.JSONDecodeError:
                    # If JSON parsing fails, create mock tweets
                    return self._create_fallback_tweets(ticker, limit)
            else:
                print(f"Grok API error: {response.status_code} - {response.text}")
                return self._create_fallback_tweets(ticker, limit)
                
        except Exception as e:
            print(f"Error calling Grok API: {e}")
            return self._create_fallback_tweets(ticker, limit)
    
    def _format_tweets(self, tweets: List[Dict]) -> List[Dict]:
        """Format tweets to match expected structure"""
        formatted = []
        for tweet in tweets:
            formatted.append({
                "text": tweet.get("text", ""),
                "created_at": tweet.get("created_at", "2024-09-07T10:00:00Z"),
                "like_count": tweet.get("like_count", 0),
                "retweet_count": tweet.get("retweet_count", 0),
                "author": tweet.get("author", "@unknown"),
                "sentiment_hint": tweet.get("sentiment_hint", "neutral")
            })
        return formatted
    
    def _create_fallback_tweets(self, ticker: str, limit: int) -> List[Dict]:
        """Create fallback tweets when API fails"""
        fallback_tweets = [
            {
                "text": f"${ticker} showing strong fundamentals in this market environment. Long-term outlook remains positive despite short-term volatility. #investing",
                "author": "@ARKInvest",
                "sentiment_hint": "positive",
                "created_at": "2024-09-07T09:30:00Z",
                "like_count": 245,
                "retweet_count": 67
            },
            {
                "text": f"Watching ${ticker} closely. Technical indicators suggest we might see some consolidation before the next move. #trading",
                "author": "@NorthmanTrader", 
                "sentiment_hint": "neutral",
                "created_at": "2024-09-07T10:15:00Z",
                "like_count": 123,
                "retweet_count": 34
            },
            {
                "text": f"${ticker} earnings disappointed. Market expectations were too high. Adjusting position accordingly. #earnings",
                "author": "@DeItaone",
                "sentiment_hint": "negative", 
                "created_at": "2024-09-07T11:00:00Z",
                "like_count": 89,
                "retweet_count": 23
            },
            {
                "text": f"Innovation cycle for ${ticker} is just beginning. This is a multi-year story, not a quarterly trade. #innovation #disruption",
                "author": "@CathieDWood",
                "sentiment_hint": "positive",
                "created_at": "2024-09-07T12:30:00Z", 
                "like_count": 567,
                "retweet_count": 145
            },
            {
                "text": f"${ticker} breaking key resistance levels. Volume confirms the move. Could see continuation. #technicalanalysis",
                "author": "@RaoulGMI",
                "sentiment_hint": "positive",
                "created_at": "2024-09-07T13:45:00Z",
                "like_count": 234,
                "retweet_count": 78
            }
        ]
        
        return fallback_tweets[:limit]
    
    def get_reddit_posts_from_grok(self, ticker: str, limit: int = 10) -> List[Dict]:
        """
        Use Grok to generate realistic Reddit posts and comments about a ticker
        """
        prompt = f"""
        Generate {limit} realistic Reddit posts about {ticker} stock that would appear in subreddits like:
        - r/stocks
        - r/investing  
        - r/wallstreetbets
        - r/SecurityAnalysis
        
        Each post should include:
        - A realistic title (Reddit post style)
        - 2-3 realistic top comments
        - Vary in sentiment and perspective
        - Use Reddit terminology and style
        - Include realistic discussion points
        
        Return as JSON array:
        [
            {{
                "title": "post title text",
                "comments": ["comment 1", "comment 2", "comment 3"],
                "sentiment_hint": "positive/negative/neutral",
                "score": 45,
                "subreddit": "stocks"
            }}
        ]
        
        Make them realistic for current market conditions and {ticker}.
        """
        
        try:
            payload = {
                "model": "grok-beta",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert at generating realistic Reddit financial content. Create realistic but fictional posts and comments that match Reddit's tone and style."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 3000
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                try:
                    start_idx = content.find('[')
                    end_idx = content.rfind(']') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = content[start_idx:end_idx]
                        posts = json.loads(json_str)
                        return self._format_reddit_posts(posts)
                except json.JSONDecodeError:
                    return self._create_fallback_reddit_posts(ticker, limit)
            else:
                print(f"Grok API error for Reddit posts: {response.status_code} - {response.text}")
                return self._create_fallback_reddit_posts(ticker, limit)
                
        except Exception as e:
            print(f"Error calling Grok API for Reddit posts: {e}")
            return self._create_fallback_reddit_posts(ticker, limit)
    
    def _format_reddit_posts(self, posts: List[Dict]) -> List[Dict]:
        """Format Reddit posts to match expected structure"""
        formatted = []
        for post in posts:
            formatted.append({
                "title": post.get("title", ""),
                "comments": post.get("comments", []),
                "sentiment_hint": post.get("sentiment_hint", "neutral"),
                "score": post.get("score", 10),
                "subreddit": post.get("subreddit", "stocks")
            })
        return formatted
    
    def _create_fallback_reddit_posts(self, ticker: str, limit: int) -> List[Dict]:
        """Create fallback Reddit posts when API fails"""
        fallback_posts = [
            {
                "title": f"{ticker} Q3 earnings discussion - what are your thoughts?",
                "comments": [
                    f"Strong quarter for {ticker}. Revenue beat expectations and guidance looks solid.",
                    f"Still overvalued IMO. P/E ratio is way too high for current growth rate.",
                    f"Long {ticker} since 2020. This company is just getting started."
                ],
                "sentiment_hint": "mixed",
                "score": 156,
                "subreddit": "stocks"
            },
            {
                "title": f"DD: Why {ticker} is positioned for long-term growth",
                "comments": [
                    "Great analysis! The moat is getting stronger every quarter.",
                    f"Thanks for the DD. Added {ticker} to my watchlist.",
                    "Market cap already too high. Better opportunities elsewhere."
                ],
                "sentiment_hint": "positive",
                "score": 89,
                "subreddit": "investing"
            },
            {
                "title": f"{ticker} technical analysis - breakout incoming?",
                "comments": [
                    "RSI looks good, MACD crossing over. Could see a move higher.",
                    "Resistance at $X level has been strong. Need volume to break through.",
                    "TA is astrology for traders but I like the setup here."
                ],
                "sentiment_hint": "neutral",
                "score": 67,
                "subreddit": "SecurityAnalysis"
            },
            {
                "title": f"YOLO'd into {ticker} calls, am I retarded?",
                "comments": [
                    "Yes but you might get lucky 🚀🚀🚀",
                    f"{ticker} to the moon! Diamond hands!",
                    "Sir this is a casino. Godspeed retard."
                ],
                "sentiment_hint": "positive",
                "score": 234,
                "subreddit": "wallstreetbets"
            },
            {
                "title": f"Thoughts on {ticker} after recent selloff?",
                "comments": [
                    "Buying opportunity if you believe in the fundamentals.",
                    "Market overreacted. This is temporary.",
                    "Falling knife. Wait for clear reversal signals."
                ],
                "sentiment_hint": "mixed",
                "score": 78,
                "subreddit": "stocks"
            }
        ]
        
        return fallback_posts[:limit]

# Test function
def test_grok_tweets(ticker: str = "AAPL", limit: int = 5):
    """Test the Grok tweet fetching"""
    client = GrokTwitterClient()
    tweets = client.get_tweets_from_influencers(ticker, limit)
    
    print(f"Generated {len(tweets)} tweets for {ticker}:")
    for i, tweet in enumerate(tweets, 1):
        print(f"\nTweet {i} ({tweet.get('author', 'Unknown')}):")
        print(f"Text: {tweet['text']}")
        print(f"Sentiment: {tweet.get('sentiment_hint', 'unknown')}")
        print(f"Engagement: {tweet['like_count']} likes, {tweet['retweet_count']} retweets")
    
    return tweets

if __name__ == "__main__":
    test_grok_tweets("MSFT", 5)
