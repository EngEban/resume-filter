# ============================================================
# app/services/storage.py
# MinIO / S3 storage helpers for resume files.
# ============================================================
import io
import logging
from datetime import timedelta

from minio import Minio
from minio.error import S3Error

from app.core.config import settings

logger = logging.getLogger(__name__)


_client: Minio | None = None


def get_client() -> Minio:
    """Return a singleton MinIO client."""
    global _client
    if _client is None:
        _client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
    return _client


def ensure_bucket() -> None:
    """Create the default bucket if it does not exist."""
    client = get_client()
    if not client.bucket_exists(settings.MINIO_BUCKET):
        client.make_bucket(settings.MINIO_BUCKET)
        logger.info("Created MinIO bucket: %s", settings.MINIO_BUCKET)


def upload_file(
    object_name: str, data: bytes, content_type: str = "application/octet-stream"
) -> str:
    """
    Upload bytes to MinIO and return the object path.
    """
    ensure_bucket()
    client = get_client()
    client.put_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_name,
        data=io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return f"{settings.MINIO_BUCKET}/{object_name}"


def download_file(object_name: str) -> bytes:
    """
    Download an object's bytes. Accepts either a raw name or 'bucket/name'.
    """
    if object_name.startswith(f"{settings.MINIO_BUCKET}/"):
        object_name = object_name[len(settings.MINIO_BUCKET) + 1 :]

    client = get_client()
    response = None
    try:
        response = client.get_object(settings.MINIO_BUCKET, object_name)
        return response.read()
    except S3Error as exc:
        logger.error("Failed to download %s: %s", object_name, exc)
        raise
    finally:
        if response is not None:
            response.close()
            response.release_conn()


def delete_file(object_name: str) -> None:
    """Delete an object from MinIO."""
    if object_name.startswith(f"{settings.MINIO_BUCKET}/"):
        object_name = object_name[len(settings.MINIO_BUCKET) + 1 :]
    try:
        get_client().remove_object(settings.MINIO_BUCKET, object_name)
    except S3Error as exc:
        logger.warning("Failed to delete %s: %s", object_name, exc)


def get_presigned_url(object_name: str, expires_minutes: int = 60) -> str:
    """Generate a temporary download URL."""
    if object_name.startswith(f"{settings.MINIO_BUCKET}/"):
        object_name = object_name[len(settings.MINIO_BUCKET) + 1 :]
    return get_client().presigned_get_object(
        settings.MINIO_BUCKET,
        object_name,
        expires=timedelta(minutes=expires_minutes),
    )
