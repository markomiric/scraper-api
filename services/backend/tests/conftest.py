import os

import boto3
import jwt
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from src.job.store import JobStore, get_job_store
from src.main import app


@pytest.fixture
def client(job_store):
    app.dependency_overrides[get_job_store] = lambda: job_store
    return TestClient(app)


@pytest.fixture
def job_store(dynamodb_table):
    return JobStore(dynamodb_table)


@pytest.fixture
def user_email():
    return "user@email.com"


@pytest.fixture
def id_token(user_email):
    return jwt.encode({"cognito:username": user_email}, "secret")


@pytest.fixture
def dynamodb_table():
    os.environ["AWS_REGION"] = "eu-central-1"

    with mock_aws():
        client = boto3.client("dynamodb")
        table_name = "test-table"
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GS1PK", "AttributeType": "S"},
                {"AttributeName": "GS1SK", "AttributeType": "S"},
            ],
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GS1",
                    "KeySchema": [
                        {"AttributeName": "GS1PK", "KeyType": "HASH"},
                        {"AttributeName": "GS1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {
                        "ProjectionType": "ALL",
                    },
                },
            ],
        )
        yield table_name
