"""
app/integrations/storage/local_provider.py

Local disk storage provider for development.
Saves files under the configured UPLOAD_DIR and serves them via the
/uploads static mount that is registered in main.py.

In production, swap this for an S3Provider or GCSProvider that implements
the same AbstractStorageProvider interface — no service layer changes needed.
"""
import hashlib
import logging
import os
import uuid
from pathlib import Path

from app.core.config import settings
from app.integrations.storage.base import AbstractStorageProvider

logger = logging.getLogger(__name__)


class LocalStorageProvider(AbstractStorageProvider):
    """
    Stores files on the local filesystem under UPLOAD_DIR.
    Returns public URLs relative to the backend's /uploads static mount.
    """

    def __init__(self, upload_dir: str | None = None, base_url: str | None = None):
        self.upload_dir = Path(upload_dir or settings.UPLOAD_DIR)
        self.base_url = (base_url or settings.UPLOAD_BASE_URL).rstrip("/")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload(self, file_data: bytes, file_name: str, mime_type: str) -> str:
        """
        Save file_data to disk under a UUID-based key to avoid collisions.

        Returns:
            storage_key — relative path within upload_dir, e.g. "abc123/photo.jpg"
        """
        # Use a unique subdirectory per upload to avoid name collisions
        folder = uuid.uuid4().hex
        safe_name = Path(file_name).name  # strip any path traversal attempts
        storage_key = f"{folder}/{safe_name}"
        dest = self.upload_dir / folder / safe_name

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(file_data)

        logger.info(f"LocalStorageProvider: uploaded {len(file_data)} bytes → {storage_key}")
        return storage_key

    async def delete(self, storage_key: str) -> None:
        """Remove a previously uploaded file from disk."""
        target = self.upload_dir / storage_key
        try:
            target.unlink(missing_ok=True)
            # Remove the parent folder if it's empty
            parent = target.parent
            if parent != self.upload_dir and not any(parent.iterdir()):
                parent.rmdir()
        except OSError as exc:
            logger.warning(f"LocalStorageProvider: could not delete {storage_key}: {exc}")

    async def get_url(self, storage_key: str, presigned: bool = False, expiry_seconds: int = 3600) -> str:
        """
        Return the public URL for a given storage key.
        LocalStorageProvider does not support presigned URLs — always returns a plain URL.
        """
        return f"{self.base_url}/uploads/{storage_key}"
