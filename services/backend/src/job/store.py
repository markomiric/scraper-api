# python
import logging
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Key

from src.job.model import Job, JobStatus

logger = logging.getLogger("job.store")
logger.setLevel(logging.INFO)


class JobStore:
    """
    DynamoDB-based implementation for storing and retrieving Job entities.
    """

    def __init__(self, table_name: str, dynamodb_url: str = None):
        self.table_name = table_name
        self.dynamodb_url = dynamodb_url
        logger.info("Initialized JobStore with table: %s", table_name)

    def add(self, job: Job) -> None:
        logger.info("Adding job with id: %s for author: %s", job.id, job.author)
        try:
            dynamodb = boto3.resource("dynamodb", endpoint_url=self.dynamodb_url)
            table = dynamodb.Table(self.table_name)
            result = table.put_item(
                Item={
                    "PK": f"#{job.author}",
                    "SK": f"#{job.id}",
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
            http_status = result.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if http_status == 200:
                logger.debug(
                    "Job %s added successfully with HTTPStatusCode: %s",
                    job.id,
                    http_status,
                )
            else:
                logger.warning(
                    "Job %s put_item returned HTTPStatusCode: %s", job.id, http_status
                )
        except Exception as e:
            logger.exception(
                "Error adding job %s for author %s: %s", job.id, job.author, e
            )
            raise

    def get(self, job_id: str, author: str) -> Job:
        logger.info("Retrieving job with id: %s for author: %s", job_id, author)
        dynamodb = boto3.resource("dynamodb", endpoint_url=self.dynamodb_url)
        table = dynamodb.Table(self.table_name)
        record = table.get_item(Key={"PK": f"#{author}", "SK": f"#{job_id}"})
        item = record.get("Item")
        if not item:
            logger.error("Job %s not found for author %s", job_id, author)
            raise ValueError(f"Job {job_id} not found for author {author}")
        job = Job(
            id=UUID(item["id"]),
            title=item["title"],
            company=item["company"],
            location=item["location"],
            job_url=item["job_url"],
            description=item["description"],
            logo_url=item["logo_url"],
            status=JobStatus[item["status"]],
            author=item["author"],
            created_at=item["created_at"],
            updated_at=item["updated_at"],
        )
        logger.debug("Job retrieved successfully: %s", job_id)
        return job

    def get_active(self, author: str):
        logger.info("Retrieving active jobs for author: %s", author)
        return self._get_by_status(author, JobStatus.ACTIVE)

    def get_closed(self, author: str):
        logger.info("Retrieving closed jobs for author: %s", author)
        return self._get_by_status(author, JobStatus.CLOSED)

    def _get_by_status(self, author: str, status: JobStatus):
        logger.info(
            "Retrieving jobs for author: %s with status: %s", author, status.value
        )
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
        logger.debug(
            "Retrieved %d jobs for author %s with status %s",
            len(jobs),
            author,
            status.value,
        )
        return jobs

    def get_all(self, limit: int, last_key: dict = None):
        """
        Retrieve up to a limited number of jobs from the table using pagination.
        Use last_key to continue from a previous scan, if provided.
        """
        logger.info("Retrieving up to %d jobs", limit)
        dynamodb = boto3.resource("dynamodb", endpoint_url=self.dynamodb_url)
        table = dynamodb.Table(self.table_name)
        scan_kwargs = {"Limit": limit}
        if last_key is not None:
            scan_kwargs["ExclusiveStartKey"] = last_key

        response = table.scan(**scan_kwargs)
        jobs = [
            Job(
                id=UUID(item["id"]),
                title=item["title"],
                company=item["company"],
                location=item["location"],
                job_url=item["job_url"],
                description=item["description"],
                logo_url=item.get("logo_url"),
                status=JobStatus[item["status"]],
                author=item["author"],
                created_at=item["created_at"],
                updated_at=item["updated_at"],
            )
            for item in response.get("Items", [])
        ]
        new_last_key = response.get("LastEvaluatedKey")
        logger.debug("Retrieved %d jobs; new_last_key: %s", len(jobs), new_last_key)
        return jobs, new_last_key

    def get_all_by_author(self, author: str):
        logger.info("Retrieving all jobs for author: %s", author)
        dynamodb = boto3.resource("dynamodb", endpoint_url=self.dynamodb_url)
        table = dynamodb.Table(self.table_name)
        response = table.query(KeyConditionExpression=Key("PK").eq(f"#{author}"))
        jobs = [
            Job(
                id=UUID(item["id"]),
                title=item["title"],
                company=item["company"],
                location=item["location"],
                job_url=item["job_url"],
                description=item["description"],
                logo_url=item.get("logo_url"),
                status=JobStatus[item["status"]],
                author=item["author"],
                created_at=item["created_at"],
                updated_at=item["updated_at"],
            )
            for item in response["Items"]
        ]
        logger.debug("Retrieved %d total jobs for author %s", len(jobs), author)
        return jobs

    def update(self, job: Job) -> None:
        logger.info("Updating job with id: %s for author: %s", job.id, job.author)
        dynamodb = boto3.resource("dynamodb", endpoint_url=self.dynamodb_url)
        table = dynamodb.Table(self.table_name)
        table.update_item(
            Key={
                "PK": f"#{job.author}",
                "SK": f"#{job.id}",
            },
            UpdateExpression="""
                SET #title=:title, 
                    #company=:company, 
                    #location=:location,
                    #job_url=:job_url, 
                    #description=:description, 
                    #logo_url=:logo_url,
                    #status=:status, 
                    #updated_at=:updated_at
            """,
            ExpressionAttributeNames={
                "#title": "title",
                "#company": "company",
                "#location": "location",
                "#job_url": "job_url",
                "#description": "description",
                "#logo_url": "logo_url",
                "#status": "status",
                "#updated_at": "updated_at",
            },
            ExpressionAttributeValues={
                ":title": job.title,
                ":company": job.company,
                ":location": job.location,
                ":job_url": job.job_url,
                ":description": job.description,
                ":logo_url": job.logo_url,
                ":status": job.status.value,
                ":updated_at": job.updated_at,
            },
        )
        logger.debug("Job updated successfully: %s", job.id)

    def delete(self, job_id: str, author: str) -> None:
        logger.info("Deleting job with id: %s for author: %s", job_id, author)
        dynamodb = boto3.resource("dynamodb", endpoint_url=self.dynamodb_url)
        table = dynamodb.Table(self.table_name)
        table.delete_item(
            Key={
                "PK": f"#{author}",
                "SK": f"#{job_id}",
            }
        )
        logger.debug("Job deleted successfully: %s", job_id)
