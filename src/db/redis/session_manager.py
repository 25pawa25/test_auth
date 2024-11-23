import contextlib

from db.base.abc_async_session_manager import BaseAsyncSessionManager
from redis.asyncio import Redis


class RedisSessionManager(BaseAsyncSessionManager):
    def __init__(self) -> None:
        self._sessionmaker = None

    def init(self, host: str, port: int) -> None:
        """
        Init sessionmaker of redis database
        Args:
            host: redis host
            port: redis port

        Returns:
            None
        """
        self._sessionmaker = self._redis_sessionmaker(host, port)

    @staticmethod
    def _redis_sessionmaker(host: str, port: int):
        """
        Init redis session
        Args:
            host: redis host
            port: redis port

        Returns:
            redis sessionmaker(function)
        """

        def get_client():
            client: Redis = Redis(host=host, port=port)
            return client

        return get_client

    async def close(self) -> None:
        """
        Delete sessionmaker of redis database
        Returns:
            None
        """
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def async_session(self) -> Redis:
        """
        Get session of redis database
        Returns:
            yield session of redis database
        """
        if self._sessionmaker is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._sessionmaker() as session:
            yield session


redis_db_manager = RedisSessionManager()
