import asyncio
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate

async def main():
    async for session in get_db():
        repo = UserRepository(session)
        service = AuthService(repo)
        data = UserCreate(
            email="test_internal@example.com",
            username="test_internal",
            password="Password123!",
            full_name="Internal Test",
        )
        try:
            user = await service.register_user(data)
            print("Success:", user)
        except Exception as e:
            print("Error in registration:")
            import traceback
            traceback.print_exc()
        break

if __name__ == "__main__":
    asyncio.run(main())
