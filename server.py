import asyncio
import io
import json
import uuid

import redis
from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse

from config import settings
from storage import minio_client
from tasks import handle_transcode

app = FastAPI()
r = redis.from_url(settings.REDIS_URL)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload(file: UploadFile):
    try:
        job_id = uuid.uuid4()
        object_name: str = f"{job_id}.mp4"
        file_bytes = await file.read()
        file_size = len(file_bytes)
        minio_client.upload_video(object_name, io.BytesIO(file_bytes), file_size)
        resolution = settings.RESOLUTION


        for key, value in resolution.items():
            handle_transcode.delay(object_name, key, str(job_id))

        return {"job_id": job_id}
    except Exception as e:
        raise e


async def status_generator(job_id: str):
    while True:
        statuses = r.hgetall(f"job:{job_id}")
        decoded = {k.decode(): v.decode() for k, v in statuses.items()}
        yield f"data: {json.dumps(decoded)}\n\n"
        all_resolutions = set(settings.RESOLUTION.keys())
        completed = {k for k, v in decoded.items() if v in ("done", "failed")}
        if all_resolutions == completed:
            break
        await asyncio.sleep(1)

@app.get("/status/{job_id}")
async def status(job_id: str):
    try:
        return StreamingResponse(
            status_generator(job_id),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise e
