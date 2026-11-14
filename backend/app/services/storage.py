import io
import json
import logging
import uuid
from minio import Minio
from minio.error import S3Error
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET

    def ensure_bucket(self) -> None:
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
        except S3Error as e:
            logger.error("Error ensuring MinIO bucket: %s", e)

    def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str = "image/jpeg",
    ) -> str:
        self.ensure_bucket()
        ext = filename.split(".")[-1] if "." in filename else "jpg"
        object_name = f"{uuid.uuid4().hex}.{ext}"

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=io.BytesIO(file_bytes),
            length=len(file_bytes),
            content_type=content_type,
        )

        # Public access URL:
        # Default is relative URL "/storage/products/<object_name>", which works
        # seamlessly in standard web browsers, mobile TMA, and through reverse proxy / tunnels
        # without breaking due to 'localhost' hostname resolution on remote devices!
        base_url = settings.MINIO_PUBLIC_URL.rstrip("/")
        if base_url.endswith(f"/{self.bucket}"):
            image_url = f"{base_url}/{object_name}"
        else:
            image_url = f"{base_url}/{self.bucket}/{object_name}"

        # If PUBLIC_BASE_URL is provided (e.g. https://xxx.trycloudflare.com) and base_url is relative, prefix it
        if settings.PUBLIC_BASE_URL and image_url.startswith("/"):
            image_url = f"{settings.PUBLIC_BASE_URL.rstrip('/')}{image_url}"

        return image_url


storage_service = StorageService()
