import io
import json
import logging
import uuid
from minio import Minio
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        endpoint = settings.MINIO_ENDPOINT.strip()
        secure = settings.MINIO_SECURE

        if endpoint.startswith("https://"):
            endpoint = endpoint.replace("https://", "")
            secure = True
        elif endpoint.startswith("http://"):
            endpoint = endpoint.replace("http://", "")
        endpoint = endpoint.rstrip("/")

        self.storage_type = "r2" if "r2.cloudflarestorage" in endpoint else "minio"
        try:
            self.client = Minio(
                endpoint=endpoint,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=secure,
            )
        except Exception as e:
            logger.error("Failed to init S3/MinIO client: %s", e)
            self.client = None

        self.bucket = settings.MINIO_BUCKET.strip()

    def ensure_bucket(self) -> None:
        if not self.client:
            raise RuntimeError("S3/MinIO client not initialized")
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info("Bucket %s created.", self.bucket)

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
            logger.info("Bucket ensure note: %s", e)

    def upload_file(self, file_bytes: bytes, filename: str, content_type: str = "image/jpeg") -> str:
        if not self.client:
            raise RuntimeError("S3/MinIO хранилище не инициализировано: проверьте настройки S3/MinIO")

        ext = filename.split(".")[-1] if "." in filename else "jpg"
        object_name = f"{uuid.uuid4().hex}.{ext}"

        try:
            self.ensure_bucket()
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=io.BytesIO(file_bytes),
                length=len(file_bytes),
                content_type=content_type,
            )
        except Exception as e:
            logger.error("S3/MinIO put_object failed: %s", e)
            raise RuntimeError(f"Ошибка сохранения файла в S3/MinIO: {str(e)}")

        base_url = settings.MINIO_PUBLIC_URL.rstrip("/")
        if "r2.dev" in base_url or base_url.endswith(f"/{self.bucket}"):
            return f"{base_url}/{object_name}"
        return f"{base_url}/{self.bucket}/{object_name}"

    def check_health(self) -> tuple[bool, str]:
        if not self.client:
            return False, "client not configured"
        try:
            exists = self.client.bucket_exists(self.bucket)
            if not exists:
                return False, f"bucket '{self.bucket}' does not exist"

            # Probe write & read to verify real storage I/O
            probe_key = ".health_probe"
            probe_data = b"ok"
            self.client.put_object(self.bucket, probe_key, io.BytesIO(probe_data), len(probe_data))
            obj = self.client.get_object(self.bucket, probe_key)
            obj.read()
            obj.close()
            obj.release_conn()
            return True, f"ok ({self.storage_type})"
        except Exception as e:
            return False, f"error ({self.storage_type}): {str(e)}"


storage_service = StorageService()
