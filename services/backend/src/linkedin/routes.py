# python
import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from src.dependencies import has_roles
from src.linkedin.scraper import main as run_scraper

router = APIRouter(tags=["Scraper"])
logger = logging.getLogger("linkedin.routes")


@router.get("/scrape/linkedin", response_model=dict)
async def scrape_linkedin(
    background_tasks: BackgroundTasks,
    keywords: str = Query(..., description="Keywords to guide the scraping process"),
    _: Any = Depends(has_roles(["Admin"])),
) -> dict:
    """
    Endpoint to trigger LinkedIn scraping in the background.

    This endpoint accepts a `keywords` query parameter, which will be passed to the scraper
    to determine the best method for processing.
    """
    try:
        background_tasks.add_task(run_scraper, keywords)
        logger.info("Scraping task added with keywords: %s", keywords)
        return {"message": f"LinkedIn scraping started with keywords: {keywords}"}
    except Exception:
        logger.error("Failed to launch LinkedIn scraping task", exc_info=True)
        raise HTTPException(status_code=500, detail="Scraping could not be started.")
