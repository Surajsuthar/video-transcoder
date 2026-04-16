from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379"
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "videos"

    RESOLUTION: dict = {
        "480": {
            "width": 854,
            "height": 480,
            "bitrate": "1M"
        },
        "720": {
            "width": 1280,
            "height": 720,
            "bitrate": "2.5M"
        },
        "1080": {
            "width": 1920,
            "height": 1080,
            "bitrate": "5M"
        },
        "4k": {
            "width": 3840,
            "height": 2160,
            "bitrate": "15M"
        }
    }


settings = Settings()
