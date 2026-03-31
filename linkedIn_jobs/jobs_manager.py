from wsgiref import headers

import requests
from bs4 import BeautifulSoup
import re
import time
from linkedIn_jobs.models import Company, Job, JobRawData
from utils.commonUtils import get_object_size
import logging
from linkedIn_jobs.utils import requests_with_retry

jobs_logger = logging.getLogger('JobsHandler')


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

class JobsManager:
    BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    JOB_DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/"

    def __init__(self, source):
        self.source = source
        self.total_created = 0
        self.total_skipped = 0
        self.session = requests.session()
        self.session.headers.update(HEADERS)
        jobs_logger.info(f'Jobs ingestion started for {source}')

    def extract_company_slug(self, url):
        if not url:
            return None

        match = re.search(r'/company/([^/?]+)', url)
        if match:
            return match.group(1)

        return None


    def parse_job_cards(self, html):
        soup = BeautifulSoup(html, "lxml")
        cards = soup.find_all("div", class_="base-search-card")

        jobs = []

        for card in cards:
            urn = card.get("data-entity-urn")
            job_id = urn.split(":")[-1] if urn else None

            title = card.find("h3", class_="base-search-card__title")
            title = title.text.strip() if title else None

            company_tag = card.find("h4", class_="base-search-card__subtitle")

            company_name = None
            company_url = None
            company_slug = None

            if company_tag:
                link = company_tag.find("a")

                if link:
                    company_name = link.text.strip()
                    company_url = link.get("href")
                    company_slug = self.extract_company_slug(company_url)

            location_tag = card.find("span", class_="job-search-card__location")
            location = location_tag.text.strip() if location_tag else None

            job_link = card.find("a", class_="base-card__full-link")
            job_url = job_link.get("href") if job_link else None

            jobs.append({
                "job_id": job_id,
                "title": title,
                "company_name": company_name,
                "company_slug": company_slug,
                "company_url": company_url,
                "location": location,
                "job_url": job_url
            })

        return jobs


    def get_job_description(self, job_id):
        url = self.JOB_DETAIL_URL + str(job_id)

        r = self.session.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(r.text, "lxml")
        desc = soup.find("div", class_="show-more-less-html__markup")

        if desc:
            return desc.get_text("\n").strip()

        return None


    def scrape_jobs(self, *args, **kwargs):
        location = kwargs.get("location", "India")
        pages = kwargs.get("pages", 1)
        f_TPR = kwargs.get("f_TPR", None)

        for page in range(pages):
            all_jobs = []
            start = page * 25
            params = {
                "location": location,
                "start": start,
                "f_TPR": f_TPR
            }

            jobs_logger.info(f'Started fetching data from URL for page {start}:- {self.BASE_URL}')
            for attempt in range(5):
                r = self.session.get(self.BASE_URL, params=params, timeout=30)

                if r.status_code == 429:
                    wait = 20 * (attempt + 1)
                    jobs_logger.warning(f"Rate limited. Sleeping {wait}s")
                    time.sleep(wait)
                    continue

                break
            jobs_logger.info(f'Response of the URL:- {r.status_code}')

            if r.status_code != 200:
                print(f'Fetching data from URL failed:- {self.BASE_URL}, {r.text}')
                raise Exception(f'Fetching data from URL failed:- {self.BASE_URL}, {r.text}')

            jobs = self.parse_job_cards(r.text)
            jobs_logger.info(f'Job cards parsed successfully')

            job_raw_data = JobRawData.objects.create(raw_html=r.content)
            jobs_logger.info(f'Job raw data created successfully:- {job_raw_data.pk}')

            for job in jobs:
                job['raw_data_id'] = job_raw_data.id
                if job["job_id"]:
                    job["description"] = self.get_job_description(job["job_id"])

                all_jobs.append(job)
                time.sleep(0.3)

            self.save_jobs(all_jobs)


    def save_jobs(self, job_list):
        jobs_logger.info(f'Started saving jobs, Count:- {len(job_list)}')
        bulk_jobs_lst = []

        for job in job_list:
            jobs_logger.info(f'job:- {job}')
            job_id = job["job_id"]

            if Job.objects.filter(job_id=job_id).exists():
                jobs_logger.info(f'Job already created')
                self.total_skipped += 1
                continue
            
            if not job["company_slug"]:
                self.total_skipped += 1
                continue

            company, _ = Company.objects.get_or_create(
                slugname=job["company_slug"],
                defaults={
                    "name": job["company_name"],
                    "company_url": job["company_url"]
                }
            )

            job_obj = Job(
                            job_id=job_id,
                            company=company,
                            title=job["title"],
                            location=job["location"],
                            job_url=job["job_url"],
                            description=job.get("description"),
                            source=self.source,
                            payload=job,
                            raw_data_id=job["raw_data_id"]
                        )
            bulk_jobs_lst.append(job_obj)

        jobs_logger.info(f'{len(bulk_jobs_lst)} jobs are there to save')
        if bulk_jobs_lst:
            Job.objects.bulk_create(bulk_jobs_lst)
            self.total_created += len(bulk_jobs_lst)

        jobs_logger.info(f'{len(bulk_jobs_lst)} jobs created successfully for {self.source}')


    def start(self):
        self.scrape_jobs(location="India", pages=40, f_TPR='last 24 hours')

        JobRawData.objects.filter(job__isnull=True).delete()

        jobs_logger.info(f'Total created:- {self.total_created}, Total skipped:- {self.total_skipped}')
        print(f'Total created:- {self.total_created}, Total skipped:- {self.total_skipped}')
