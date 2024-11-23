from abc import ABC, abstractmethod

from schemas.entities.auth_entity import AuthEntity, RefreshEntity
from schemas.response.token import TokensResponse


class AbstractAuthService(ABC):
    @staticmethod
    @abstractmethod
    def encode_fingerprint(fingerprint: dict) -> str:
        ...

    @abstractmethod
    async def get_fingerprint_by_access_token(self, user_id: str, access_token: str) -> dict:
        ...

    @abstractmethod
    async def get_fingerprint_by_refresh_token(self, user_id: str, access_token: str) -> dict:
        ...

    @abstractmethod
    async def create_token_pair(self, user_payload: AuthEntity, fingerprint: str) -> TokensResponse:
        ...

    @abstractmethod
    async def get_auth_data(self, token: str) -> AuthEntity:
        ...

    @abstractmethod
    async def validate_refresh_token(self, refresh_token: str) -> RefreshEntity:
        ...

    @abstractmethod
    async def remove_tokens_from_cache(self, token: str) -> None:
        ...

    @abstractmethod
    async def refresh_tokens(self, refresh_token: str, user_payload: AuthEntity, fingerprint: str) -> TokensResponse:
        ...

    @abstractmethod
    async def revoke_refresh_token(self, user_id: str, access_token: str) -> None:
        ...
