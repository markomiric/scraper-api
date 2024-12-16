import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from src.job.routes import router as job_router
from src.user.routes import router as auth_router

# Get the stage from environment variables
stage = os.environ.get("STAGE", "")
root_path = f"/{stage}" if stage else ""


def create_application() -> FastAPI:
    application = FastAPI(root_path=root_path)
    application.include_router(auth_router, prefix="/api", tags=["Auth"])
    application.include_router(job_router, prefix="/api", tags=["Job"])
    return application


app = create_application()
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"message": "OK"}


handle = Mangum(app)
