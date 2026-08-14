"""
tests/test_approval.py

Tests for the Content Approval Workflow.
"""
import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

from httpx import AsyncClient

from app.models.post import PostStatus, ContentType, Post
from app.models.social_account import SocialPlatform
from app.models.project import Project
from app.models.workspace import Workspace
from app.models.user import User
from app.models.approval_log import ApprovalLog, ApprovalAction
from app.services.post_service import PostService
from app.core.exceptions import InvalidStatusTransitionError, ProjectNotFoundError, PostNotFoundError
from app.mcp.tools.social.publish_post import PublishPostTool
from app.mcp.exceptions.exceptions import MCPProviderError

@pytest.fixture
def test_user():
    user = User(
        id=uuid.uuid4(), 
        email="test@example.com", 
        username="testuser",
        password_hash="pw",
        full_name="Test User"
    )
    return user

@pytest.fixture
def test_workspace(test_user):
    ws = Workspace(id=uuid.uuid4(), name="Test WS", owner_id=test_user.id)
    return ws

@pytest.fixture
def test_project(test_workspace):
    proj = Project(id=uuid.uuid4(), name="Test Project", workspace_id=test_workspace.id)
    return proj

@pytest.fixture
def test_post(test_project):
    post = Post(
        id=uuid.uuid4(),
        project_id=test_project.id,
        content="Test content",
        content_type=ContentType.TEXT,
        status=PostStatus.DRAFT,
        platform=SocialPlatform.BLUESKY,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    return post

@pytest.mark.asyncio
async def test_draft_to_pending_review(test_post, test_project, test_user):
    """1. Draft -> pending review."""
    post_repo = AsyncMock()
    post_repo.get_by_id.return_value = test_post
    post_repo.update.return_value = test_post
    
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = test_project
    
    ws_repo = AsyncMock()
    ws_repo.get_by_id.return_value = MagicMock(owner_id=test_user.id, id=test_project.workspace_id)
    
    service = PostService(post_repo, project_repo, ws_repo)
    
    with patch("app.services.post_service.AsyncSessionLocal") as mock_session:
        mock_db = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_db
        
        await service.submit_for_review(test_project.id, test_post.id, test_user.id)
        
        post_repo.update.assert_called_once()
        update_call_args = post_repo.update.call_args[0]
        assert update_call_args[1].status == PostStatus.PENDING_REVIEW
        
        # 11. Approval audit record created
        mock_db.add.assert_called_once()
        added_log = mock_db.add.call_args[0][0]
        assert isinstance(added_log, ApprovalLog)
        assert added_log.action == ApprovalAction.SUBMIT
        assert added_log.previous_status == PostStatus.DRAFT
        assert added_log.new_status == PostStatus.PENDING_REVIEW

@pytest.mark.asyncio
async def test_pending_review_to_approved(test_post, test_project, test_user):
    """2. Pending review -> approved."""
    test_post.status = PostStatus.PENDING_REVIEW
    
    post_repo = AsyncMock()
    post_repo.get_by_id.return_value = test_post
    post_repo.update.return_value = test_post
    
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = test_project
    
    ws_repo = AsyncMock()
    ws_repo.get_by_id.return_value = MagicMock(owner_id=test_user.id, id=test_project.workspace_id)
    
    service = PostService(post_repo, project_repo, ws_repo)
    
    with patch("app.services.post_service.AsyncSessionLocal") as mock_session:
        mock_db = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_db
        
        await service.approve_post(test_project.id, test_post.id, test_user.id)
        
        post_repo.update.assert_called_once()
        update_data = post_repo.update.call_args[0][1]
        assert update_data.status == PostStatus.APPROVED
        assert update_data.approved_by == test_user.id

@pytest.mark.asyncio
async def test_pending_review_to_rejected(test_post, test_project, test_user):
    """3. Pending review -> rejected."""
    test_post.status = PostStatus.PENDING_REVIEW
    
    post_repo = AsyncMock()
    post_repo.get_by_id.return_value = test_post
    post_repo.update.return_value = test_post
    
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = test_project
    
    ws_repo = AsyncMock()
    ws_repo.get_by_id.return_value = MagicMock(owner_id=test_user.id, id=test_project.workspace_id)
    
    service = PostService(post_repo, project_repo, ws_repo)
    
    with patch("app.services.post_service.AsyncSessionLocal") as mock_session:
        mock_db = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_db
        
        await service.reject_post(test_project.id, test_post.id, "Needs revision", test_user.id)
        
        post_repo.update.assert_called_once()
        update_data = post_repo.update.call_args[0][1]
        assert update_data.status == PostStatus.REJECTED
        assert update_data.rejection_reason == "Needs revision"

@pytest.mark.asyncio
async def test_invalid_approval_transition_rejected(test_post, test_project, test_user):
    """4. Invalid approval transition rejected."""
    # Try to approve a DRAFT directly (invalid)
    test_post.status = PostStatus.DRAFT
    
    post_repo = AsyncMock()
    post_repo.get_by_id.return_value = test_post
    
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = test_project
    
    ws_repo = AsyncMock()
    ws_repo.get_by_id.return_value = MagicMock(owner_id=test_user.id, id=test_project.workspace_id)
    
    service = PostService(post_repo, project_repo, ws_repo)
    
    with pytest.raises(InvalidStatusTransitionError):
        await service.approve_post(test_project.id, test_post.id, test_user.id)

@pytest.mark.asyncio
async def test_viewer_cannot_approve(test_post, test_project, test_user):
    """5 & 6. Viewer / Unauthorized workspace user cannot approve."""
    test_post.status = PostStatus.PENDING_REVIEW
    
    post_repo = AsyncMock()
    post_repo.get_by_id.return_value = test_post
    
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = test_project
    
    ws_repo = AsyncMock()
    # Workspace owned by someone else
    ws_repo.get_by_id.return_value = MagicMock(owner_id=uuid.uuid4(), id=test_project.workspace_id)
    
    service = PostService(post_repo, project_repo, ws_repo)
    
    with pytest.raises(ProjectNotFoundError):
        await service.approve_post(test_project.id, test_post.id, test_user.id)

@pytest.mark.asyncio
@patch("app.mcp.tools.social.publish_post.AsyncSessionLocal")
async def test_unapproved_post_cannot_publish(mock_session):
    """8. Unapproved post cannot publish."""
    # Test publishing a DRAFT post
    mock_db = AsyncMock()
    mock_session.return_value.__aenter__.return_value = mock_db
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    mock_account = MagicMock(workspace_id=uuid.uuid4(), platform="BLUESKY")
    mock_post = MagicMock(status=PostStatus.DRAFT, content="draft content")
    
    with patch("app.mcp.tools.social.publish_post.SocialAccountRepository") as mock_repo_class, \
         patch("app.mcp.tools.social.publish_post.PostRepository") as mock_post_repo_class:
         
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_account
        mock_repo_class.return_value = mock_repo
        
        mock_post_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = mock_post
        mock_post_repo_class.return_value = mock_post_repo
        
        tool = PublishPostTool()
        with pytest.raises(MCPProviderError, match="not APPROVED"):
            await tool.execute({
                "workspace_id": str(mock_account.workspace_id),
                "social_account_id": str(uuid.uuid4()),
                "post_id": str(uuid.uuid4()),
                "idempotency_key": "idemp-test"
            })

@pytest.mark.asyncio
@patch("app.mcp.tools.social.publish_post.AsyncSessionLocal")
async def test_rejected_post_cannot_publish(mock_session):
    """10. Rejected post cannot publish."""
    # Test publishing a REJECTED post
    mock_db = AsyncMock()
    mock_session.return_value.__aenter__.return_value = mock_db
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    mock_account = MagicMock(workspace_id=uuid.uuid4(), platform="BLUESKY")
    mock_post = MagicMock(status=PostStatus.REJECTED, content="rejected content")
    
    with patch("app.mcp.tools.social.publish_post.SocialAccountRepository") as mock_repo_class, \
         patch("app.mcp.tools.social.publish_post.PostRepository") as mock_post_repo_class:
         
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_account
        mock_repo_class.return_value = mock_repo
        
        mock_post_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = mock_post
        mock_post_repo_class.return_value = mock_post_repo
        
        tool = PublishPostTool()
        with pytest.raises(MCPProviderError, match="not APPROVED"):
            await tool.execute({
                "workspace_id": str(mock_account.workspace_id),
                "social_account_id": str(uuid.uuid4()),
                "post_id": str(uuid.uuid4()),
                "idempotency_key": "idemp-test"
            })

@pytest.mark.asyncio
@patch("app.mcp.tools.social.publish_post.AsyncSessionLocal")
async def test_approved_post_can_publish(mock_session):
    """9. Approved post can publish through existing MCP tool."""
    mock_db = AsyncMock()
    mock_session.return_value.__aenter__.return_value = mock_db
    # First execute gives no publishing log, second gives the inserted one to update
    mock_result1 = MagicMock()
    mock_result1.scalar_one_or_none.return_value = None
    
    mock_log = MagicMock()
    mock_result2 = MagicMock()
    mock_result2.scalar_one.return_value = mock_log
    
    mock_db.execute.side_effect = [mock_result1, mock_result2]
    
    mock_account = MagicMock(workspace_id=uuid.uuid4(), platform="BLUESKY")
    mock_post = MagicMock(status=PostStatus.APPROVED, content="approved content")
    
    mock_adapter = AsyncMock()
    mock_adapter_result = MagicMock()
    mock_adapter_result.model_dump.return_value = {"platform": "BLUESKY"}
    mock_adapter.publish_post.return_value = mock_adapter_result
    
    with patch("app.mcp.tools.social.publish_post.SocialAccountRepository") as mock_repo_class, \
         patch("app.mcp.tools.social.publish_post.PostRepository") as mock_post_repo_class, \
         patch("app.mcp.tools.social.publish_post.get_social_adapter", return_value=mock_adapter):
         
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_account
        mock_repo_class.return_value = mock_repo
        
        mock_post_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = mock_post
        mock_post_repo_class.return_value = mock_post_repo
        
        tool = PublishPostTool()
        result = await tool.execute({
            "workspace_id": str(mock_account.workspace_id),
            "social_account_id": str(uuid.uuid4()),
            "post_id": str(uuid.uuid4()),
            "idempotency_key": "idemp-test-approved"
        })
        
        assert result.success is True
        mock_adapter.publish_post.assert_called_once_with(
            content="approved content",
            idempotency_key="idemp-test-approved",
            media=[]
        )
