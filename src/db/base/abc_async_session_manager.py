from abc import ABC, abstractmethod


class BaseAsyncSessionManager(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def async_session(self):
        pass
