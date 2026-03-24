"""
Script to create the DynamoDB table for the guidance catalog.
"""

import os
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
try:
    from dotenv import load_dotenv

    load_dotenv(env_path, override=True)
except ImportError:
    pass


def create_guidance_catalog_table(table_name="SecuriVAGuidanceCatalog"):
    """
    Create DynamoDB table with schema for guidance catalog storage.

    Schema:
    - Partition Key: content_type (String)
    - Sort Key: content_id (String)
    - Attributes: content (Map/List), updated_at (String)
    """
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError as exc:
        print("❌ boto3 and botocore are required to create the guidance catalog table")
        raise exc

    try:
        dynamodb = boto3.resource(
            "dynamodb",
            region_name=os.getenv("AWS_REGION", "us-east-2"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "content_type", "KeyType": "HASH"},
                {"AttributeName": "content_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "content_type", "AttributeType": "S"},
                {"AttributeName": "content_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
            Tags=[
                {"Key": "Environment", "Value": "Production"},
                {"Key": "Application", "Value": "SecuriVA"},
                {"Key": "Purpose", "Value": "GuidanceCatalog"},
            ],
        )

        print(f"⏳ Creating table '{table_name}'...")
        table.wait_until_exists()
        print(f"✅ Table '{table_name}' created successfully")
        print(f"   Status: {table.table_status}")
        print(f"   ARN: {table.table_arn}")
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f"ℹ️  Table '{table_name}' already exists")
            return True
        print(f"❌ Error creating table: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    create_guidance_catalog_table()