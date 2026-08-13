"""
app/rag/embeddings/base.py

Abstract embedding provider and a fake provider for foundational testing.
"""
from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    """Abstract base class for all embedding providers."""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Embed a single piece of text."""
        pass
        
    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple pieces of text."""
        pass


class FakeEmbeddingProvider(EmbeddingProvider):
    """A fake embedding provider for testing and MVP architecture validation."""
    
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        
    async def embed_text(self, text: str) -> List[float]:
        # Return a deterministic, fake embedding
        return [0.1] * self.dimension
        
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * self.dimension for _ in texts]
