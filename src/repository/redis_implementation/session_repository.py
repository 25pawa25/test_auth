from repository.interfaces.kv.abc_session_repository import AbstractSessionRepository
from repository.redis_implementation.base_repository import BaseSessionRepository


class SessionRepository(BaseSessionRepository, AbstractSessionRepository):
    async def has_refresh(self, refresh_token: str) -> bool:
        """
        Check if refresh token exists
        Args:
            refresh_token: refresh_token

        Returns:
            bool
        """
        return await self.has(f"refresh:*:{refresh_token}")

    async def set_blocked_token(self, **kwargs) -> None:
        """
        Set blocked token
        Args:
            **kwargs:
        """
        await self.set(
            key=f"blocked:{kwargs.get('user_id')}:{kwargs.get('access_token')}",
            value=kwargs.get("value"),
            expire=kwargs.get("expire"),
        )
