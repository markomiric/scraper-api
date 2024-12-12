from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from src.job.routes import router as job_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(job_router, prefix="/api", tags=["jobs"])

    return application


app = create_application()


@app.get("/api/health")
def health():
    return {"message": "OK"}


handle = Mangum(app)
