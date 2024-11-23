from abc import abstractmethod
from typing import List, Union

from repository.base.abc_kv_repository import AbstractKVRepository


class AbstractSessionRepository(AbstractKVRepository):
    @staticmethod
    def create_access_key(user_id: str, access_token: str) -> str:
        raise NotImplementedError

    @staticmethod
    def create_refresh_key(user_id: str, refresh_token: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def has_refresh(self, refresh_token: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def set_blocked_token(self, **kwargs) -> bool:
        raise NotImplementedError
