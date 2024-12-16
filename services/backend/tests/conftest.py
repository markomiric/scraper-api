import os
import time

import boto3
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from moto import mock_aws

from src.dependencies import get_job_store
from src.job.store import JobStore
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
def admin_email():
    return "admin@email.com"


@pytest.fixture
def token(user_email):
    token = jwt.encode(
        {
            "sub": "1234567890",
            "email": user_email,
            "cognito:username": user_email,
            "cognito:groups": ["User"],
            "token_use": "id",
            "auth_time": int(time.time()),
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_MockPoolId",
            "aud": "MockClientId",
        },
        "test-secret",
        algorithm="HS256",
    )
    return token


@pytest.fixture
def admin_token(admin_email):
    token = jwt.encode(
        {
            "sub": "0987654321",
            "email": admin_email,
            "cognito:username": admin_email,
            "cognito:groups": ["Admin"],
            "token_use": "id",
            "auth_time": int(time.time()),
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_MockPoolId",
            "aud": "MockClientId",
        },
        "test-secret",
        algorithm="HS256",
    )
    return token


@pytest.fixture(scope="session", autouse=True)
def set_testing_env():
    os.environ["TESTING"] = "1"
    yield
    os.environ.pop("TESTING", None)


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
