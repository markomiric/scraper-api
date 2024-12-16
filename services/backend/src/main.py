import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from src.health.routes import router as health_router
from src.job.routes import router as job_router
from src.user.routes import router as auth_router

stage = os.environ.get("STAGE", "")
root_path = f"/{stage}" if stage else ""


def create_application() -> FastAPI:
    application = FastAPI(root_path=root_path)
    application.include_router(auth_router, prefix="/api")
    application.include_router(job_router, prefix="/api")
    application.include_router(health_router, prefix="/api")
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
