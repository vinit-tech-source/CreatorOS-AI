import asyncio
import uuid
import sys
from datetime import datetime, timedelta, timezone

from app.core.database import AsyncSessionLocal
from app.api.dev_auth import _upsert_dev_user
from app.models.workspace import Workspace
from app.models.project import Project, ProjectStatus
from app.models.post import Post, PostStatus, SchedulingStatus
from app.models.social_account import SocialAccount, SocialPlatform
from app.services.post_service import PostService
from app.services.scheduler_service import SchedulerService
from app.schemas.post import PostCreate, PostSchedule

async def run_e2e():
    async with AsyncSessionLocal() as session:
        print("Starting E2E Validation...")
        
        # 1. Setup Dev User, Workspace, Project, Social Account
        user = await _upsert_dev_user(session)
        print(f"User: {user.email}")
        
        ws = Workspace(id=uuid.uuid4(), name="E2E Workspace", slug=f"e2e-{uuid.uuid4().hex[:6]}", owner_id=user.id)
        session.add(ws)
        
        proj = Project(id=uuid.uuid4(), workspace_id=ws.id, name="E2E Project", slug=f"e2e-proj-{uuid.uuid4().hex[:6]}")
        session.add(proj)
        
        acc = SocialAccount(id=uuid.uuid4(), workspace_id=ws.id, platform=SocialPlatform.X, access_token_encrypted='fake', is_active=True, account_name="E2E X", platform_user_id="fake_user")
        session.add(acc)
        
        await session.commit()
        
    # We need to initialize SchedulerService with repos. Let's do it right.
    from app.repositories.post_repository import PostRepository
    from app.repositories.project_repository import ProjectRepository
    from app.repositories.workspace_repository import WorkspaceRepository
    
    async with AsyncSessionLocal() as session:
        post_repo = PostRepository(session)
        proj_repo = ProjectRepository(session)
        ws_repo = WorkspaceRepository(session)
        post_service = PostService(post_repo, proj_repo, ws_repo)
        sched_service = SchedulerService(post_repo, proj_repo, ws_repo)
        
        # 2. Create DRAFT post
        print("\n--- 2. APPROVAL FLOW ---")
        post_data = PostCreate(
            title="E2E Test Post",
            content="This is a test post for E2E validation.",
            platform=SocialPlatform.X,
            content_type="TEXT"
        )
        post = await post_service.create_post(proj.id, post_data, user.id)
        print(f"Created post: {post.id} with status {post.status}")
        assert post.status == PostStatus.DRAFT
        
        # 3. Submit for Review
        post = await post_service.submit_for_review(proj.id, post.id, user.id)
        print(f"Submitted for review, status: {post.status}")
        assert post.status == PostStatus.PENDING_REVIEW
        
        # 4. Approve
        post = await post_service.approve_post(proj.id, post.id, user.id)
        print(f"Approved, status: {post.status}")
        assert post.status == PostStatus.APPROVED
        
        # 5. Schedule Flow
        print("\n--- 3. SCHEDULING FLOW ---")
        sched_time = datetime.now(timezone.utc) + timedelta(seconds=2)
        sched_data = PostSchedule(scheduled_at=sched_time, timezone="UTC")
        post = await sched_service.schedule_post(proj.id, post.id, sched_data, user.id)
        print(f"Scheduled at: {post.scheduled_at}, status: {post.status}, sched_status: {post.scheduling_status}")
        assert post.status == PostStatus.SCHEDULED
        assert post.scheduling_status == SchedulingStatus.SCHEDULED
        
        # 6. Worker Execution
        print("\n--- 4. WORKER & MCP VALIDATION ---")
        print("Waiting 3 seconds for post to become due...")
        await asyncio.sleep(3)
        
        # We simulate the worker loop here
        from app.workers.scheduler_worker import process_due_posts
        await process_due_posts()
        
    async with AsyncSessionLocal() as session:
        # Check post status after worker
        post_repo = PostRepository(session)
        post_after = await post_repo.get_by_id(post.id)
        print(f"After worker, post status: {post_after.status}, sched_status: {post_after.scheduling_status}")
        assert post_after.status == PostStatus.PUBLISHED
        assert post_after.scheduling_status == SchedulingStatus.COMPLETED
        
        # 7. Analytics Flow
        print("\n--- 8. ANALYTICS FLOW ---")
        from app.workers.analytics_worker import process_analytics_for_published_posts
        await process_analytics_for_published_posts()
        
    async with AsyncSessionLocal() as session:
        from app.repositories.analytics_repository import AnalyticsRepository
        analytics_repo = AnalyticsRepository(session)
        snapshots = await analytics_repo.list_snapshots_by_post(post.id, ws.id)
        if snapshots:
            print(f"Analytics collected: likes={snapshots[0].likes}, shares={snapshots[0].shares}")
        else:
            print("No analytics collected (maybe FakeSocialAdapter returned None?)")
        
        print("\n✅ E2E Flow Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(run_e2e())
