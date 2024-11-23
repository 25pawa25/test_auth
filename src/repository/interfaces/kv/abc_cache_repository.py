from abc import abstractmethod

from repository.base.abc_kv_repository import AbstractKVRepository


class AbstractRedisCacheRepository(AbstractKVRepository):
    @abstractmethod
    async def redis_has_key(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def redis_set_key(self, key: str, value: str, expire: int):
        raise NotImplementedError
