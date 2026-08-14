import asyncio
import uuid
from app.core.database import AsyncSessionLocal
from app.api.dev_auth import _DEV_USER_ID, _upsert_dev_user
from app.models.workspace import Workspace

async def create_workspace():
    async with AsyncSessionLocal() as session:
        user = await _upsert_dev_user(session)
        ws = Workspace(
            id=uuid.uuid4(),
            name="My Dev Workspace",
            slug="my-dev-workspace",
            description="Created by setup script",
            owner_id=user.id
        )
        session.add(ws)
        await session.commit()
        print(f"Created workspace '{ws.name}' for user {user.email}")

if __name__ == "__main__":
    asyncio.run(create_workspace())
