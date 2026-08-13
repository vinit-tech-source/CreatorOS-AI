"""
app/integrations/storage/base.py

Abstract interface for cloud storage providers.
"""
from abc import ABC, abstractmethod


class AbstractStorageProvider(ABC):
    """
    Protocol for interacting with a cloud storage provider (e.g., S3, GCS, R2).
    """

    @abstractmethod
    async def upload(self, file_data: bytes, file_name: str, mime_type: str) -> str:
        """
        Upload a file to the storage provider.
        
        Args:
            file_data: The raw file bytes.
            file_name: The desired destination filename or path.
            mime_type: The MIME type of the file.
            
        Returns:
            The storage key representing the uploaded file.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, storage_key: str) -> None:
        """
        Delete a file from the storage provider.
        
        Args:
            storage_key: The storage key of the file to delete.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_url(self, storage_key: str, presigned: bool = False, expiry_seconds: int = 3600) -> str:
        """
        Retrieve a URL for the given storage key.
        
        Args:
            storage_key: The storage key of the file.
            presigned: Whether to return a temporary presigned URL for private assets.
            expiry_seconds: Expiration time for presigned URLs.
            
        Returns:
            The public or presigned URL.
        """
        raise NotImplementedError
