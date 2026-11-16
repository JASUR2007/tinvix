import io
import json
import logging
import os
import uuid
from minio import Minio
from minio.error import S3Error
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        try:
            self.client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
        except Exception as e:
            logger.warning("MinIO client init warning: %s", e)
            self.client = None
        self.bucket = settings.MINIO_BUCKET

    def ensure_bucket(self) -> None:
        if not self.client:
            return
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info("Bucket %s created.", self.bucket)

            # Set public read policy for the bucket so clients can display photos
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicRead",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket}/*"],
                    }
                ],
            }
            self.client.set_bucket_policy(self.bucket, json.dumps(policy))
        except Exception as e:
            logger.warning("Could not ensure MinIO bucket (%s), will fallback to local storage if needed.", e)

    def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str = "image/jpeg",
    ) -> str:
        ext = filename.split(".")[-1] if "." in filename else "jpg"
        object_name = f"{uuid.uuid4().hex}.{ext}"
        image_url = ""

        # Try MinIO first
        try:
            if self.client:
                self.ensure_bucket()
                self.client.put_object(
                    bucket_name=self.bucket,
                    object_name=object_name,
                    data=io.BytesIO(file_bytes),
                    length=len(file_bytes),
                    content_type=content_type,
                )
                base_url = settings.MINIO_PUBLIC_URL.rstrip("/")
                if base_url.endswith(f"/{self.bucket}"):
                    image_url = f"{base_url}/{object_name}"
                else:
                    image_url = f"{base_url}/{self.bucket}/{object_name}"
        except Exception as e:
            logger.warning("MinIO put_object failed (%s), saving to local static storage...", e)

        # Fallback to local static storage if MinIO is not available (e.g. Render cloud deployment)
        if not image_url:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            upload_dir = os.path.join(base_dir, "static", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            with open(os.path.join(upload_dir, object_name), "wb") as f:
                f.write(file_bytes)
            image_url = f"/storage/products/{object_name}"

        # If PUBLIC_BASE_URL is set, prepend it
        if settings.PUBLIC_BASE_URL and image_url.startswith("/"):
            image_url = f"{settings.PUBLIC_BASE_URL.rstrip('/')}{image_url}"

        return image_url


storage_service = StorageService()
