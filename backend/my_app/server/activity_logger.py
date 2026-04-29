"""
Unified activity logger for SECURIVA.
Captures all system events: signins, logouts, chats, tool calls, voice sessions, errors.
Stores in DynamoDB (production) or local JSON file (development).
"""

import json
import os
import time
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


# Config
USE_DYNAMO = os.getenv("USE_DYNAMO_LOGS", "false").lower() == "true"
TABLE_NAME = "SecuriVALogs"
REGION = "us-east-2"
LOG_TTL_DAYS = 90

# Local file fallback
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_FILE = LOG_DIR / "activity.json"


def _get_table():
    return boto3.resource("dynamodb", region_name=REGION).Table(TABLE_NAME)


def _convert_floats(obj):
    """DynamoDB doesn't support float — convert to Decimal."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _convert_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_floats(i) for i in obj]
    return obj


def log_activity(
    event_type: str,
    user_email: Optional[str] = None,
    user_id: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
    status: str = "success",
    error: Optional[str] = None,
):
    """
    Log a system activity event.

    event_type: signin, logout, chat, tool_call, voice_session, sms, error
    """
    timestamp = datetime.utcnow().isoformat()

    entry = {
        "event_type": event_type,
        "timestamp": timestamp,
        "status": "error" if error else status,
        "user_email": user_email,
        "user_id": user_id,
    }

    if details:
        entry["details"] = details
    if error:
        entry["error"] = error

    if USE_DYNAMO:
        _write_dynamo(entry)
    else:
        _write_file(entry)


def _write_dynamo(entry: dict):
    """Write log entry to DynamoDB."""
    try:
        table = _get_table()
        item = _convert_floats(entry)

        # Add a unique suffix to timestamp to avoid collisions
        item["timestamp"] = item["timestamp"] + f"#{uuid.uuid4().hex[:8]}"

        # TTL: auto-delete after LOG_TTL_DAYS
        item["ttl"] = int(time.time()) + (LOG_TTL_DAYS * 86400)

        # Remove None values (DynamoDB doesn't like them)
        item = {k: v for k, v in item.items() if v is not None}

        table.put_item(Item=item)
    except Exception as e:
        print(f"DynamoDB activity log write failed: {e}")
        # Fall back to file
        _write_file(entry)


def _write_file(entry: dict):
    """Write log entry to local JSON file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Activity log write failed: {e}")


def get_activity_logs(
    limit: int = 200,
    event_filter: Optional[str] = None,
) -> list:
    """Read recent activity logs, newest first."""
    if USE_DYNAMO:
        return _read_dynamo(limit, event_filter)
    else:
        return _read_file(limit, event_filter)


def _read_dynamo(limit: int, event_filter: Optional[str] = None) -> list:
    """Read logs from DynamoDB."""
    try:
        table = _get_table()
        all_logs = []

        # If filtering by event type, query that partition directly
        if event_filter:
            response = table.query(
                KeyConditionExpression=Key("event_type").eq(event_filter),
                ScanIndexForward=False,
                Limit=limit,
            )
            all_logs = response.get("Items", [])
        else:
            # Query each event type partition
            event_types = ["signin", "logout", "chat", "tool_call", "voice_session", "sms", "error"]
            for et in event_types:
                response = table.query(
                    KeyConditionExpression=Key("event_type").eq(et),
                    ScanIndexForward=False,
                    Limit=limit,
                )
                all_logs.extend(response.get("Items", []))

        # Sort all by timestamp descending, strip uuid suffix for display
        for log in all_logs:
            log["event"] = log.pop("event_type", "unknown")
            # Clean the uuid suffix from timestamp for display
            ts = log.get("timestamp", "")
            if "#" in ts:
                log["timestamp"] = ts.split("#")[0]
            # Convert Decimals back to numbers for JSON serialization
            log = _decimal_to_num(log)

        all_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return all_logs[:limit]

    except Exception as e:
        print(f"DynamoDB activity log read failed: {e}")
        return _read_file(limit, event_filter)


def _decimal_to_num(obj):
    """Convert Decimal back to int/float for JSON serialization."""
    if isinstance(obj, Decimal):
        return int(obj) if obj == int(obj) else float(obj)
    if isinstance(obj, dict):
        return {k: _decimal_to_num(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decimal_to_num(i) for i in obj]
    return obj


def _read_file(limit: int, event_filter: Optional[str] = None) -> list:
    """Read logs from local JSON file."""
    if not LOG_FILE.exists():
        return []

    try:
        logs = []
        with open(LOG_FILE, "r") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    # Normalize: file entries use event_type, API expects event
                    if "event_type" in entry and "event" not in entry:
                        entry["event"] = entry.pop("event_type")
                    if event_filter and entry.get("event") != event_filter:
                        continue
                    logs.append(entry)
        return logs[-limit:][::-1]
    except Exception:
        return []
