from typing import Optional
from uuid import UUID

from pydantic import Field

from src.common.schema import BaseSchema
from src.job.model import JobStatus


class CreateJobRequest(BaseSchema):
    title: str = Field(..., min_length=1, description="Job title")
    company: str = Field(..., min_length=1, description="Company name")
    location: str = Field(..., min_length=1, description="Job location")
    job_url: str = Field(..., min_length=1, description="URL to job posting")
    author: str = Field(..., min_length=1, description="Email of job poster")
    description: str = Field(default="", description="Job description")
    logo_url: Optional[str] = Field(default=None, description="Company logo URL")


class JobResponse(BaseSchema):
    id: UUID = Field(..., description="Unique job identifier")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    job_url: str = Field(..., description="URL to job posting")
    description: str = Field(default="", description="Job description")
    logo_url: Optional[str] = Field(default=None, description="Company logo URL")
    status: JobStatus = Field(..., description="Current job status")
    author: str = Field(..., description="Email of job poster")
    created_at: str = Field(..., description="ISO formatted creation timestamp")
    updated_at: str = Field(..., description="ISO formatted update timestamp")
