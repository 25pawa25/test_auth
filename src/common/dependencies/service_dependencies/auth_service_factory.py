from common.dependencies.registrator import add_factory_to_mapper
from core.config import get_settings, settings
from db.postgres.connection import get_async_session
from db.redis.connection import get_async_redis_client
from fastapi import Depends
from redis.asyncio import Redis
from repository.postgres_implementation.user_repository import SQLUserRepository
from repository.redis_implementation.session_repository import SessionRepository
from services import AuthService
from services.auth.abc_auth import AbstractAuthService
from sqlalchemy.ext.asyncio import AsyncSession


@add_factory_to_mapper(AbstractAuthService)
def create_auth_service(
    settings: settings = Depends(get_settings),
    redis_client: Redis = Depends(get_async_redis_client),
    session: AsyncSession = Depends(get_async_session),
):
    cache_client = SessionRepository(redis_client)
    return AuthService(
        cache_client=cache_client,
        jwt_secret_key=settings.jwt_config.jwt_secret_key,
        user_repository=SQLUserRepository(session=session),
    )
