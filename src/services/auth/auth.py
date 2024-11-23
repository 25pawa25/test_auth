import base64
import json
from datetime import datetime, timedelta

import jwt
from loguru import logger
from pydantic import ValidationError

import common.exceptions.auth as auth_exceptions
from common.constants import EXPIRE_ACCESS_TOKEN, EXPIRE_REFRESH_TOKEN
from core.config import settings
from repository.interfaces.entity.abc_user_repository import AbstractUserRepository
from repository.interfaces.kv.abc_session_repository import AbstractSessionRepository
from schemas.entities.auth_entity import AuthEntity, RefreshEntity
from schemas.response.token import TokensResponse
from services.auth.base_auth import BaseAuthService


class AuthService(BaseAuthService):
    encode_algorithm: str = settings.jwt_config.encode_algorithm

    def __init__(
            self,
            cache_client: AbstractSessionRepository,
            jwt_secret_key: str,
            user_repository: AbstractUserRepository,
    ) -> None:
        self.jwt_secret_key = jwt_secret_key
        self.cache_client = cache_client
        self.user_repository = user_repository

    async def get_fingerprint_by_access_token(self, user_id: str, access_token: str) -> dict:
        """
        Get fingerprint by access token
        Args:
            user_id: user_id
            access_token: access token

        Returns:
            dict
        """
        refresh_token = await self.cache_client.get(self.cache_client.create_access_key(user_id, access_token))
        if not refresh_token:
            logger.error(f"Can't get token from cache! {access_token}")
            raise auth_exceptions.TokenException("Bad device token error!")
        return await self.get_fingerprint_by_refresh_token(user_id, refresh_token)

    async def get_fingerprint_by_refresh_token(self, user_id: str, refresh_token: str) -> dict:
        """
        Get fingerprint by refresh token
        Args:
            user_id: user_id
            refresh_token: access token

        Returns:
            dict
        """
        fingerprint_base64 = await self.cache_client.get(self.cache_client.create_refresh_key(user_id, refresh_token))
        if not fingerprint_base64:
            logger.error(f"Can't get fingerprint from cache! {refresh_token}")
            raise auth_exceptions.TokenException("Bad device token error!")
        fingerprint = json.loads(base64.b64decode(fingerprint_base64).decode())
        return fingerprint

    async def create_token_pair(self, user_payload: AuthEntity, fingerprint: str) -> TokensResponse:
        """
        Create token pair
        Args:
            user_payload: AuthEntity
            fingerprint: fingerprint

        Returns:
            TokensResponse
        """
        refresh_token = await self.create_refresh_token(user_payload, fingerprint)
        access_token = await self.create_access_token(user_payload, refresh_token)
        return TokensResponse(access_token=access_token, refresh_token=refresh_token)

    def _create_token(self, expire_timestamp: int, user_payload: AuthEntity) -> str:
        payload = {
            "sub": "authentication",
            "exp": expire_timestamp,
            "iat": int(datetime.utcnow().timestamp()),
            **user_payload.dict(),
        }
        try:
            token = jwt.encode(payload, self.jwt_secret_key, algorithm=self.encode_algorithm)
        except (ValueError, TypeError):
            logger.error("Can't create jwt token! See JWT_SECRET_KEY env, or something else...", exc_info=True)
            raise auth_exceptions.TokenEncodeException("Can't create jwt token", name=user_payload.user_id)
        return token

    def _validate_token(self, token: str) -> dict:
        try:
            payload: dict = jwt.decode(token, self.jwt_secret_key, algorithms=[self.encode_algorithm])
        except (
                jwt.DecodeError,
                jwt.InvalidKeyError,
                jwt.InvalidIssuerError,
                jwt.InvalidSignatureError,
        ):
            logger.error(f"Can't decode jwt token! See {token}")
            raise auth_exceptions.TokenDecodeException("Token is invalid or expired")
        except jwt.exceptions.ExpiredSignatureError as error:
            logger.warning(f"Token is expired! error = {error}")
            raise auth_exceptions.TokenExpiredException("Token is invalid or expired")
        return payload

    async def create_refresh_token(self, user_payload: AuthEntity, fingerprint: str) -> str:
        """Генерация refresh токена и запись в кеш."""

        refresh_expire = (datetime.now() + timedelta(seconds=EXPIRE_REFRESH_TOKEN)).timestamp()
        refresh_token = self._create_token(expire_timestamp=int(refresh_expire), user_payload=user_payload)
        await self.cache_client.set(
            key=self.cache_client.create_refresh_key(user_payload.user_id, refresh_token),
            value=fingerprint,
            expire=EXPIRE_REFRESH_TOKEN,
        )
        return refresh_token

    async def create_access_token(self, user_payload: AuthEntity, refresh_token: str) -> str:
        """Генерация access токена."""

        access_expire = (datetime.now() + timedelta(seconds=EXPIRE_ACCESS_TOKEN)).timestamp()
        access_token = self._create_token(expire_timestamp=int(access_expire), user_payload=user_payload)
        await self.cache_client.set(
            key=self.cache_client.create_access_key(user_payload.user_id, access_token),
            value=refresh_token,
            expire=EXPIRE_REFRESH_TOKEN,
        )
        return access_token

    async def get_auth_data(self, token: str) -> AuthEntity:
        """Валидация access токена."""
        payload = self._validate_token(token)
        try:
            return AuthEntity(**payload)
        except ValidationError:
            logger.error(f"Can't get user_id from token {token}! Payload {payload}")
            raise auth_exceptions.TokenException("Token is invalid or expired")

    async def validate_refresh_token(self, refresh_token: str) -> RefreshEntity:
        """Валидация refresh токена."""
        if not await self.cache_client.has_refresh(refresh_token):
            logger.error(f"Can't get token from cache! {refresh_token}")
            raise auth_exceptions.TokenException("Bad token error!")
        auth_data: AuthEntity = await self.get_auth_data(refresh_token)
        return RefreshEntity(**auth_data.dict(), refresh_token=refresh_token)

    async def refresh_tokens(self, refresh_token: str, user_payload: AuthEntity, fingerprint: str) -> TokensResponse:
        """Обновление токенов"""
        refresh_key = self.cache_client.create_refresh_key(user_payload.user_id, refresh_token)
        await self.remove_tokens_from_cache(f"access:{user_payload.user_id}:*", refresh_key)
        return await self.create_token_pair(user_payload, fingerprint)

    async def remove_tokens_from_cache(self, *tokens) -> None:
        """Удаление токенов из БД."""
        await self.cache_client.delete(*tokens)

    async def revoke_refresh_token(self, user_id: str, access_token: str) -> None:
        """Помещение access токена в key и удаление refresh токена"""
        access_key = self.cache_client.create_access_key(user_id, access_token)
        refresh_token = await self.cache_client.get(access_key)
        refresh_key = self.cache_client.create_refresh_key(user_id, refresh_token)
        await self.cache_client.set_blocked_token(
            user_id=user_id, access_token=access_token, value="True", expire=EXPIRE_ACCESS_TOKEN
        )
        await self.remove_tokens_from_cache(access_key, refresh_key)
