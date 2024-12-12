import os
from typing import Dict

import boto3
from botocore.exceptions import ClientError


def create_table(
    table_name: str, endpoint_url: str, region: str = "eu-central-1"
) -> Dict:
    """Create DynamoDB table for jobs."""
    try:
        client = boto3.client(
            "dynamodb",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id="dummy",
            aws_secret_access_key="dummy",
        )

        response = client.create_table(
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
        print(f"Table {table_name} created successfully")
        return response
    except ClientError as e:
        print(f"Error creating table: {e}")
        raise


if __name__ == "__main__":
    table_name = os.getenv("TABLE_NAME", "local-jobs-table")
    dynamodb_url = os.getenv("DYNAMODB_URL", "http://localhost:8000")

    create_table(table_name=table_name, endpoint_url=dynamodb_url)
