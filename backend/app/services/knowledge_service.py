import uuid
from typing import List

from app.models.knowledge_source import KnowledgeSource
from app.repositories.knowledge_repository_interface import KnowledgeRepositoryInterface
from app.repositories.workspace_repository_interface import AbstractWorkspaceRepository
from app.schemas.knowledge import KnowledgeSourceCreate
from app.rag.ingestion.pipeline import IngestionPipeline
from app.rag.schemas.document import RAGDocument
from app.rag.vectorstore.base import VectorStore
import logging

logger = logging.getLogger(__name__)

class KnowledgeService:
    def __init__(
        self,
        knowledge_repo: KnowledgeRepositoryInterface,
        workspace_repo: AbstractWorkspaceRepository,
        ingestion_pipeline: IngestionPipeline,
        vector_store: VectorStore,
    ):
        self.knowledge_repo = knowledge_repo
        self.workspace_repo = workspace_repo
        self.ingestion_pipeline = ingestion_pipeline
        self.vector_store = vector_store

    async def _verify_access(self, workspace_id: uuid.UUID, requesting_user_id: uuid.UUID) -> None:
        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if not workspace or workspace.owner_id != requesting_user_id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or unauthorized.",
            )

    async def create_knowledge_source(
        self, workspace_id: uuid.UUID, data: KnowledgeSourceCreate, requesting_user_id: uuid.UUID
    ) -> KnowledgeSource:
        await self._verify_access(workspace_id, requesting_user_id)

        source = KnowledgeSource(
            workspace_id=workspace_id,
            name=data.name,
            source_type=data.source_type,
            content=data.content,
            status="PENDING",
        )
        source = await self.knowledge_repo.create(source)

        # Process through the RAG Ingestion Pipeline
        try:
            document = RAGDocument(
                id=str(source.id),
                content=source.content,
                workspace_id=str(workspace_id),
                metadata={"source_name": source.name, "source_type": source.source_type}
            )
            await self.ingestion_pipeline.ingest_document(document)
            
            source.status = "PROCESSED"
            await self.knowledge_repo.update(source)
            
        except Exception as e:
            logger.error(f"Ingestion failed for source {source.id}: {e}")
            source.status = "FAILED"
            await self.knowledge_repo.update(source)

        return source

    async def list_knowledge_sources(
        self, workspace_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> List[KnowledgeSource]:
        await self._verify_access(workspace_id, requesting_user_id)
        return await self.knowledge_repo.get_by_workspace_id(workspace_id)

    async def delete_knowledge_source(
        self, workspace_id: uuid.UUID, knowledge_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> None:
        await self._verify_access(workspace_id, requesting_user_id)
        
        source = await self.knowledge_repo.get_by_id(knowledge_id)
        if not source or source.workspace_id != workspace_id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge source not found.",
            )
            
        # Delete from vector store
        await self.vector_store.delete_documents([str(knowledge_id)])
        
        # Delete from DB
        await self.knowledge_repo.delete(knowledge_id)
