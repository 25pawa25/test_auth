from abc import ABC, abstractmethod
from typing import Union


class AbstractKVRepository(ABC):
    @abstractmethod
    async def get(self, key: str, **kwargs) -> Union[str, None]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *keys, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: Union[str, bytes], expire: int, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def has(self, key: str) -> bool:
        raise NotImplementedError
