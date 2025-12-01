import boto3
import os
import json
from botocore.client import Config
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request

class S3Service:
    def __init__(self):
        self.bucket_name = os.getenv("AWS_S3_BUCKET")
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION"),
            config=Config(signature_version="s3v4")
        )

    def upload_json(self, key: str, data: dict):
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=json.dumps(datac),
            ContentType="application/json"
        )
        return {"status": "uploaded", "key": key}

    def load_json(self, key: str):
        obj = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        return json.loads(obj["Body"].read())

    def list_files(self, prefix=""):
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        return [item["Key"] for item in response.get("Contents", [])]

    def delete_file(self, key: str):
        self.s3.delete_object(Bucket=self.bucket_name, Key=key)
        return {"status": "deleted", "key": key}
    


s3_service = S3Service()

# ---- Upload Endpoint ----
async def upload_file(request: Request):
    try:
        form = await request.form()
        upload_file = form.get("file")
        if not upload_file:
            return JSONResponse({"error": "No file provided"}, status_code=400)

        file_key = upload_file.filename
        content = await upload_file.read()

        # Try JSON upload, fallback to raw bytes
        try:
            import json
            data = json.loads(content.decode())
            result = s3_service.upload_json(file_key, data)
        except:
            s3_service.s3.put_object(
                Bucket=s3_service.bucket_name,
                Key=file_key,
                Body=content
            )
            result = {"status": "uploaded", "key": file_key}

        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---- List Files Endpoint ----
async def list_files(request: Request):
    try:
        prefix = request.query_params.get("prefix", "")
        files = s3_service.list_files(prefix=prefix)
        return JSONResponse({"files": files})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---- Download Endpoint ----
async def download_file(request: Request):
    try:
        key = request.query_params.get("key")
        if not key:
            return JSONResponse({"error": "Key parameter required"}, status_code=400)
        obj = s3_service.s3.get_object(Bucket=s3_service.bucket_name, Key=key)
        content = obj["Body"].read()
        return JSONResponse({"file": content.decode()})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---- Delete Endpoint ----
async def delete_file(request: Request):
    try:
        key = request.query_params.get("key")
        if not key:
            return JSONResponse({"error": "Key parameter required"}, status_code=400)
        result = s3_service.delete_file(key)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


\
s3_routes = [
    Route("/upload", upload_file, methods=["POST"]),
    Route("/list", list_files, methods=["GET"]),
    Route("/download", download_file, methods=["GET"]),
    Route("/delete", delete_file, methods=["DELETE"]),
]


s3_app = Starlette(routes=s3_routes)
