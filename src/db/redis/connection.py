import backoff
from core.config import settings
from db.redis.session_manager import redis_db_manager
from redis import Redis


@backoff.on_exception(backoff.expo, RuntimeError, max_time=30)
async def get_async_redis_client() -> Redis:
    async with redis_db_manager.async_session() as session:
        return session
