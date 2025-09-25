import os
from typing import Dict, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('EMAIL_FROM')
        self.to_email = os.getenv('EMAIL_TO')

    def send_email(self, subject: str, content: str) -> Dict[str, Any]:
        """Send an email using SendGrid"""
        if not self.api_key or not self.from_email or not self.to_email:
            return {"success": False, "error": "SendGrid API key, from email, or to email not configured"}

        message = Mail(
            from_email=self.from_email,
            to_emails=self.to_email,
            subject=subject,
            html_content=content
        )

        try:
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            if response.status_code == 202:
                return {"success": True, "message_id": response.headers.get('X-Message-Id')}
            else:
                return {"success": False, "error": f"SendGrid error: {response.status_code} - {response.body}"}
        except Exception as e:
            return {"success": False, "error": f"Exception during email sending: {str(e)}"}

# Singleton instance
email_service = EmailService()