import uuid

from starlette import status

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


def test_create_job(client, user_email, id_token):
    job_data = {
        "title": "Python Developer",
        "company": "Tech Corp",
        "location": "Berlin, Germany",
        "job_url": "https://example.com/job/123",
        "author": user_email,
        "description": "We are looking for a Python developer",
        "logo_url": "https://example.com/logo.png",
    }

    # Make request
    response = client.post(
        "/api/jobs", json=job_data, headers={"Authorization": id_token}
    )
    body = response.json()

    # Assertions
    assert response.status_code == status.HTTP_201_CREATED
    assert uuid.UUID(body["id"])
    assert body["title"] == job_data["title"]
    assert body["company"] == job_data["company"]
    assert body["location"] == job_data["location"]
    assert body["job_url"] == job_data["job_url"]
    assert body["description"] == job_data["description"]
    assert body["logo_url"] == job_data["logo_url"]
    assert body["status"] == "DRAFT"
    assert body["author"] == user_email
    assert "created_at" in body
    assert "updated_at" in body
