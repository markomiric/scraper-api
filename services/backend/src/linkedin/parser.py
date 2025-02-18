import logging
import uuid
from typing import List, Optional

from bs4 import BeautifulSoup, Tag

from src.common.http_client import HttpClient
from src.config import get_settings
from src.job.model import Job

logger = logging.getLogger("linkedin.parser")

settings = get_settings()


class LinkedInJobParser:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client
        self._logger = logging.getLogger(__name__)

    def _extract_text(self, element: Optional[Tag], strip: bool = True) -> str:
        if not element:
            return ""
        return (
            element.get_text(strip=strip).replace("\n", " ")
            if strip
            else element.get_text()
        )

    def _extract_job_id(self, parent_div: Tag) -> str:
        entity_urn = parent_div.get("data-entity-urn", "")
        return entity_urn.split(":")[-1]

    def _build_job_url(self, job_id: str) -> str:
        return f"https://www.linkedin.com/jobs/view/{job_id}/"

    async def parse_job_cards(self, soup: BeautifulSoup) -> List[Job]:
        jobs = []
        divs = soup.find_all("div", class_="base-search-card__info")

        if not divs:
            self._logger.info("No jobs found on the page.")
            return jobs

        for item in divs:
            try:
                job = await self._parse_single_job_card(item)
                if job:
                    jobs.append(job)
            except Exception as e:
                self._logger.error(f"Error parsing job card: {str(e)}")
                continue

        return jobs

    async def _parse_single_job_card(self, item: Tag) -> Optional[Job]:
        try:
            parent_div = item.parent
            job_id = self._extract_job_id(parent_div)
            job_url = self._build_job_url(job_id)

            title = self._extract_text(item.find("h3"))
            company = self._extract_text(item.find("a", class_="hidden-nested-link"))
            location = self._extract_text(
                item.find("span", class_="job-search-card__location")
            )
            description_soup = await self.http_client.get(job_url)
            description = (
                self.parse_job_description(description_soup) if description_soup else ""
            )
            logo_url = self._extract_logo_url(item)

            job = Job.create(
                id_=uuid.uuid4(),
                title=title,
                company=company,
                location=location,
                job_url=job_url,
                description=description,
                logo_url=logo_url,
                author=settings.AUTHOR,
            )

            return job

        except Exception as e:
            self._logger.error(f"Error parsing job card: {str(e)}")
            return None

    def _extract_date(self, item: Tag) -> str:
        date_tag = item.find("time", class_="job-search-card__listdate") or item.find(
            "time", class_="job-search-card__listdate--new"
        )
        return date_tag["datetime"] if date_tag else ""

    def _extract_logo_url(self, item: Tag) -> str:
        logo_img = item.find_previous("img", class_="artdeco-entity-image")
        return logo_img.get("data-delayed-url", "") if logo_img else ""

    def parse_job_description(self, soup: BeautifulSoup) -> str:
        try:
            div = soup.find("div", class_="description__text description__text--rich")
            if not div:
                return "Could not find Job Description"

            # Remove unwanted elements
            for element in div.find_all(["span", "a"]):
                element.decompose()

            # Format bullet points
            for ul in div.find_all("ul"):
                for li in ul.find_all("li"):
                    li.insert(0, "- ")

            # Clean up text
            text = div.get_text(separator="\n").strip()
            text = text.replace("::marker", "-").replace("-\n", "- ")
            text = text.replace("Show less", "").replace("Show more", "")

            return text

        except Exception as e:
            self._logger.error(f"Error parsing job description: {str(e)}")
            return "Error parsing job description"
