import os
import requests
from typing import Optional, Dict, Any

class LinkedInService:
    def __init__(self):
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.base_url = "https://api.linkedin.com/v2"

    def get_person_id(self) -> Optional[str]:
        """Get the LinkedIn person ID for the authenticated user"""
        if not self.access_token:
            return None

        url = f"{self.base_url}/me"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get('id')
            else:
                print("Failed to get person ID: " + str(response.status_code) + " - " + str(response.text))
                return None
        except Exception as e:
            print("Error posting to LinkedIn: " + str(e))
            return None

    def post_content(self, text: str) -> Dict[str, Any]:
        """Post content to LinkedIn"""
        if not self.access_token:
            return {"success": False, "error": "LinkedIn access token not configured"}

        person_id = self.get_person_id()
        if not person_id:
            return {"success": False, "error": "Could not retrieve LinkedIn person ID"}

        url = f"{self.base_url}/shares"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "owner": f"urn:li:person:{person_id}",
            "text": {
                "text": text
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 201:
                return {"success": True, "post_id": response.json().get('id'), "url": response.json().get('activity')}
            else:
                return {"success": False, "error": "LinkedIn API error: " + str(response.status_code) + " - " + str(response.text)}
        except Exception as e:
            return {"success": False, "error": f"Exception during posting: {str(e)}"}

# Singleton instance
linkedin_service = LinkedInService()