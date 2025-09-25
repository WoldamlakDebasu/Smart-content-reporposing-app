import os
import requests
from typing import Optional, Dict, Any

class FacebookService:
    def __init__(self):
        self.page_access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.base_url = "https://graph.facebook.com/v18.0"

    def post_to_page(self, message: str) -> Dict[str, Any]:
        """Post a message to Facebook page"""
        if not self.page_access_token or not self.page_id:
            return {"success": False, "error": "Facebook Page Access Token or Page ID not configured"}

        url = f"{self.base_url}/{self.page_id}/feed"
        params = {
            "message": message,
            "access_token": self.page_access_token
        }

        try:
            response = requests.post(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "post_id": data.get('id'), "url": f"https://www.facebook.com/{data.get('id')}"}
            else:
                return {"success": False, "error": f"Facebook API error: {response.status_code} - {response.text}"}
        except Exception as e:
            return {"success": False, "error": f"Exception during posting: {str(e)}"}

# Singleton instance
facebook_service = FacebookService()