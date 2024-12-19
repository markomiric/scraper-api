import os
import time
from unittest.mock import patch

import boto3
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from moto import mock_aws

from src.dependencies import get_job_store
from src.job.store import JobStore
from src.main import app


@pytest.fixture
def mock_cognito_get_user():
    with patch("src.aws.cognito.Cognito.get_user") as mock:
        mock.return_value = {
            "UserAttributes": [
                {"Name": "sub", "Value": "1234567890"},
                {"Name": "email", "Value": "user@email.com"},
                {"Name": "email_verified", "Value": "true"},
                {"Name": "username", "Value": "user@email.com"},
            ]
        }
        yield mock


@pytest.fixture
def client(job_store, mock_cognito_get_user):
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
    current_time = int(time.time())
    token = jwt.encode(
        {
            "sub": "1234567890",
            "cognito:groups": ["User"],  # Changed from "cognito:groups" to "roles"
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_MockPoolId",
            "client_id": "test-client-id",
            "origin_jti": "test-origin-jti",
            "event_id": "test-event-id",
            "token_use": "id",
            "scope": "aws.cognito.signin.user.admin",
            "auth_time": current_time,
            "exp": current_time + 3600,
            "iat": current_time,
            "jti": "test-jti",
            "username": user_email,
        },
        "test-secret",
        algorithm="HS256",
    )
    return token


@pytest.fixture
def admin_token(admin_email):
    current_time = int(time.time())
    token = jwt.encode(
        {
            "sub": "0987654321",
            "email": admin_email,
            "username": admin_email,
            "cognito:groups": ["Admin"],  # Changed from "cognito:groups" to "roles"
            "token_use": "id",
            "auth_time": current_time,
            "exp": current_time + 3600,
            "iat": current_time,
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_MockPoolId",
            "client_id": "test-client-id",
            "origin_jti": "test-origin-jti",
            "event_id": "test-event-id",
            "scope": "aws.cognito.signin.user.admin",
            "jti": "test-jti",
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
