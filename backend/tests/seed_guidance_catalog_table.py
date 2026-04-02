"""
Seed the guidance catalog DynamoDB table with curated local guidance content.

Usage:
  python tests/seed_guidance_catalog_table.py
  python tests/seed_guidance_catalog_table.py --table SecuriVAGuidanceCatalog
  python tests/seed_guidance_catalog_table.py --clear-first
"""

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

from my_app.server.guidance_store import LocalFileGuidanceStore


env_path = Path(__file__).parent.parent / ".env"
try:
    from dotenv import load_dotenv

    load_dotenv(env_path, override=True)
except ImportError:
    pass


def build_seed_items() -> list[dict]:
    """Build deterministic seed items from local guidance sources."""
    store = LocalFileGuidanceStore()
    timestamp = datetime.now(timezone.utc).isoformat()
    items: list[dict] = []

    for content_id, content in store.get_procedures().items():
        items.append(
            {
                "content_type": "procedure",
                "content_id": content_id,
                "content": content,
                "updated_at": timestamp,
            }
        )

    for content_id, content in store.get_decision_trees().items():
        items.append(
            {
                "content_type": "decision_tree",
                "content_id": content_id,
                "content": content,
                "updated_at": timestamp,
            }
        )

    for content_id, content in store.get_examples().items():
        items.append(
            {
                "content_type": "example",
                "content_id": content_id,
                "content": content,
                "updated_at": timestamp,
            }
        )

    return items


def clear_existing_items(table):
    """Delete existing catalog items for all supported content types."""
    from boto3.dynamodb.conditions import Key

    content_types = ["procedure", "decision_tree", "example"]
    for content_type in content_types:
        response = table.query(
            KeyConditionExpression=Key("content_type").eq(content_type)
        )
        items = response.get("Items", [])
        if not items:
            continue

        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(
                    Key={
                        "content_type": item["content_type"],
                        "content_id": item["content_id"],
                    }
                )


def seed_guidance_catalog(table_name: str, region: str, clear_first: bool = False) -> bool:
    """Seed the guidance catalog table from local files."""
    import boto3

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=region,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    table = dynamodb.Table(table_name)

    if clear_first:
        print("Clearing existing guidance catalog items...")
        clear_existing_items(table)

    items = build_seed_items()
    with table.batch_writer(overwrite_by_pkeys=["content_type", "content_id"]) as batch:
        for item in items:
            batch.put_item(Item=item)

    print(f"Seeded {len(items)} guidance catalog items into '{table_name}'")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed DynamoDB guidance catalog table")
    parser.add_argument(
        "--table",
        default=os.getenv("GUIDANCE_CATALOG_DYNAMODB_TABLE", "SecuriVAGuidanceCatalog"),
        help="DynamoDB table name (default: GUIDANCE_CATALOG_DYNAMODB_TABLE or SecuriVAGuidanceCatalog)",
    )
    parser.add_argument(
        "--region",
        default=os.getenv("AWS_REGION", "us-east-2"),
        help="AWS region (default: AWS_REGION or us-east-2)",
    )
    parser.add_argument(
        "--clear-first",
        action="store_true",
        help="Delete existing guidance catalog items before seeding",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        seed_guidance_catalog(args.table, args.region, clear_first=args.clear_first)
        print("Guidance catalog seeding complete")
    except Exception as exc:
        print(f"Failed to seed guidance catalog: {exc}")
        raise
