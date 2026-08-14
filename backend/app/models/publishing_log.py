"""
app/models/publishing_log.py

Database model for tracking publishing operations and providing idempotency.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
import enum

from app.models.base import Base
from app.models.social_account import SocialPlatform

class PublishStatus(enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class PublishingLog(Base):
    __tablename__ = "publishing_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True)
    social_account_id = Column(UUID(as_uuid=True), ForeignKey("social_accounts.id"), nullable=False, index=True)
    
    platform = Column(SQLEnum(SocialPlatform), nullable=False)
    idempotency_key = Column(String(255), nullable=False, unique=True, index=True)
    
    external_post_id = Column(String(255), nullable=True)
    status = Column(SQLEnum(PublishStatus), nullable=False, default=PublishStatus.PENDING)
    error_code = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
