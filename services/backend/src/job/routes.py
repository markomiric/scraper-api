import uuid

from fastapi import APIRouter, Depends
from starlette import status

from src.common import get_user_email
from src.job.model import Job
from src.job.schema import CreateJobRequest, JobResponse
from src.job.store import JobStore, get_job_store

router = APIRouter()


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: CreateJobRequest,
    user_email: str = Depends(get_user_email),
    job_store: JobStore = Depends(get_job_store),
):
    job = Job.create(
        id_=uuid.uuid4(),
        title=payload.title,
        company=payload.company,
        location=payload.location,
        job_url=payload.job_url,
        description=payload.description,
        logo_url=payload.logo_url,
        author=user_email,
    )
    job_store.add(job)

    return job
