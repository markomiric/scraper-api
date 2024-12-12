from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.job.model import JobStatus


class CreateJobRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Job title")
    company: str = Field(..., min_length=1, description="Company name")
    location: str = Field(..., min_length=1, description="Job location")
    job_url: str = Field(..., min_length=1, description="URL to job posting")
    author: str = Field(..., min_length=1, description="Email of job poster")
    description: str = Field(default="", description="Job description")
    logo_url: Optional[str] = Field(default=None, description="Company logo URL")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "Berlin, Germany",
                "job_url": "https://example.com/job/123",
                "author": "recruiter@example.com",
                "description": "We are looking for...",
                "logo_url": "https://example.com/logo.png",
            }
        }


class JobResponse(BaseModel):
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

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "Berlin, Germany",
                "job_url": "https://example.com/job/123",
                "author": "recruiter@example.com",
                "description": "We are looking for...",
                "logo_url": "https://example.com/logo.png",
                "status": "ACTIVE",
                "created_at": "2024-03-15T10:30:00Z",
                "updated_at": "2024-03-15T10:30:00Z",
            }
        }
