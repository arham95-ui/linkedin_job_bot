from twilio.rest import Client
import json
from datetime import datetime
import os

class NotificationManager:
    def __init__(self):
        self.client = self._setup_twilio()
        self.job_history = self._load_history()
    
    def _setup_twilio(self):
        """Setup Twilio client"""
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        if account_sid and auth_token:
            return Client(account_sid, auth_token)
        return None
    
    def _load_history(self) -> list:
        """Load job history from file"""
        try:
            with open('data/job_history.json', 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_history(self):
        """Save job history to file"""
        with open('data/job_history.json', 'w') as f:
            json.dump(self.job_history, f, indent=2)
    
    def send_notification(self, matched_jobs: list):
        """Send notification for matched jobs"""
        if not matched_jobs:
            return
        
        # Format message
        message = self._format_message(matched_jobs)
        
        # Send via Twilio (SMS)
        if self.client:
            try:
                self.client.messages.create(
                    body=message,
                    from_=os.getenv('TWILIO_PHONE_NUMBER'),
                    to=os.getenv('YOUR_PHONE_NUMBER')
                )
                print("✅ SMS notification sent!")
            except Exception as e:
                print(f"❌ Failed to send SMS: {e}")
        
        # Also print to console
        print("\n" + "="*50)
        print("🔔 NEW JOB ALERTS")
        print("="*50)
        print(message)
        
        # Update history
        for job, score in matched_jobs:
            if job['url'] not in [h['url'] for h in self.job_history]:
                self.job_history.append({
                    'url': job['url'],
                    'title': job['title'],
                    'company': job['company'],
                    'notified_at': datetime.now().isoformat()
                })
        
        self._save_history()
    
    def _format_message(self, matched_jobs: list) -> str:
        """Format job notification message"""
        message = "🤖 IoT/Robotics Job Alerts\n\n"
        
        for job, score in matched_jobs[:5]:  # Top 5 matches
            message += f"📌 {job['title']}\n"
            message += f"🏢 {job['company']}\n"
            message += f"📍 {job['location']}\n"
            message += f"🎯 Match: {score:.0f}%\n"
            message += f"🔗 {job['url']}\n\n"
        
        message += f"Total {len(matched_jobs)} matching jobs found!"
        return message