# ============================================================
# app/services/storage.py
# S3-compatible object storage (SeaweedFS).
# ============================================================
import io
import logging

import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)

# Singleton client
_client = None


def get_client():
    """Return a singleton S3 client (SeaweedFS-compatible)."""
    global _client
    if _client is None:
        protocol = "https" if settings.S3_SECURE else "http"
        endpoint_url = f"{protocol}://{settings.S3_ENDPOINT}"

        _client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )
    return _client


def ensure_bucket() -> None:
    """Create the default bucket if it does not exist."""
    client = get_client()
    try:
        client.head_bucket(Bucket=settings.S3_BUCKET)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in ("404", "NoSuchBucket"):
            client.create_bucket(Bucket=settings.S3_BUCKET)
            logger.info("Created S3 bucket: %s", settings.S3_BUCKET)
        else:
            raise


def upload_file(
    object_name: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    """
    Upload bytes to storage and return the object path.
    """
    ensure_bucket()
    client = get_client()
    client.put_object(
        Bucket=settings.S3_BUCKET,
        Key=object_name,
        Body=io.BytesIO(data),
        ContentType=content_type,
    )
    return f"{settings.S3_BUCKET}/{object_name}"


def download_file(object_name: str) -> bytes:
    """
    Download an object's bytes. Accepts either 'name' or 'bucket/name'.
    """
    if object_name.startswith(f"{settings.S3_BUCKET}/"):
        object_name = object_name[len(settings.S3_BUCKET) + 1 :]

    client = get_client()
    try:
        response = client.get_object(Bucket=settings.S3_BUCKET, Key=object_name)
        return response["Body"].read()
    except (BotoCoreError, ClientError) as exc:
        logger.error("Failed to download %s: %s", object_name, exc)
        raise


def delete_file(object_name: str) -> None:
    """Delete an object from storage."""
    if object_name.startswith(f"{settings.S3_BUCKET}/"):
        object_name = object_name[len(settings.S3_BUCKET) + 1 :]
    try:
        get_client().delete_object(Bucket=settings.S3_BUCKET, Key=object_name)
    except (BotoCoreError, ClientError) as exc:
        logger.warning("Failed to delete %s: %s", object_name, exc)


def get_presigned_url(object_name: str, expires_minutes: int = 60) -> str:
    """Generate a temporary download URL."""
    if object_name.startswith(f"{settings.S3_BUCKET}/"):
        object_name = object_name[len(settings.S3_BUCKET) + 1 :]
    return get_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": object_name},
        ExpiresIn=expires_minutes * 60,
    )
