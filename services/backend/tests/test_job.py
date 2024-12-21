import uuid

from starlette import status

from src.job.model import Job
from src.job.store import JobStore


def test_added_job_retrieved_by_id(dynamodb_table):
    """
    Verifies that a newly added job can be retrieved by its ID.
    """
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
    """
    Ensures that only active jobs are returned for a given author.
    """
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


def test_create_job(client, user_email, token):
    job_data = {
        "title": "Python Developer",
        "company": "Tech Corp",
        "location": "Berlin, Germany",
        "description": "Python role",
        "job_url": "https://example.com/job/123",
        "logo_url": "https://example.com/logo.png",
    }

    response = client.post(
        "/api/v1/jobs",
        json=job_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    body = response.json()

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


def test_get_all_jobs(client, job_store, user_email, token):
    job1 = Job.create(
        id_=uuid.uuid4(),
        title="Python Developer",
        company="Tech Corp",
        location="Berlin",
        job_url="https://example.com/job/1",
        description="Python role",
        logo_url="https://example.com/logo1.png",
        author=user_email,
    )
    job2 = Job.create(
        id_=uuid.uuid4(),
        title="Senior Developer",
        company="Other Corp",
        location="Remote",
        job_url="https://example.com/job/2",
        description="Senior role",
        logo_url="https://example.com/logo2.png",
        author=user_email,
    )
    job_store.add(job1)
    job_store.add(job2)

    response = client.get(
        "/api/v1/jobs",
        headers={"Authorization": f"Bearer {token}"},
    )
    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(body) == 2
    assert any(job["id"] == str(job1.id) for job in body)
    assert any(job["id"] == str(job2.id) for job in body)


def test_get_job_by_id(client, job_store, user_email, token):
    job = Job.create(
        id_=uuid.uuid4(),
        title="Python Developer",
        company="Tech Corp",
        location="Berlin",
        job_url="https://example.com/job/1",
        description="Python role",
        logo_url="https://example.com/logo1.png",
        author=user_email,
    )
    job_store.add(job)

    response = client.get(
        f"/api/v1/jobs/{job.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body["id"] == str(job.id)
    assert body["title"] == job.title
    assert body["status"] == job.status.value


def test_update_job(client, job_store, user_email, token):
    job = Job.create(
        id_=uuid.uuid4(),
        title="Python Developer",
        company="Tech Corp",
        location="Berlin",
        job_url="https://example.com/job/1",
        description="Python role",
        logo_url="https://example.com/logo1.png",
        author=user_email,
    )
    job_store.add(job)

    update_data = {
        "title": "Senior Python Developer",
        "location": "Remote",
        "status": "ACTIVE",
    }

    response = client.put(
        f"/api/v1/jobs/{job.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body["title"] == update_data["title"]
    assert body["location"] == update_data["location"]
    assert body["status"] == update_data["status"]
    assert body["company"] == job.company  # Unchanged field


def test_delete_job(client, job_store, user_email, token):
    job = Job.create(
        id_=uuid.uuid4(),
        title="Python Developer",
        company="Tech Corp",
        location="Berlin",
        job_url="https://example.com/job/1",
        description="Python role",
        logo_url="https://example.com/logo1.png",
        author=user_email,
    )
    job_store.add(job)

    response = client.delete(
        f"/api/v1/jobs/{job.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    try:
        job_store.get(str(job.id), user_email)
        assert False, "Job should have been deleted"
    except Exception:
        pass


def test_update_job_maintains_unchanged_fields(client, job_store, user_email, token):
    job = Job.create(
        id_=uuid.uuid4(),
        title="Python Developer",
        company="Tech Corp",
        location="Berlin",
        job_url="https://example.com/job/1",
        description="Python role",
        logo_url="https://example.com/logo1.png",
        author=user_email,
    )
    job_store.add(job)

    update_data = {"title": "Senior Python Developer"}

    response = client.put(
        f"/api/v1/jobs/{job.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body["title"] == update_data["title"]
    assert body["location"] == job.location
    assert body["company"] == job.company
    assert body["job_url"] == job.job_url
    assert body["description"] == job.description
    assert body["logo_url"] == job.logo_url
