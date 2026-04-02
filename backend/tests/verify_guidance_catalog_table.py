"""
Verify guidance catalog parity between local curated sources and DynamoDB.

Usage:
  python tests/verify_guidance_catalog_table.py
  python tests/verify_guidance_catalog_table.py --table SecuriVAGuidanceCatalog
  python tests/verify_guidance_catalog_table.py --strict
"""

import argparse
import os
from pathlib import Path

from my_app.server.guidance_store import LocalFileGuidanceStore


env_path = Path(__file__).parent.parent / ".env"
try:
    from dotenv import load_dotenv

    load_dotenv(env_path, override=True)
except ImportError:
    pass


CONTENT_TYPES = ["procedure", "decision_tree", "example"]


def get_local_counts() -> dict[str, int]:
    """Count local guidance records by content type."""
    store = LocalFileGuidanceStore()
    return {
        "procedure": len(store.get_procedures()),
        "decision_tree": len(store.get_decision_trees()),
        "example": len(store.get_examples()),
    }


def query_items_for_type(table, content_type: str) -> list[dict]:
    """Query all table items for a content_type with pagination."""
    query_kwargs = {"content_type": content_type}
    try:
        from boto3.dynamodb.conditions import Key

        query_kwargs["KeyConditionExpression"] = Key("content_type").eq(content_type)
    except ImportError:
        pass

    items: list[dict] = []
    while True:
        response = table.query(**query_kwargs)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        query_kwargs["ExclusiveStartKey"] = last_key
    return items


def get_dynamodb_counts(table) -> dict[str, int]:
    """Count DynamoDB guidance records by content type."""
    counts: dict[str, int] = {}
    for content_type in CONTENT_TYPES:
        items = query_items_for_type(table, content_type)
        counts[content_type] = len(items)
    return counts


def build_parity_report(local_counts: dict[str, int], dynamo_counts: dict[str, int]) -> dict:
    """Build parity report with per-type deltas and aggregate totals."""
    per_type = {}
    all_equal = True

    for content_type in CONTENT_TYPES:
        local_count = local_counts.get(content_type, 0)
        dynamo_count = dynamo_counts.get(content_type, 0)
        delta = dynamo_count - local_count
        is_equal = delta == 0
        all_equal = all_equal and is_equal
        per_type[content_type] = {
            "local": local_count,
            "dynamodb": dynamo_count,
            "delta": delta,
            "match": is_equal,
        }

    total_local = sum(local_counts.values())
    total_dynamodb = sum(dynamo_counts.values())

    return {
        "match": all_equal and total_local == total_dynamodb,
        "local_total": total_local,
        "dynamodb_total": total_dynamodb,
        "total_delta": total_dynamodb - total_local,
        "per_type": per_type,
    }


def print_report(report: dict):
    """Pretty-print parity report."""
    print("Guidance Catalog Parity Report")
    print("=" * 40)
    print(f"Overall match: {report['match']}")
    print(f"Local total: {report['local_total']}")
    print(f"DynamoDB total: {report['dynamodb_total']}")
    print(f"Total delta: {report['total_delta']}")
    print("-" * 40)
    for content_type in CONTENT_TYPES:
        row = report["per_type"][content_type]
        print(
            f"{content_type:14} local={row['local']:4}  dynamodb={row['dynamodb']:4}  "
            f"delta={row['delta']:4}  match={row['match']}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify guidance catalog parity with DynamoDB")
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
        "--strict",
        action="store_true",
        help="Exit with code 1 when counts do not match",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        import boto3
    except ImportError as exc:
        print("boto3 is required to verify DynamoDB catalog parity")
        raise exc

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=args.region,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    table = dynamodb.Table(args.table)

    local_counts = get_local_counts()
    dynamo_counts = get_dynamodb_counts(table)
    report = build_parity_report(local_counts, dynamo_counts)
    print_report(report)

    if args.strict and not report["match"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
