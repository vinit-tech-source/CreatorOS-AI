"""
tests/test_scheduler.py

Tests for the Post Scheduling System and Worker.
"""
import pytest
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

from httpx import AsyncClient

from app.models.post import PostStatus, ContentType, Post, SchedulingStatus
from app.models.social_account import SocialPlatform
from app.models.project import Project
from app.models.workspace import Workspace
from app.models.user import User
from app.services.scheduler_service import SchedulerService
from app.schemas.post import PostSchedule, PostUpdate
from app.core.exceptions import InvalidStatusTransitionError, ProjectNotFoundError, PostNotFoundError
from app.workers.scheduler_worker import process_due_posts
from app.mcp.tools.social.publish_post import PublishPostTool
from app.mcp.exceptions.exceptions import MCPProviderError, MCPAuthenticationError

@pytest.fixture
def test_user():
    return User(
        id=uuid.uuid4(), 
        email="test_scheduler@example.com", 
        username="testscheduler",
        password_hash="pw",
        full_name="Scheduler User"
    )

@pytest.fixture
def test_workspace(test_user):
    return Workspace(id=uuid.uuid4(), name="Test WS", owner_id=test_user.id)

@pytest.fixture
def test_project(test_workspace):
    return Project(id=uuid.uuid4(), name="Test Project", workspace_id=test_workspace.id)

@pytest.fixture
def test_post(test_project):
    return Post(
        id=uuid.uuid4(),
        project_id=test_project.id,
        title=None,
        content="Test content",
        content_type=ContentType.TEXT,
        status=PostStatus.APPROVED,
        platform=SocialPlatform.BLUESKY,
        scheduled_at=None,
        published_at=None,
        external_post_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        approval_status=None,
        approved_by=None,
        approved_at=None,
        rejection_reason=None,
        timezone=None,
        scheduling_status=SchedulingStatus.NOT_SCHEDULED,
        scheduled_attempts=0,
        last_attempt_at=None,
        failure_reason=None
    )

def _setup_service_mocks(test_post, test_project, test_workspace):
    post_repo = AsyncMock()
    post_repo.get_by_id.return_value = test_post
    post_repo.update.return_value = test_post
    
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = test_project
    
    ws_repo = AsyncMock()
    ws_repo.get_by_id.return_value = test_workspace
    
    service = SchedulerService(post_repo, project_repo, ws_repo)
    return service, post_repo, project_repo, ws_repo

@pytest.mark.asyncio
async def test_approved_post_can_be_scheduled(test_post, test_project, test_workspace, test_user):
    """1. Approved post can be scheduled."""
    service, post_repo, _, _ = _setup_service_mocks(test_post, test_project, test_workspace)
    
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    schedule_data = PostSchedule(scheduled_at=future_time, timezone="UTC")
    
    await service.schedule_post(test_project.id, test_post.id, schedule_data, test_user.id)
    
    post_repo.update.assert_called_once()
    update_data = post_repo.update.call_args[0][1]
    assert update_data.scheduled_at == future_time
    assert update_data.scheduling_status == SchedulingStatus.SCHEDULED
    assert update_data.status == PostStatus.SCHEDULED

@pytest.mark.asyncio
async def test_draft_cannot_be_scheduled(test_post, test_project, test_workspace, test_user):
    """2. Draft cannot be scheduled."""
    test_post.status = PostStatus.DRAFT
    service, _, _, _ = _setup_service_mocks(test_post, test_project, test_workspace)
    
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    schedule_data = PostSchedule(scheduled_at=future_time, timezone="UTC")
    
    with pytest.raises(InvalidStatusTransitionError):
        await service.schedule_post(test_project.id, test_post.id, schedule_data, test_user.id)

@pytest.mark.asyncio
async def test_pending_review_cannot_be_scheduled(test_post, test_project, test_workspace, test_user):
    """3. Pending review cannot be scheduled."""
    test_post.status = PostStatus.PENDING_REVIEW
    service, _, _, _ = _setup_service_mocks(test_post, test_project, test_workspace)
    
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    schedule_data = PostSchedule(scheduled_at=future_time, timezone="UTC")
    
    with pytest.raises(InvalidStatusTransitionError):
        await service.schedule_post(test_project.id, test_post.id, schedule_data, test_user.id)

@pytest.mark.asyncio
async def test_rejected_post_cannot_be_scheduled(test_post, test_project, test_workspace, test_user):
    """4. Rejected post cannot be scheduled."""
    test_post.status = PostStatus.REJECTED
    service, _, _, _ = _setup_service_mocks(test_post, test_project, test_workspace)
    
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    schedule_data = PostSchedule(scheduled_at=future_time, timezone="UTC")
    
    with pytest.raises(InvalidStatusTransitionError):
        await service.schedule_post(test_project.id, test_post.id, schedule_data, test_user.id)

@pytest.mark.asyncio
async def test_cancelled_schedule_is_not_executed(test_post, test_project, test_workspace, test_user):
    """15. Cancelled schedule is not executed."""
    test_post.status = PostStatus.SCHEDULED
    service, post_repo, _, _ = _setup_service_mocks(test_post, test_project, test_workspace)
    
    await service.cancel_schedule(test_project.id, test_post.id, test_user.id)
    
    post_repo.update.assert_called_once()
    update_data = post_repo.update.call_args[0][1]
    assert update_data.scheduling_status == SchedulingStatus.CANCELLED
    assert update_data.status == PostStatus.APPROVED
    assert update_data.scheduled_at is None

@pytest.mark.asyncio
async def test_rescheduling_works(test_post, test_project, test_workspace, test_user):
    """16. Rescheduling works."""
    test_post.status = PostStatus.SCHEDULED
    service, post_repo, _, _ = _setup_service_mocks(test_post, test_project, test_workspace)
    
    future_time = datetime.now(timezone.utc) + timedelta(days=2)
    schedule_data = PostSchedule(scheduled_at=future_time, timezone="America/New_York")
    
    await service.reschedule_post(test_project.id, test_post.id, schedule_data, test_user.id)
    
    post_repo.update.assert_called_once()
    update_data = post_repo.update.call_args[0][1]
    assert update_data.scheduled_at == future_time
    assert update_data.timezone == "America/New_York"
    assert update_data.scheduled_attempts == 0
    assert update_data.failure_reason is None

@pytest.mark.asyncio
async def test_workspace_authorization_is_enforced(test_post, test_project, test_user):
    """18. Workspace authorization is enforced."""
    post_repo = AsyncMock()
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = test_project
    
    ws_repo = AsyncMock()
    # Workspace owned by a different user
    test_workspace_diff_owner = Workspace(id=uuid.uuid4(), name="Test WS", owner_id=uuid.uuid4())
    ws_repo.get_by_id.return_value = test_workspace_diff_owner
    
    service = SchedulerService(post_repo, project_repo, ws_repo)
    
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    schedule_data = PostSchedule(scheduled_at=future_time, timezone="UTC")
    
    with pytest.raises(ProjectNotFoundError):
        await service.schedule_post(test_project.id, test_post.id, schedule_data, test_user.id)

@pytest.mark.asyncio
async def test_timezone_handling_is_correct(test_post, test_project, test_workspace, test_user):
    """19. Timezone handling is correct."""
    service, _, _, _ = _setup_service_mocks(test_post, test_project, test_workspace)
    
    # Must reject non-timezone aware datetime or past datetime
    past_time = datetime.now(timezone.utc) - timedelta(days=1)
    schedule_data = PostSchedule(scheduled_at=past_time, timezone="UTC")
    
    with pytest.raises(ValueError, match="future"):
        await service.schedule_post(test_project.id, test_post.id, schedule_data, test_user.id)

# ---------------------------------------------------------
# WORKER TESTS
# ---------------------------------------------------------

@pytest.mark.asyncio
@patch("app.workers.scheduler_worker.AsyncSessionLocal")
async def test_successful_publish_marks_scheduling_completed(mock_session, test_post):
    """5, 6, 8, 9, 10, 14. Scheduler worker successful publish."""
    # Setup mocks
    mock_db = AsyncMock()
    mock_session.return_value.__aenter__.return_value = mock_db
    
    test_post.scheduling_status = SchedulingStatus.SCHEDULED
    test_post.status = PostStatus.SCHEDULED
    
    # Mock service get_due_posts
    with patch("app.workers.scheduler_worker.SchedulerService") as MockService, \
         patch("app.workers.scheduler_worker.ProjectRepository") as MockProjectRepo, \
         patch("app.workers.scheduler_worker.WorkspaceRepository"), \
         patch("app.workers.scheduler_worker.PostRepository"), \
         patch("app.workers.scheduler_worker.SocialAccountRepository") as MockSocialRepo, \
         patch("app.workers.scheduler_worker.PublishPostTool") as MockTool:
         
        mock_service_inst = AsyncMock()
        mock_service_inst.get_due_posts.return_value = [test_post]
        mock_service_inst.claim_due_post.return_value = True
        MockService.return_value = mock_service_inst
        
        mock_proj_repo_inst = AsyncMock()
        mock_project = MagicMock(workspace_id=uuid.uuid4())
        mock_proj_repo_inst.get_by_id.return_value = mock_project
        MockProjectRepo.return_value = mock_proj_repo_inst
        
        mock_social_repo_inst = AsyncMock()
        mock_account = MagicMock(id=uuid.uuid4(), platform=test_post.platform, is_active=True)
        mock_social_repo_inst.get_by_workspace_id.return_value = [mock_account]
        MockSocialRepo.return_value = mock_social_repo_inst
        
        mock_tool_inst = AsyncMock()
        mock_tool_inst.execute.return_value = MagicMock(success=True)
        MockTool.return_value = mock_tool_inst
        
        await process_due_posts()
        
        # Verify claim
        mock_service_inst.claim_due_post.assert_called_once_with(test_post.id)
        
        # Verify MCP tool was called
        mock_tool_inst.execute.assert_called_once()
        exec_args = mock_tool_inst.execute.call_args[0][0]
        assert exec_args["post_id"] == str(test_post.id)
        assert "idempotency_key" in exec_args
        
        # Verify completion
        mock_service_inst.mark_completed.assert_called_once_with(test_post.id)

@pytest.mark.asyncio
@patch("app.workers.scheduler_worker.AsyncSessionLocal")
async def test_transient_failure_retries(mock_session, test_post):
    """11. Transient failure retries."""
    mock_db = AsyncMock()
    mock_session.return_value.__aenter__.return_value = mock_db
    
    test_post.status = PostStatus.SCHEDULED
    
    with patch("app.workers.scheduler_worker.SchedulerService") as MockService, \
         patch("app.workers.scheduler_worker.ProjectRepository") as MockProjectRepo, \
         patch("app.workers.scheduler_worker.WorkspaceRepository"), \
         patch("app.workers.scheduler_worker.PostRepository"), \
         patch("app.workers.scheduler_worker.SocialAccountRepository") as MockSocialRepo, \
         patch("app.workers.scheduler_worker.PublishPostTool") as MockTool:
         
        mock_service_inst = AsyncMock()
        mock_service_inst.get_due_posts.return_value = [test_post]
        mock_service_inst.claim_due_post.return_value = True
        MockService.return_value = mock_service_inst
        
        mock_proj_repo_inst = AsyncMock()
        mock_project = MagicMock(workspace_id=uuid.uuid4())
        mock_proj_repo_inst.get_by_id.return_value = mock_project
        MockProjectRepo.return_value = mock_proj_repo_inst
        
        mock_social_repo_inst = AsyncMock()
        mock_account = MagicMock(id=uuid.uuid4(), platform=test_post.platform, is_active=True)
        mock_social_repo_inst.get_by_workspace_id.return_value = [mock_account]
        MockSocialRepo.return_value = mock_social_repo_inst
        
        mock_tool_inst = AsyncMock()
        # Raise generic provider error
        mock_tool_inst.execute.side_effect = MCPProviderError("Timeout")
        MockTool.return_value = mock_tool_inst
        
        await process_due_posts()
        
        mock_service_inst.mark_failed.assert_called_once_with(test_post.id, reason="Timeout", retry=True)

@pytest.mark.asyncio
@patch("app.workers.scheduler_worker.AsyncSessionLocal")
async def test_permanent_failure_no_retry(mock_session, test_post):
    """12. Permanent failure is not retried."""
    mock_db = AsyncMock()
    mock_session.return_value.__aenter__.return_value = mock_db
    
    test_post.status = PostStatus.SCHEDULED
    
    with patch("app.workers.scheduler_worker.SchedulerService") as MockService, \
         patch("app.workers.scheduler_worker.ProjectRepository") as MockProjectRepo, \
         patch("app.workers.scheduler_worker.WorkspaceRepository"), \
         patch("app.workers.scheduler_worker.PostRepository"), \
         patch("app.workers.scheduler_worker.SocialAccountRepository") as MockSocialRepo, \
         patch("app.workers.scheduler_worker.PublishPostTool") as MockTool:
         
        mock_service_inst = AsyncMock()
        mock_service_inst.get_due_posts.return_value = [test_post]
        mock_service_inst.claim_due_post.return_value = True
        MockService.return_value = mock_service_inst
        
        mock_proj_repo_inst = AsyncMock()
        mock_project = MagicMock(workspace_id=uuid.uuid4())
        mock_proj_repo_inst.get_by_id.return_value = mock_project
        MockProjectRepo.return_value = mock_proj_repo_inst
        
        mock_social_repo_inst = AsyncMock()
        mock_account = MagicMock(id=uuid.uuid4(), platform=test_post.platform, is_active=True)
        mock_social_repo_inst.get_by_workspace_id.return_value = [mock_account]
        MockSocialRepo.return_value = mock_social_repo_inst
        
        mock_tool_inst = AsyncMock()
        # Raise auth error
        mock_tool_inst.execute.side_effect = MCPAuthenticationError("Invalid Token")
        MockTool.return_value = mock_tool_inst
        
        await process_due_posts()
        
        mock_service_inst.mark_failed.assert_called_once_with(test_post.id, reason="Invalid Token", retry=False)

@pytest.mark.asyncio
@patch("app.workers.scheduler_worker.AsyncSessionLocal")
async def test_unapproved_post_blocked_at_execution(mock_session, test_post):
    """17. Unapproved post is blocked at execution time."""
    mock_db = AsyncMock()
    mock_session.return_value.__aenter__.return_value = mock_db
    
    # Due post somehow got here but status is no longer SCHEDULED/APPROVED
    test_post.status = PostStatus.REJECTED
    
    with patch("app.workers.scheduler_worker.SchedulerService") as MockService, \
         patch("app.workers.scheduler_worker.ProjectRepository") as MockProjectRepo, \
         patch("app.workers.scheduler_worker.WorkspaceRepository"), \
         patch("app.workers.scheduler_worker.PostRepository"), \
         patch("app.workers.scheduler_worker.SocialAccountRepository") as MockSocialRepo:
         
        mock_service_inst = AsyncMock()
        mock_service_inst.get_due_posts.return_value = [test_post]
        mock_service_inst.claim_due_post.return_value = True
        MockService.return_value = mock_service_inst
        
        mock_proj_repo_inst = AsyncMock()
        mock_project = MagicMock(workspace_id=uuid.uuid4())
        mock_proj_repo_inst.get_by_id.return_value = mock_project
        MockProjectRepo.return_value = mock_proj_repo_inst
        
        mock_social_repo_inst = AsyncMock()
        mock_account = MagicMock(id=uuid.uuid4(), platform=test_post.platform, is_active=True)
        mock_social_repo_inst.get_by_workspace_id.return_value = [mock_account]
        MockSocialRepo.return_value = mock_social_repo_inst
        
        await process_due_posts()
        
        # Should not execute tool, should mark failed immediately
        mock_service_inst.mark_failed.assert_called_once()
        assert "no longer in an approved" in mock_service_inst.mark_failed.call_args[1]["reason"]
        assert mock_service_inst.mark_failed.call_args[1]["retry"] is False
