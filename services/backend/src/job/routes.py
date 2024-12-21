import datetime
import uuid
from typing import List

from fastapi import APIRouter, Depends
from starlette import status

from src.dependencies import get_current_user, get_job_store
from src.job.model import Job
from src.job.schema import CreateJobRequest, JobResponse, UpdateJobRequest
from src.job.store import JobStore

router = APIRouter(prefix="/jobs", tags=["Job"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_request: CreateJobRequest,
    job_store: JobStore = Depends(get_job_store),
    current_user=Depends(get_current_user),
):
    """
    Create a new job listing in DynamoDB.
    """
    job = Job.create(
        id_=uuid.uuid4(),
        title=job_request.title,
        company=job_request.company,
        location=job_request.location,
        job_url=job_request.job_url,
        description=job_request.description,
        logo_url=job_request.logo_url,
        author=current_user["email"],
    )
    job_store.add(job)

    return job


@router.get("/", response_model=List[JobResponse])
def get_jobs(
    job_store: JobStore = Depends(get_job_store), current_user=Depends(get_current_user)
):
    """
    Retrieve all jobs for the current user.
    """
    jobs = job_store.get_all(current_user["email"])
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    job_store: JobStore = Depends(get_job_store),
    current_user=Depends(get_current_user),
):
    job = job_store.get(job_id, current_user["email"])
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: str,
    job_request: UpdateJobRequest,
    job_store: JobStore = Depends(get_job_store),
    current_user=Depends(get_current_user),
):
    """
    Update an existing job with new field values.
    """
    job = job_store.get(job_id, current_user["email"])
    update_data = job_request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    job.updated_at = datetime.datetime.now(datetime.UTC).isoformat()
    job_store.update(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: str,
    job_store: JobStore = Depends(get_job_store),
    current_user=Depends(get_current_user),
):
    job_store.delete(job_id, current_user["email"])
