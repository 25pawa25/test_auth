import contextlib
from typing import AsyncIterator

from core.config import settings
from db.postgres.session_manager import db_manager
from db.redis.session_manager import redis_db_manager
from fastapi import FastAPI


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    db_manager.init(settings.postgres.database_url)
    redis_db_manager.init(settings.redis.host, settings.redis.port)
    yield
    await db_manager.close()
    await redis_db_manager.close()
