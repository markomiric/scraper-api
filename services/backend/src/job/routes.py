import uuid

from fastapi import APIRouter, Depends
from starlette import status

from src.dependencies import get_current_user, get_job_store
from src.job.model import Job
from src.job.schema import CreateJobRequest, JobResponse
from src.job.store import JobStore

router = APIRouter()


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_request: CreateJobRequest,
    job_store: JobStore = Depends(get_job_store),
    current_user=Depends(get_current_user),
):
    job = Job.create(
        id_=uuid.uuid4(),
        title=job_request.title,
        company=job_request.company,
        location=job_request.location,
        job_url=job_request.job_url,
        description=job_request.description,
        logo_url=job_request.logo_url,
        author=current_user["email"],  # Set author to user's email
    )
    job_store.add(job)

    return job
