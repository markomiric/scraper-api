import datetime
from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class JobStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    DRAFT = "DRAFT"


@dataclass
class Job:
    id: UUID
    title: str
    company: str
    location: str
    job_url: str
    description: str
    logo_url: str
    status: JobStatus
    author: str
    created_at: str
    updated_at: str

    @classmethod
    def create(cls, id_, title, company, location, job_url, description, logo_url, author) -> "Job":
        status = JobStatus.DRAFT
        created_at = datetime.datetime.now(datetime.UTC).isoformat()
        updated_at = datetime.datetime.now(datetime.UTC).isoformat()
        return cls(
            id_, title, company, location, job_url, description, logo_url, status, author, created_at, updated_at
        )

    def activate(self) -> None:
        self.status = JobStatus.ACTIVE
        self.updated_at = datetime.datetime.now(datetime.UTC).isoformat()

    def close(self) -> None:
        self.status = JobStatus.CLOSED
        self.updated_at = datetime.datetime.now(datetime.UTC).isoformat()
