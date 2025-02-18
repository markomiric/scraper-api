# python
import datetime
import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from starlette import status

from src.dependencies import get_current_user, get_job_store
from src.job.model import Job
from src.job.schema import (
    CreateJobRequest,
    JobResponse,
    PaginatedJobsResponse,
    UpdateJobRequest,
)
from src.job.store import JobStore
from src.job.util import decode_last_key, encode_last_key

logger = logging.getLogger("job.routes")
router = APIRouter(prefix="/jobs", tags=["Job"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_request: CreateJobRequest,
    job_store: JobStore = Depends(get_job_store),
    current_user=Depends(get_current_user),
):
    """
    Create a new job listing in DynamoDB.
    """
    logger.info("Creating job for user %s", current_user["email"])
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
    logger.debug("Job created with ID %s", job.id)
    return job


@router.get("/paginated", response_model=PaginatedJobsResponse)
def get_paginated_jobs(
    job_store: JobStore = Depends(get_job_store),
    limit: int = Query(10, gt=0),
    last_key: Optional[str] = Query(
        None, description="Base64-encoded LastEvaluatedKey"
    ),
):
    logger.info("Fetching paginated jobs with limit %d", limit)
    parsed_last_key = decode_last_key(last_key) if last_key else None
    jobs, new_last_key = job_store.get_all(limit=limit, last_key=parsed_last_key)
    encoded_last_key = encode_last_key(new_last_key) if new_last_key else None
    return {"jobs": jobs, "last_key": encoded_last_key}


@router.get("/mine", response_model=List[JobResponse])
def get_jobs_by_author(
    job_store: JobStore = Depends(get_job_store), current_user=Depends(get_current_user)
):
    """
    Retrieve all jobs for the current user.
    """
    logger.info("Fetching all jobs for user %s", current_user["email"])
    jobs = job_store.get_all_by_author(current_user["email"])
    logger.debug("Fetched %d jobs for user %s", len(jobs), current_user["email"])
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    job_store: JobStore = Depends(get_job_store),
    current_user=Depends(get_current_user),
):
    logger.info("Fetching job %s for user %s", job_id, current_user["email"])
    job = job_store.get(job_id, current_user["email"])
    logger.debug("Job %s fetched successfully", job_id)
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
    logger.info("Updating job %s for user %s", job_id, current_user["email"])
    job = job_store.get(job_id, current_user["email"])
    update_data = job_request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    job.updated_at = datetime.datetime.now(datetime.UTC).isoformat()
    job_store.update(job)
    logger.debug("Job %s updated successfully", job_id)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: str,
    job_store: JobStore = Depends(get_job_store),
    current_user=Depends(get_current_user),
):
    logger.info("Deleting job %s for user %s", job_id, current_user["email"])
    job_store.delete(job_id, current_user["email"])
    logger.debug("Job %s deleted successfully", job_id)
