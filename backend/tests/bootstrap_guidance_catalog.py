"""
Create, seed, and verify the DynamoDB guidance catalog in one fail-fast command.

Usage:
  python tests/bootstrap_guidance_catalog.py
  python tests/bootstrap_guidance_catalog.py --table SecuriVAGuidanceCatalog --region us-east-2
  python tests/bootstrap_guidance_catalog.py --clear-first
"""

import argparse
import os

from tests.create_guidance_catalog_table import create_guidance_catalog_table
from tests.seed_guidance_catalog_table import seed_guidance_catalog
from tests.verify_guidance_catalog_table import (
    build_parity_report,
    get_dynamodb_counts,
    get_local_counts,
    print_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap guidance catalog table (create + seed + verify)")
    parser.add_argument(
        "--table",
        default=os.getenv("GUIDANCE_CATALOG_DYNAMODB_TABLE", "SecuriVAGuidanceCatalog"),
        help="DynamoDB table name",
    )
    parser.add_argument(
        "--region",
        default=os.getenv("AWS_REGION", "us-east-2"),
        help="AWS region",
    )
    parser.add_argument(
        "--clear-first",
        action="store_true",
        help="Delete existing catalog items before seeding",
    )
    return parser.parse_args()


def get_dynamodb_table(table_name: str, region: str):
    """Build DynamoDB table handle for guidance catalog operations."""
    import boto3

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=region,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    return dynamodb.Table(table_name)


def run_bootstrap(table_name: str, region: str, clear_first: bool = False) -> int:
    """Run create -> seed -> verify in order, returning shell exit code."""
    print("Step 1/3: Ensuring guidance catalog table exists...")
    if not create_guidance_catalog_table(table_name):
        print("❌ Table creation failed")
        return 1

    print("Step 2/3: Seeding guidance catalog data...")
    if not seed_guidance_catalog(table_name, region, clear_first=clear_first):
        print("❌ Seeding failed")
        return 1

    print("Step 3/3: Verifying parity with local curated sources...")
    try:
        table = get_dynamodb_table(table_name, region)
    except ImportError:
        print("❌ boto3 is required for verification")
        return 1

    local_counts = get_local_counts()
    dynamo_counts = get_dynamodb_counts(table)
    report = build_parity_report(local_counts, dynamo_counts)
    print_report(report)

    if not report["match"]:
        print("❌ Verification failed: local and DynamoDB counts do not match")
        return 1

    print("✅ Guidance catalog bootstrap complete")
    return 0


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(run_bootstrap(args.table, args.region, clear_first=args.clear_first))
