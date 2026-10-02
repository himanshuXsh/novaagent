import os
import boto3
from botocore.exceptions import ClientError
from backend.shared.logger import get_logger

logger = get_logger(__name__)


class StorageClient:
    def __init__(self):
        self.bucket_name = 'novaagent-bucket'
        self.client = None
        self.is_connected = False
        try:
            minio_endpoint = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")
            self.client = boto3.client(
                's3',
                endpoint_url=minio_endpoint,
                aws_access_key_id=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
                aws_secret_access_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin"),
                region_name='us-east-1'
            )
            self._ensure_bucket_exists()
        except Exception as e:
            logger.warning(f"MinIO client init skipped/failed: {e}")

    def _ensure_bucket_exists(self):
        if not self.client:
            return
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            self.is_connected = True
        except ClientError:
            try:
                self.client.create_bucket(Bucket=self.bucket_name)
                self.is_connected = True
            except Exception as e:
                logger.warning(f"Could not create MinIO bucket. Error: {e}")
        except Exception as e:
            logger.warning(f"Could not connect to MinIO. Error: {e}")

    def upload_file(self, file_path: str, object_name: str) -> str:
        if self.client and self.is_connected:
            try:
                self.client.upload_file(file_path, self.bucket_name, object_name)
                return self.get_presigned_url(object_name)
            except Exception as e:
                logger.warning(f"MinIO upload_file failed ({e}), falling back to local file route.")
        return f"/api/v1/agents/documents/raw/{object_name}"

    def get_presigned_url(self, object_name: str, expiration=3600) -> str:
        if self.client and self.is_connected:
            try:
                return self.client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': object_name},
                    ExpiresIn=expiration
                )
            except Exception:
                pass
        return f"/api/v1/agents/documents/raw/{object_name}"

storage = StorageClient()
