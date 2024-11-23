from repository.interfaces.kv.abc_cache_repository import AbstractRedisCacheRepository
from repository.redis_implementation.base_repository import BaseSessionRepository


class RedisCacheRepository(BaseSessionRepository, AbstractRedisCacheRepository):
    async def redis_has_key(self, key: str) -> bool:
        """
        Check if a key exists in the cache
        Args:
            key: the key to check the value in the cache
        Returns:
            fp
        """
        return await self.has(key)

    async def redis_set_key(self, key: str, value: str, expire: int):
        """
        Set key to cache
        Args:
            key: the key to set in the cache
            value: the value to set in the cache
            expire: expire time
        """
        await self.set(
            key=key,
            value=value,
            expire=expire,
        )
