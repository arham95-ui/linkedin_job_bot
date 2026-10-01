import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LinkedIn Credentials
    LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
    
    # Profile Keywords (IoT/Robotics specific)
    PROFILE_KEYWORDS = [
        'IoT', 'Internet of Things', 'Robotics', 'Embedded Systems',
        'Arduino', 'Raspberry Pi', 'Sensor Networks', 'Automation',
        'Mechatronics', 'Control Systems', 'Machine Learning',
        'Computer Vision', 'ROS', 'Robot Operating System'
    ]
    
    # Job Search Filters
    JOB_FILTERS = {
        'keywords': ['IoT', 'Robotics', 'Embedded', 'Automation'],
        'job_type': ['Full-time', 'Internship'],
        'experience_level': ['Entry level', 'Associate'],
        'remote': ['Remote', 'Hybrid', 'On-site']
    }
    
    # Notification Settings
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    YOUR_PHONE_NUMBER = os.getenv('YOUR_PHONE_NUMBER')
    
    # Database
    DATA_DIR = 'data/'
    PROFILE_FILE = f'{DATA_DIR}profile_data.json'
    JOB_HISTORY_FILE = f'{DATA_DIR}job_history.json'
    
    # Scraping Settings
    SCRAPE_INTERVAL_HOURS = 2
    MAX_JOBS_PER_RUN = 50