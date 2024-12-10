import uuid

from src.job.model import Job
from src.job.store import JobStore


def test_added_job_retrieved_by_id(dynamodb_table):
    repository = JobStore(table_name=dynamodb_table)
    job = Job.create(
        id_=uuid.uuid4(),
        title="Software Engineer",
        company="Big Corp",
        location="Remote",
        job_url="https://example.com",
        description="Join us!",
        logo_url="https://example.com/logo.png",
        author="admin@email.com",
    )

    repository.add(job)

    assert repository.get(job_id=job.id, author=job.author) == job


def test_active_jobs_retrieved_by_status(dynamodb_table):
    repository = JobStore(table_name=dynamodb_table)
    active_job = Job.create(
        uuid.uuid4(),
        "Software Engineer",
        "Big Corp",
        "Remote",
        "https://example.com",
        "Join us!",
        "https://example.com/logo.png",
        "admin@email.com",
    )
    active_job.activate()
    closed_job = Job.create(
        uuid.uuid4(),
        "Software Engineer",
        "Big Corp",
        "Remote",
        "https://example.com",
        "Join us!",
        "https://example.com/logo.png",
        "admin@email.com",
    )
    closed_job.close()

    repository.add(active_job)
    repository.add(closed_job)

    assert repository.get_active(author=active_job.author) == [active_job]
