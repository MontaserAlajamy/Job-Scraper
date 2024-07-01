from scraper import JobScraper

job_scraper = JobScraper()


def scrape_jobs_thread(keywords, location, days):
    try:
        return job_scraper.scrape_jobs(keywords, location, days)
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []  # return empty list in case of errors

