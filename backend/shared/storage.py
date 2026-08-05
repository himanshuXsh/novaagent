import os

import boto3
from botocore.exceptions import ClientError


class StorageClient:
    def __init__(self):
        minio_endpoint = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")
        self.client = boto3.client(
            's3',
            endpoint_url=minio_endpoint,
            aws_access_key_id=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
            aws_secret_access_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin"),
            region_name='us-east-1'
        )
        self.bucket_name = 'novaagent-bucket'
        self._ensure_bucket_exists()
        
    def _ensure_bucket_exists(self):
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            self.client.create_bucket(Bucket=self.bucket_name)
            
    def upload_file(self, file_path: str, object_name: str) -> str:
        self.client.upload_file(file_path, self.bucket_name, object_name)
        return self.get_presigned_url(object_name)
        
    def get_presigned_url(self, object_name: str, expiration=3600) -> str:
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': object_name},
            ExpiresIn=expiration
        )

storage = StorageClient()
