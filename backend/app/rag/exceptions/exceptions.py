"""
app/rag/exceptions/exceptions.py

Exceptions for the RAG foundation.
"""
from app.core.exceptions import AppException

class RAGError(AppException):
    """Base exception for RAG-related errors."""
    def __init__(self, message: str):
        super().__init__(message=message)

class RAGProviderError(RAGError):
    """Raised when an external embedding or vector store provider fails."""
    pass

class RAGValidationError(RAGError):
    """Raised when document content or schema is invalid."""
    pass
