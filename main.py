import schedule
import time
from datetime import datetime
from core.profile_analyzer import ProfileAnalyzer
from core.job_scraper import JobScraper
from core.job_matcher import JobMatcher
from core.notification import NotificationManager
from config import Config
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInJobBot:
    def __init__(self):
        self.profile_analyzer = ProfileAnalyzer()
        self.job_scraper = JobScraper()
        self.job_matcher = JobMatcher()
        self.notifier = NotificationManager()
        
        self.config = Config()
        self.profile_data = None
        
        # Load or create profile
        self._initialize_profile()
    
    def _initialize_profile(self):
        """Initialize profile data"""
        try:
            with open('data/profile_data.json', 'r') as f:
                self.profile_data = json.load(f)
                logger.info("✅ Profile loaded from storage")
        except:
            logger.info("⚠️ No profile found. Please run setup first.")
    
    def setup_profile(self):
        """Setup profile manually or via LinkedIn"""
        print("\n🔧 LinkedIn Job Bot Setup")
        print("="*50)
        
        # Option 1: Manual entry
        print("\nOption 1: Enter profile details manually")
        profile_data = {
            'headline': input("Headline: "),
            'summary': input("Summary: "),
            'skills': input("Skills (comma separated): ").split(','),
            'experience': []
        }
        
        # Add experience
        num_experiences = int(input("Number of experiences: "))
        for i in range(num_experiences):
            print(f"\nExperience {i+1}:")
            exp = {
                'title': input("  Title: "),
                'company': input("  Company: "),
                'duration': input("  Duration (e.g., 2 years): "),
                'description': input("  Description: ")
            }
            profile_data['experience'].append(exp)
        
        # Analyze profile
        analyzed = self.profile_analyzer.analyze_profile(profile_data)
        self.profile_data = analyzed
        
        logger.info("✅ Profile setup complete!")
        self.show_profile_summary()
        
        return analyzed
    
    def show_profile_summary(self):
        """Display profile summary"""
        if not self.profile_data:
            print("❌ No profile data available")
            return
        
        print("\n📊 PROFILE SUMMARY")
        print("="*50)
        print(f"Field: {self.profile_data.get('field', 'N/A')}")
        print(f"Experience: {self.profile_data.get('experience_years', 0)} years")
        print(f"Strength: {self.profile_data.get('profile_strength', 'N/A')}")
        print(f"Skills: {', '.join(self.profile_data.get('skills', [])[:10])}")
        print("="*50)
    
    def search_and_notify(self):
        """Main function to search jobs and send notifications"""
        try:
            logger.info("🔍 Starting job search...")
            
            # Scrape jobs
            keywords = ['IoT', 'Robotics', 'Embedded Systems', 'Automation']
            jobs = self.job_scraper.scrape_jobs(
                keywords=keywords,
                location='Pakistan'
            )
            
            logger.info(f"📊 Found {len(jobs)} jobs")
            
            if not jobs:
                logger.info("No new jobs found")
                return
            
            # Match with profile
            matched_jobs = self.job_matcher.match_jobs(jobs)
            
            # Filter new jobs (not in history)
            new_jobs = []
            for job, score in matched_jobs:
                if job['url'] not in [h['url'] for h in self.notifier.job_history]:
                    new_jobs.append((job, score))
            
            if new_jobs:
                logger.info(f"📨 Found {len(new_jobs)} new matching jobs")
                self.notifier.send_notification(new_jobs)
            else:
                logger.info("No new matching jobs found")
            
        except Exception as e:
            logger.error(f"❌ Error in search_and_notify: {e}")
    
    def run_once(self):
        """Run the bot once"""
        logger.info("🚀 Running job bot once...")
        self.search_and_notify()
    
    def run_scheduled(self):
        """Run the bot on schedule"""
        logger.info("🔄 Starting scheduled job bot...")
        
        # Schedule job every X hours
        schedule.every(Config.SCRAPE_INTERVAL_HOURS).hours.do(self.search_and_notify)
        
        # Run immediately on start
        self.search_and_notify()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def cleanup(self):
        """Cleanup resources"""
        if self.job_scraper:
            self.job_scraper.close()
        logger.info("🧹 Cleanup complete")

def main():
    """Main entry point"""
    print("\n🤖 LinkedIn Job Bot for IoT/Robotics")
    print("="*50)
    
    bot = LinkedInJobBot()
    
    try:
        while True:
            print("\nMenu:")
            print("1. Setup Profile")
            print("2. Show Profile")
            print("3. Search Jobs (Run Once)")
            print("4. Start Scheduled Monitoring")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ")
            
            if choice == '1':
                bot.setup_profile()
            
            elif choice == '2':
                bot.show_profile_summary()
            
            elif choice == '3':
                bot.run_once()
            
            elif choice == '4':
                bot.run_scheduled()
            
            elif choice == '5':
                print("👋 Goodbye!")
                bot.cleanup()
                break
            
            else:
                print("❌ Invalid option. Please try again.")
    
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        bot.cleanup()

if __name__ == "__main__":
    main()