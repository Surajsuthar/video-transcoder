import os
import uuid

import redis
from celery import Celery

from config import settings
from storage import minio_client
from transcode import transcode_video

celery_client = Celery("tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
r = redis.from_url(settings.REDIS_URL)

@celery_client.task
def handle_transcode(object_name: str, resolution: str, job_id: str):
    file_path = None
    output_path = None
    try:
        file_path = minio_client.download_file(object_name)
        video_config = settings.RESOLUTION[resolution]
        width, height, bitrate = video_config["width"], video_config["height"], video_config["bitrate"]
        output_path = transcode_video(file_path, width, height, bitrate, resolution)
        file_size = os.path.getsize(output_path)
        processed_file_path = f"{uuid.uuid4()}_{resolution}.mp4"
        with open(output_path, "rb") as f:
            minio_client.upload_video(processed_file_path, f, file_size)

        r.hset(f"job:{job_id}", resolution, "done")

    except Exception as e:
        r.hset(f"job:{job_id}", resolution, "failed")
        raise e

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if output_path and os.path.exists(output_path):
            os.remove(output_path)
