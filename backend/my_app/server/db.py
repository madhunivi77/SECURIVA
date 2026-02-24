from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
from pydantic import BaseModel
import asyncio
from typing import List, Dict, Optional
import sqlite3
import json
import boto3
import time
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import traceback
from pathlib import Path
from .api_key_manager import validate_api_key


def get_authenticated_user(request: Request):
    api_key = request.cookies.get("api_key")

    if not api_key:
        print("No api_key cookie found")
        return None

    oauth_file = Path(__file__).parent / "oauth.json"

    user_id = validate_api_key(api_key, oauth_file)

    if not user_id:
        print("Invalid api_key")
        return None

    return user_id

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRecord(BaseModel):
    user_id: str
    version: int
    messages: List[ChatMessage]



# Abstract DB Interface

class BaseConnector:
    def save_chat(self, user_id: str, version: int, messages: List[Dict]):
        raise NotImplementedError

    def get_latest_chat(self, user_id: str) -> Optional[ChatRecord]:
        raise NotImplementedError

    def delete_latest_chat(self, user_id: str) -> bool:
        raise NotImplementedError



# SQLite Connector 


class SQLiteConnector(BaseConnector):
    def __init__(self, db_path="local.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                user_id TEXT,
                version INTEGER,
                messages TEXT,
                PRIMARY KEY (user_id, version)
            )
        """)
        self.conn.commit()

    def save_chat(self, user_id: str, version: int, messages: List[Dict]):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO chats VALUES (?, ?, ?)",
            (user_id, version, json.dumps(messages))
        )
        self.conn.commit()

    def get_latest_chat(self, user_id: str) -> Optional[ChatRecord]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT version, messages FROM chats
            WHERE user_id = ?
            ORDER BY version DESC
            LIMIT 1
        """, (user_id,))
        row = cur.fetchone()

        if not row:
            return None

        return ChatRecord(
            user_id=user_id,
            version=row[0],
            messages=[ChatMessage(**m) for m in json.loads(row[1])]
        )

    def delete_latest_chat(self, user_id: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT version FROM chats
            WHERE user_id = ?
            ORDER BY version DESC
            LIMIT 1
        """, (user_id,))
        row = cur.fetchone()

        if not row:
            return False

        cur.execute("""
            DELETE FROM chats
            WHERE user_id = ? AND version = ?
        """, (user_id, row[0]))
        self.conn.commit()
        return True



# DynamoDB Connector (Production)


class DynamoDBConnector(BaseConnector):
    def __init__(self, table_name: str, region="us-east-2"):
        self.table = boto3.resource(
            "dynamodb",
            region_name=region
        ).Table(table_name)

    def save_chat(self, user_id: str, version: int, messages: List[Dict]):
        session_timestamp = str(int(time.time() * 1000))
        try:
            self.table.put_item(Item={
                "user_id": user_id,
                "session_timestamp": session_timestamp,
                "version": version,
                "messages": messages
            })
        except ClientError as e:
            raise RuntimeError(str(e))

    def get_latest_chat(self, user_id: str) -> Optional[ChatRecord]:
        try:
            response = self.table.query(
                KeyConditionExpression=Key("user_id").eq(user_id),
                ScanIndexForward=False,
                Limit=1
            )
            items = response.get("Items", [])
            if not items:
                return None

            item = items[0]
            return ChatRecord(
                user_id=user_id,
                version=item["version"],
                messages=[ChatMessage(**m) for m in item["messages"]]
            )
        except ClientError as e:
            raise RuntimeError(str(e))

    def delete_latest_chat(self, user_id: str) -> bool:
        try:
            response = self.table.query(
                KeyConditionExpression=Key("user_id").eq(user_id),
                ScanIndexForward=False,
                Limit=1
            )
            items = response.get("Items", [])
            if not items:
                return False

            item = items[0]
            self.table.delete_item(
                Key={
                    "user_id": item["user_id"],
                    "session_timestamp": item["session_timestamp"]
                }
            )
            return True
        except ClientError as e:
            raise RuntimeError(str(e))



# DB Selection


USE_DYNAMO = False  # set True in production
db = DynamoDBConnector("SecuriVAChats") if USE_DYNAMO else SQLiteConnector()


# Route Handlers
async def save_chat(request: Request):
    user_id = get_authenticated_user(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
  
    try:
        body = await request.json()
        messages = [ChatMessage(**m) for m in body]
    except Exception as e:
        return JSONResponse({"error": f"Invalid JSON body: {str(e)}"}, status_code=400)

    try:
        latest = await asyncio.to_thread(db.get_latest_chat, user_id)
        new_version = 1 if not latest else latest.version + 1

        await asyncio.to_thread(
            db.save_chat,
            user_id,
            new_version,
            [m.dict() for m in messages]
        )
    except Exception as e:
        return JSONResponse(
            {"error": str(e), "traceback": traceback.format_exc()},
            status_code=500
        )

    return JSONResponse({"status": "saved", "version": new_version})


async def get_latest_chat(request: Request):
    user_id =get_authenticated_user(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    chat = await asyncio.to_thread(db.get_latest_chat, user_id)
    if not chat:
        return JSONResponse({"error": "No chat found"}, status_code=404)

    return JSONResponse(chat.dict())


async def delete_latest_chat(request: Request):
    user_id = get_authenticated_user(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    try:
        deleted = await asyncio.to_thread(db.delete_latest_chat, user_id)
        if not deleted:
            return JSONResponse({"error": "No chat to delete"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    return JSONResponse({"status": "deleted"})

async def list_chats(request: Request):
    user_id = get_authenticated_user(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    cur = db.conn.cursor()
    cur.execute("""
        SELECT version FROM chats
        WHERE user_id = ?
        ORDER BY version DESC
    """, (user_id,))
    
    rows = cur.fetchall()

    conversations = [
        {"version": row[0], "title": f"Conversation {row[0]}"}
        for row in rows
    ]

    return JSONResponse({"conversations": conversations})
async def get_chat_by_version(request: Request):
    user_id = get_authenticated_user(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    version = request.query_params.get("version")

    if not version:
        return JSONResponse({"error": "Version required"}, status_code=400)

    cur = db.conn.cursor()
    cur.execute("""
        SELECT messages FROM chats
        WHERE user_id = ? AND version = ?
    """, (user_id, int(version)))

    row = cur.fetchone()

    if not row:
        return JSONResponse({"error": "Chat not found"}, status_code=404)

    return JSONResponse({
        "version": int(version),
        "messages": json.loads(row[0])
    })


# Starlette App

routes = [
    Route("/save", save_chat, methods=["POST"]),
    Route("/latest", get_latest_chat, methods=["GET"]),
    Route("/delete", delete_latest_chat, methods=["DELETE"]),
    Route("/list", list_chats, methods=["GET"]),
]

db_app = Starlette(routes=routes)
