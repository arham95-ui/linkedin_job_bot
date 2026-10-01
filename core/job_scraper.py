from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict

class JobScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with headless mode"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def login_linkedin(self, email: str, password: str):
        """Login to LinkedIn"""
        try:
            self.driver.get('https://www.linkedin.com/login')
            
            # Enter email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            email_field.send_keys(email)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, 'password')
            password_field.send_keys(password)
            
            # Click login
            login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            login_button.click()
            
            time.sleep(3)
            print("✅ LinkedIn login successful!")
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
    
    def scrape_jobs(self, keywords: List[str], location: str = 'Pakistan') -> List[Dict]:
        """Scrape jobs from LinkedIn"""
        jobs = []
        
        for keyword in keywords:
            url = self._build_search_url(keyword, location)
            self.driver.get(url)
            time.sleep(3)
            
            # Scroll to load more jobs
            self._scroll_page()
            
            # Get job listings
            job_cards = self.driver.find_elements(By.CLASS_NAME, 'job-card-container')
            
            for card in job_cards[:20]:  # Limit per keyword
                try:
                    job_data = self._extract_job_data(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    print(f"Error extracting job: {e}")
                    continue
        
        return jobs
    
    def _build_search_url(self, keyword: str, location: str) -> str:
        """Build LinkedIn job search URL"""
        base_url = 'https://www.linkedin.com/jobs/search/'
        params = {
            'keywords': keyword,
            'location': location,
            'f_TPR': 'r604800',  # Last 7 days
            'f_E': '1,2',  # Entry level, Associate
        }
        
        url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        return url
    
    def _scroll_page(self):
        """Scroll the page to load more jobs"""
        for _ in range(3):
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(1)
    
    def _extract_job_data(self, card) -> Dict:
        """Extract job data from card element"""
        try:
            # Get job title
            title_elem = card.find_element(By.CLASS_NAME, 'job-card-list__title')
            title = title_elem.text.strip()
            
            # Get company name
            company_elem = card.find_element(By.CLASS_NAME, 'job-card-container__company-name')
            company = company_elem.text.strip()
            
            # Get location
            location_elem = card.find_element(By.CLASS_NAME, 'job-card-container__metadata-item')
            location = location_elem.text.strip()
            
            # Get job link
            link_elem = card.find_element(By.TAG_NAME, 'a')
            job_url = link_elem.get_attribute('href')
            
            # Get posted time
            time_elem = card.find_element(By.TAG_NAME, 'time')
            posted_time = time_elem.text.strip()
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'url': job_url,
                'posted_time': posted_time,
                'keywords': self._extract_keywords(title)
            }
            
        except Exception as e:
            print(f"Error extracting job data: {e}")
            return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from job title"""
        keywords = []
        iot_robotics_keywords = [
            'IoT', 'Robotics', 'Embedded', 'Automation',
            'Engineer', 'Developer', 'Intern', 'Trainee',
            'Mechatronics', 'Control', 'Systems'
        ]
        
        for keyword in iot_robotics_keywords:
            if keyword.lower() in text.lower():
                keywords.append(keyword)
        
        return keywords
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()