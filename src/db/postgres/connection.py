from core.config import settings
from db.postgres.session_manager import db_manager
from sqlalchemy.ext.asyncio import AsyncSession


async def get_async_session() -> AsyncSession:
    async with db_manager.async_session() as session:
        yield session


async def get_postgres_session() -> AsyncSession:
    db_manager.init(settings.postgres.database_url)
    async with db_manager.async_session() as session:
        return session