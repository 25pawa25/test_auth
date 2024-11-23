from __future__ import annotations

from abc import ABC
from typing import Union

from redis.asyncio import Redis
from repository.base.abc_kv_repository import AbstractKVRepository


class BaseSessionRepository(AbstractKVRepository, ABC):
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    @staticmethod
    def create_access_key(user_id: str, access_token: str) -> str:
        """
        Creating an access key to put in the cache access:<user_id>:<access_token>
        Args:
            user_id
            access_token
        Returns:
            str: access key
        """
        return f"access:{user_id}:{access_token}"

    @staticmethod
    def create_refresh_key(user_id: str, refresh_token: str) -> str:
        """
        Creating a refresh key to put in the cache refresh:<user_id>:<refresh_token>
        Args:
            user_id
            refresh_token
        Returns:
            str: refresh key
        """
        return f"refresh:{user_id}:{refresh_token}"

    async def get(self, key: str, **kwargs) -> str | None:
        value = await self.redis.get(key)
        if value:
            return value.decode()  # type: ignore

    async def delete(self, *keys, **kwargs) -> None:
        await self.redis.delete(*keys)

    async def set(self, key: str, value: Union[str, bytes], expire: int, **kwargs) -> None:
        await self.redis.set(key, value, expire)

    async def has(self, key: str) -> bool:
        if await self.redis.keys(key):
            return True
        return False
