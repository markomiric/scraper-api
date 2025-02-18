import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from src.auth.routes import router as auth_router
from src.health.routes import router as health_router
from src.job.routes import router as job_router
from src.linkedin.routes import router as linkedin_scraper_router
from src.user.routes import router as user_router

environment = os.environ.get("STAGE", "")
root_path = f"/{environment}" if environment else ""


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    application = FastAPI(title="KamaCareer", root_path=root_path)
    application.include_router(auth_router, prefix="/api/v1")
    application.include_router(user_router, prefix="/api/v1")
    application.include_router(job_router, prefix="/api/v1")
    application.include_router(linkedin_scraper_router, prefix="/api/v1")
    application.include_router(health_router, prefix="/api/v1")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return application


app = create_application()
handle = Mangum(app)
