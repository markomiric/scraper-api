import datetime
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Key

from src.config import get_settings
from src.job.model import Job, JobStatus


class JobStore:
    def __init__(self, table_name, dynamodb_url=None):
        self.table_name = table_name
        self.dynamodb_url = dynamodb_url

    def add(self, job: Job) -> None:
        dynamodb = boto3.resource("dynamodb", endpoint_url=self.dynamodb_url)
        table = dynamodb.Table(self.table_name)
        table.put_item(
            Item={
                "PK": f"#{job.author}",
                "SK": f"#{job.id}",
                "GS1PK": f"#{job.author}#{job.status.value}",
                "GS1SK": f"#{datetime.datetime.now(datetime.UTC).isoformat()}",
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "job_url": job.job_url,
                "description": job.description,
                "logo_url": job.logo_url,
                "status": job.status.value,
                "author": job.author,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
            }
        )

    def get(self, job_id: str, author: str) -> Job:
        dynamodb = boto3.resource("dynamodb", endpoint_url=self.dynamodb_url)
        table = dynamodb.Table(self.table_name)
        record = table.get_item(Key={"PK": f"#{author}", "SK": f"#{job_id}"})
        return Job(
            id=UUID(record["Item"]["id"]),
            title=record["Item"]["title"],
            company=record["Item"]["company"],
            location=record["Item"]["location"],
            job_url=record["Item"]["job_url"],
            description=record["Item"]["description"],
            logo_url=record["Item"]["logo_url"],
            status=record["Item"]["status"],
            author=record["Item"]["author"],
            created_at=record["Item"]["created_at"],
            updated_at=record["Item"]["updated_at"],
        )

    def get_active(self, author):
        return self._get_by_status(author, JobStatus.ACTIVE)

    def get_closed(self, author):
        return self._get_by_status(author, JobStatus.CLOSED)

    def _get_by_status(self, author, status):
        dynamodb = boto3.resource("dynamodb", endpoint_url=self.dynamodb_url)
        table = dynamodb.Table(self.table_name)
        last_key = None
        query_kwargs = {
            "IndexName": "GS1",
            "KeyConditionExpression": Key("GS1PK").eq(f"#{author}#{status.value}"),
        }
        jobs = []
        while True:
            if last_key is not None:
                query_kwargs["ExclusiveStartKey"] = last_key
            response = table.query(**query_kwargs)
            jobs.extend(
                [
                    Job(
                        id=UUID(record["id"]),
                        title=record["title"],
                        company=record["company"],
                        location=record["location"],
                        job_url=record["job_url"],
                        description=record["description"],
                        logo_url=record["logo_url"],
                        status=JobStatus[record["status"]],
                        author=record["author"],
                        created_at=record["created_at"],
                        updated_at=record["updated_at"],
                    )
                    for record in response["Items"]
                ]
            )
            last_key = response.get("LastEvaluatedKey")
            if last_key is None:
                break

        return jobs


def get_job_store() -> JobStore:
    config = get_settings()
    return JobStore(config.TABLE_NAME, dynamodb_url=config.DYNAMODB_URL)
