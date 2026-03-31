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
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_title_from_ai(prompt: str):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Return ONLY one short title (3-4 words). No explanations. No numbering. No prefixes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.3
        )
        title = response.choices[0].message.content.strip()
        title = title.split("\n")[0]          
        title = title.replace("Chat title ideas:", "")
        title = title.replace("Title:", "")
        title = title.strip()

        # remove numbering like "1."
        if title[:2].isdigit():
            title = title[2:].strip()

        # final cleanup
        title = title[:40]
        return title

    except Exception as e:
        print("Title generation error:", e)
        return "New Chat"

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
    title: str
    messages: List[ChatMessage]



# Abstract DB Interface

class BaseConnector:
    def save_chat(self, user_id: str, version: int, title: str, messages: List[Dict]):
        raise NotImplementedError

    def get_latest_chat(self, user_id: str) -> Optional[ChatRecord]:
        raise NotImplementedError

    def delete_latest_chat(self, user_id: str) -> bool:
        raise NotImplementedError
    
    def get_chat_by_version(self, user_id: str, version: int) -> Optional[ChatRecord]:
        raise NotImplementedError
    
    def delete_by_version(self, user_id: str, version: int) -> bool:
        raise NotImplementedError
    
    def list_user_chats(self, user_id: str) -> List[Dict]:
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
                title TEXT,
                messages TEXT,
                PRIMARY KEY (user_id, version)
            )
        """)
        self.conn.commit()

    def save_chat(self, user_id: str, version: int,title: str, messages: List[Dict]):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO chats VALUES (?, ?, ?,?)",
            (user_id, version,title, json.dumps(messages))
        )
        self.conn.commit()

    def get_latest_chat(self, user_id: str) -> Optional[ChatRecord]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT version,title, messages FROM chats
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
            title=row[1],
            messages=[ChatMessage(**m) for m in json.loads(row[2])]
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
    

    def get_chat_by_version(self, user_id: str, version: int) -> Optional[ChatRecord]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT title, messages FROM chats
            WHERE user_id = ? AND version = ?
        """, (user_id, version))
        row = cur.fetchone()

        if not row:
            return None

        return ChatRecord(
            user_id=user_id,
            version=version,
            title=row[0],
            messages=[ChatMessage(**m) for m in json.loads(row[1])]
        )
    
    def delete_by_version(self, user_id: str, version: int) -> bool:
        cur = self.conn.cursor()
        cur.execute("""
            DELETE FROM chats
            WHERE user_id = ? AND version = ?
        """, (user_id, version))
        self.conn.commit()
        return cur.rowcount > 0
    
    def list_user_chats(self, user_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT version, title FROM chats
            WHERE user_id = ?
            ORDER BY version DESC
        """, (user_id,))
        rows = cur.fetchall()
        return [
            {"version": row[0], "title": row[1]}
            for row in rows
        ]


# DynamoDB Connector (Production)
class DynamoDBConnector(BaseConnector):
    def __init__(self, table_name: str, region="us-east-2"):
        self.table = boto3.resource(
            "dynamodb",
            region_name=region
        ).Table(table_name)

    def save_chat(self, user_id: str, version: int, title: str, messages: List[Dict]):
        session_timestamp = str(int(time.time() * 1000))
        try:
            self.table.put_item(Item={
                "user_id": user_id,
                "session_timestamp": session_timestamp,
                "version": version,
                "title": title,
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
                title=item.get("title", f"Chat {item['version']}"),
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
    
    def get_chat_by_version(self, user_id: str, version: int) -> Optional[ChatRecord]:
        try:
            response = self.table.query(
                KeyConditionExpression=Key("user_id").eq(user_id),
                FilterExpression="version = :v",
                ExpressionAttributeValues={
                    ":v": version
                }
            )
            items = response.get("Items", [])
            if not items:
                return None
            
            item = items[0]
            return ChatRecord(
                user_id=user_id,
                version=item["version"],
                title=item.get("title", f"Chat {version}"),
                messages=[ChatMessage(**m) for m in item["messages"]]
            )
        except ClientError as e:
            raise RuntimeError(str(e))
    
    def delete_by_version(self, user_id: str, version: int) -> bool:
        try:
            response = self.table.query(
                KeyConditionExpression=Key("user_id").eq(user_id),
                FilterExpression="version = :v",
                ExpressionAttributeValues={
                    ":v": version
                }
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
    
    def list_user_chats(self, user_id: str) -> List[Dict]:
        try:
            response = self.table.query(
                KeyConditionExpression=Key("user_id").eq(user_id),
                ProjectionExpression="version, title",
                ScanIndexForward=False  # Descending order
            )
            items = response.get("Items", [])
            return [
                {"version": item["version"], "title": item.get("title", f"Chat {item['version']}")} 
                for item in items
            ]
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

        version = body.get("version")
        messages = body.get("messages")

        if not messages:
            return JSONResponse({"error": "Messages required"}, status_code=400)

        
        if version is None:
            latest = await asyncio.to_thread(db.get_latest_chat, user_id)
            version = 1 if not latest else latest.version + 1

            #
            assistant_messages = [
            m["content"] for m in messages 
            if m["role"] == "assistant" and len(m["content"].strip()) > 20
        ]

            first_assistant_message = assistant_messages[0] if assistant_messages else "New Chat"

            # 
            title = await generate_title_from_ai(first_assistant_message)

        else:
            existing = await asyncio.to_thread(
                db.get_chat_by_version,
                user_id,
                version
            )
            title = existing.title if existing else f"Chat {version}"

    
        await asyncio.to_thread(
            db.save_chat,
            user_id,
            version,
            title,
            messages
        )

    except Exception as e:
        return JSONResponse(
            {"error": str(e), "traceback": traceback.format_exc()},
            status_code=500
        )

    return JSONResponse({"status": "saved", "version": version})

async def get_latest_chat(request: Request):
    user_id =get_authenticated_user(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    chat = await asyncio.to_thread(db.get_latest_chat, user_id)
    if not chat:
        return JSONResponse({"error": "No chat found"}, status_code=404)

    return JSONResponse(chat.dict())


async def delete_chat_by_version(request: Request):
    user_id = get_authenticated_user(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    version = request.query_params.get("version")
    if not version:
        return JSONResponse({"error": "Version required"}, status_code=400)

    try:
        success = await asyncio.to_thread(
            db.delete_by_version,
            user_id,
            int(version)
        )
        
        if success:
            return JSONResponse({"status": "deleted"})
        else:
            return JSONResponse({"error": "Chat not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(
            {"error": str(e), "traceback": traceback.format_exc()},
            status_code=500
        )

async def list_chats(request: Request):
    user_id = get_authenticated_user(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    try:
        conversations = await asyncio.to_thread(
            db.list_user_chats,
            user_id
        )
        return JSONResponse({"conversations": conversations})
    except Exception as e:
        return JSONResponse(
            {"error": str(e), "traceback": traceback.format_exc()},
            status_code=500
        )
async def get_chat_by_version(request: Request):
    user_id = get_authenticated_user(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    version = request.query_params.get("version")

    if not version:
        return JSONResponse({"error": "Version required"}, status_code=400)

    try:
        chat = await asyncio.to_thread(
            db.get_chat_by_version,
            user_id,
            int(version)
        )
        
        if not chat:
            return JSONResponse({"error": "Chat not found"}, status_code=404)

        return JSONResponse({
            "version": chat.version,
            "title": chat.title,
            "messages": [msg.dict() for msg in chat.messages]
        })
    except Exception as e:
        return JSONResponse(
            {"error": str(e), "traceback": traceback.format_exc()},
            status_code=500
        )


# Starlette App
routes = [
    Route("/save", save_chat, methods=["POST"]),
    Route("/latest", get_latest_chat, methods=["GET"]),
    Route("/delete_by_version", delete_chat_by_version, methods=["DELETE"]),
    Route("/list", list_chats, methods=["GET"]),
    Route("/get", get_chat_by_version, methods=["GET"]),
]

db_app = Starlette(routes=routes)
