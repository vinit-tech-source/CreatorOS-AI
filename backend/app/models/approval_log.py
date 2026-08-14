"""
app/models/approval_log.py

Database model for tracking content approval actions.
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.post import PostStatus

class ApprovalAction(str, enum.Enum):
    SUBMIT = "SUBMIT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"

class ApprovalLog(Base):
    __tablename__ = "approval_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    action = Column(SQLEnum(ApprovalAction, name="approvalaction"), nullable=False)
    previous_status = Column(SQLEnum(PostStatus, name="poststatus"), nullable=False)
    new_status = Column(SQLEnum(PostStatus, name="poststatus"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
