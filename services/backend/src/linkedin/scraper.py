# python
import asyncio
import logging
import sys
from urllib.parse import quote

from dotenv import load_dotenv

# from langchain_core.prompts import PromptTemplate
# from langchain_openai import ChatOpenAI
from src.common.http_client import HttpClient
from src.config import get_settings
from src.job.store import JobStore
from src.linkedin.parser import LinkedInJobParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

load_dotenv()

settings = get_settings()
job_store = JobStore(table_name=settings.TABLE_NAME, dynamodb_url=settings.DYNAMODB_URL)


def build_linkedin_url(keyword: str, location: str, timespan: str, page: int) -> str:
    return (
        f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
        f"keywords={quote(keyword)}"
        f"&location={quote(location)}"
        f"&f_WT=''"
        f"&f_TPR={timespan}"
        f"&start={page * 25}"
    )


# def get_job_summary(job: Job) -> str:
#     summary_template = """
#         Given the Linkedin job description information {information} about a job, create:
#         1. A short summary
#         2. A list of skills required
#     """
#     summary_prompt_template = PromptTemplate(input_variables=["information"], template=summary_template)
#     llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", max_tokens=1000)
#     chain = summary_prompt_template | llm
#     result = chain.invoke(input={"information": job.description})
#     return result.content


async def main(keywords: str = "python developer"):
    """
    Run the LinkedIn scraper using the provided keywords.
    If no keywords are supplied, defaults to "python developer".
    """
    logger = logging.getLogger("linkedin.scraper")
    logger.info("Starting LinkedIn scraper with keywords: %s", keywords)
    logger.debug("Settings: %s", settings.model_dump_json(indent=2))

    client = HttpClient()
    parser = LinkedInJobParser(client)
    jobs = []

    try:
        location = "Croatia"
        for page in range(settings.PAGES_TO_SCRAPE):
            url = build_linkedin_url(keywords, location, settings.TIMESPAN, page)
            if soup := await client.get(url):
                job_cards = await parser.parse_job_cards(soup)
                jobs.extend(job_cards)
                logger.info("Found %d jobs on page %d", len(job_cards), page + 1)
                await asyncio.sleep(settings.REQUEST_DELAY)

        logger.info("Found total of %d jobs, starting import to DynamoDB", len(jobs))
        for job in jobs:
            try:
                logger.debug("Adding job: %s", job)
                job_store.add(job)
                logger.info("Successfully added job with ID: %s", job.id)
            except Exception as e:
                logger.error("Failed to add job %s: %s", job.id, str(e))

    except Exception as e:
        logger.error("Error during scraping: %s", str(e))
        raise
    finally:
        await client.close()


def handler(event, context):
    asyncio.run(main(event.get("keywords", "python developer")))


if __name__ == "__main__":
    import sys

    # Optionally pass a keyword argument when running locally.
    keyword_arg = sys.argv[1] if len(sys.argv) > 1 else "python developer"
    asyncio.run(main(keyword_arg))
