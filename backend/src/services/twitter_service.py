import os
import requests
from typing import Optional, Dict, Any
import base64
import hashlib
import hmac
import time
import urllib.parse

class TwitterService:
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.consumer_key = os.getenv('TWITTER_CONSUMER_KEY')  # If using OAuth 1.0a
        self.consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
        self.base_url = "https://api.twitter.com/2"

    def post_tweet(self, text: str) -> Dict[str, Any]:
        """Post a tweet to Twitter using API v2"""
        if not self.bearer_token:
            return {"success": False, "error": "Twitter Bearer token not configured"}

        url = f"{self.base_url}/tweets"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        payload = {"text": text}

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 201:
                data = response.json()
                return {"success": True, "tweet_id": data.get('data', {}).get('id'), "url": f"https://twitter.com/i/status/{data.get('data', {}).get('id')}"}
            else:
                return {"success": False, "error": f"Twitter API error: {response.status_code} - {response.text}"}
        except Exception as e:
            return {"success": False, "error": f"Exception during tweeting: {str(e)}"}

# Singleton instance
twitter_service = TwitterService()


