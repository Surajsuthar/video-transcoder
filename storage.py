import tempfile
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from config import settings


class MinioClient:
    def __init__(self):
        self.client = Minio(
            f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        if not self.is_bucket_exists():
            self.client.make_bucket(settings.MINIO_BUCKET)

    def is_bucket_exists(self) -> bool:
        return self.client.bucket_exists(settings.MINIO_BUCKET)

    def download_file(self, object_name: str):
        try:
            response = self.client.get_object(settings.MINIO_BUCKET, object_name)
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(response.read())
                return temp_file.name
        except S3Error as e:
            raise e

    def upload_video(self, object_name: str, file_data: BinaryIO, file_size: int):
        try:
            self.client.put_object(bucket_name=settings.MINIO_BUCKET, object_name=object_name, data=file_data, length=file_size, content_type="video/mp4")
        except S3Error as e:
            raise e


minio_client = MinioClient()
