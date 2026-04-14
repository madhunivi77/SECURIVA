"""
Create DynamoDB table used for compliance report persistence.

Usage:
  python tests/create_compliance_reports_table.py
  python tests/create_compliance_reports_table.py --table SecuriVAComplianceReports
"""

import argparse
import os
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
try:
    from dotenv import load_dotenv

    load_dotenv(env_path, override=True)
except ImportError:
    pass


def create_compliance_reports_table(table_name: str = "SecuriVAComplianceReports") -> bool:
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError as exc:
        print("❌ boto3 and botocore are required to create the compliance reports table")
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
                {"AttributeName": "report_id", "KeyType": "HASH"},
                {"AttributeName": "generated_at", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "report_id", "AttributeType": "S"},
                {"AttributeName": "generated_at", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
            Tags=[
                {"Key": "Environment", "Value": "Production"},
                {"Key": "Application", "Value": "SecuriVA"},
                {"Key": "Purpose", "Value": "ComplianceReports"},
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create compliance reports DynamoDB table")
    parser.add_argument(
        "--table",
        default=os.getenv("COMPLIANCE_REPORTS_DYNAMODB_TABLE", "SecuriVAComplianceReports"),
        help="DynamoDB table name",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(0 if create_compliance_reports_table(args.table) else 1)