import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from datetime import datetime, timedelta
import time
import random

class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_page(self, url):
        try:
            print(f"Fetching URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            print(f"Successfully fetched {url}")
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_linkedin_jobs(self, html, time_filter):
        soup = BeautifulSoup(html, "html.parser")
        job_cards = soup.find_all("div", class_="base-card")
        
        print(f"Found {len(job_cards)} LinkedIn job cards")
        
        jobs = []
        for card in job_cards:
            title_elem = card.find("h3", class_="base-search-card__title")
            company_elem = card.find("h4", class_="base-search-card__subtitle")
            location_elem = card.find("span", class_="job-search-card__location")
            link_elem = card.find("a", class_="base-card__full-link")
            time_elem = card.find("time", class_="job-search-card__listdate")
            
            if all([title_elem, company_elem, location_elem, link_elem]):
                post_time = time_elem['datetime'] if time_elem else None
                if self.is_within_time_filter(post_time, time_filter):
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "company": company_elem.text.strip(),
                        "location": location_elem.text.strip(),
                        "url": link_elem['href'],
                        "source": "LinkedIn",
                        "date_posted": post_time,
                        "date_scraped": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        print(f"Extracted {len(jobs)} LinkedIn jobs")
        return jobs

    def extract_indeed_jobs(self, html, time_filter):
        soup = BeautifulSoup(html, "html.parser")
        job_cards = soup.find_all("div", class_="job_seen_beacon")
        
        print(f"Found {len(job_cards)} Indeed job cards")
        
        jobs = []
        for card in job_cards:
            title_elem = card.find("h2", class_="jobTitle")
            company_elem = card.find("span", class_="companyName")
            location_elem = card.find("div", class_="companyLocation")
            link_elem = card.find("a", class_="jcs-JobTitle")
            time_elem = card.find("span", class_="date")
            
            if all([title_elem, link_elem]):
                post_time = time_elem.text if time_elem else None
                if self.is_within_time_filter(post_time, time_filter):
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "company": company_elem.text.strip() if company_elem else "N/A",
                        "location": location_elem.text.strip() if location_elem else "N/A",
                        "url": "https://ae.indeed.com" + link_elem['href'] if link_elem['href'].startswith('/') else link_elem['href'],
                        "source": "Indeed",
                        "date_posted": post_time,
                        "date_scraped": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        print(f"Extracted {len(jobs)} Indeed jobs")
        return jobs

    def extract_bayt_jobs(self, html, time_filter):
        soup = BeautifulSoup(html, "html.parser")
        job_cards = soup.find_all("li", class_="has-pointer-d")
        
        print(f"Found {len(job_cards)} Bayt job cards")
        
        jobs = []
        for card in job_cards:
            title_elem = card.find("h2", class_="m0")
            company_elem = card.find("b", class_="jb-company")
            location_elem = card.find("span", class_="jb-loc")
            link_elem = card.find("a", class_="job-title")
            time_elem = card.find("div", class_="io-timestamp-label")            
            if all([title_elem, link_elem]):
                post_time = time_elem.text if time_elem else None
                if self.is_within_time_filter(post_time, time_filter):
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "company": company_elem.text.strip() if company_elem else "N/A",
                        "location": location_elem.text.strip() if location_elem else "N/A",
                        "url": "https://www.bayt.com" + link_elem['href'],
                        "source": "Bayt",
                        "date_posted": post_time,
                        "date_scraped": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        print(f"Extracted {len(jobs)} Bayt jobs")
        return jobs

    def is_within_time_filter(self, post_time, time_filter):
        if time_filter == 'any' or not post_time:
            return True
        
        current_time = datetime.now()
        if isinstance(post_time, str):
            try:
                post_time = datetime.strptime(post_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                # If parsing fails, assume it's a relative time string (e.g., "2 hours ago")
                if "hour" in post_time.lower():
                    hours = int(post_time.split()[0])
                    post_time = current_time - timedelta(hours=hours)
                elif "day" in post_time.lower():
                    days = int(post_time.split()[0])
                    post_time = current_time - timedelta(days=days)
                else:
                    # If we can't parse the time, assume it's within the filter
                    return True

        time_diff = current_time - post_time
        
        if time_filter == 'halfhour':
            return time_diff <= timedelta(minutes=30)
        elif time_filter == 'hour':
            return time_diff <= timedelta(hours=1)
        elif time_filter == 'day':
            return time_diff <= timedelta(days=1)
        elif time_filter == 'week':
            return time_diff <= timedelta(weeks=1)
        elif time_filter == 'month':
            return time_diff <= timedelta(days=30)
        
        return True
    def scrape_jobs(self, keywords, location, time_filter='any'):
        linkedin_url = "https://www.linkedin.com/jobs/search/?" + urlencode({
            "keywords": keywords,
            "location": location,
            "f_TPR": "r86400",  # Last 24 hours
            "f_JT": "F",
        })

        indeed_url = "https://ae.indeed.com/jobs?" + urlencode({
            "q": keywords,
            "l": location,
            "fromage": "1",  # Last 24 hours
        })

        bayt_url = "https://www.bayt.com/en/uae/jobs/?" + urlencode({
            "keyword": keywords,
            "location": location,
        })

        jobs = []

        print("Fetching LinkedIn jobs...")
        linkedin_html = self.fetch_page(linkedin_url)
        if linkedin_html:
            jobs.extend(self.extract_linkedin_jobs(linkedin_html, time_filter))
        else:
            print("Failed to fetch LinkedIn jobs.")

        time.sleep(random.uniform(1, 3))  # Random delay between requests

        print("\nFetching Indeed jobs...")
        indeed_html = self.fetch_page(indeed_url)
        if indeed_html:
            jobs.extend(self.extract_indeed_jobs(indeed_html, time_filter))
        else:
            print("Failed to fetch Indeed jobs.")

        time.sleep(random.uniform(1, 3))  # Random delay between requests

        print("\nFetching Bayt jobs...")
        bayt_html = self.fetch_page(bayt_url)
        if bayt_html:
            jobs.extend(self.extract_bayt_jobs(bayt_html, time_filter))
        else:
            print("Failed to fetch Bayt jobs.")

        # Filter jobs based on time_filter
        filtered_jobs = [job for job in jobs if self.is_within_time_filter(job['date_posted'], time_filter)]

        print(f"Found {len(filtered_jobs)} total jobs after time filtering")
        return filtered_jobs

    def is_within_time_filter(self, post_time, time_filter):
        if time_filter == 'any' or not post_time:
            return True
        
        current_time = datetime.now()
        if isinstance(post_time, str):
            try:
                post_time = datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # If parsing fails, assume it's a relative time string (e.g., "2 hours ago")
                if "minute" in post_time.lower() or "hour" in post_time.lower():
                    time_parts = post_time.split()
                    amount = int(time_parts[0])
                    unit = time_parts[1].lower()
                    if "minute" in unit:
                        post_time = current_time - timedelta(minutes=amount)
                    elif "hour" in unit:
                        post_time = current_time - timedelta(hours=amount)
                else:
                    # If we can't parse the time, assume it's within the filter
                    return True

        time_diff = current_time - post_time
        
        if time_filter == 'halfhour':
            return time_diff <= timedelta(minutes=30)
        elif time_filter == 'hour':
            return time_diff <= timedelta(hours=1)
        elif time_filter == 'day':
            return time_diff <= timedelta(days=1)
        elif time_filter == 'week':
            return time_diff <= timedelta(weeks=1)
        elif time_filter == 'month':
            return time_diff <= timedelta(days=30)
        
        return True