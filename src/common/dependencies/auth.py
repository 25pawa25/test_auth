from typing import Optional, Union

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from starlette.status import HTTP_401_UNAUTHORIZED

from schemas.entities.auth_entity import AuthEntity
from services.auth.abc_auth import AbstractAuthService

api_key_header = APIKeyHeader(name="Authorization", scheme_name="Bearer", auto_error=False)


class Fingerprint:
    async def __call__(self, request: Request) -> Union[str, dict]:
        ip = request.headers.get("X-Forwarded-For") or request.client.host
        return {"user_agent": request.headers.get("User-Agent"), "ip": ip}


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
            self,
            request: Request,
            auth_service: AbstractAuthService = Depends(),
            fp: dict = Depends(Fingerprint()),
    ) -> Optional[AuthEntity]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authorized!")
        if not credentials.scheme == 'Bearer':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Only Bearer token might be accepted')
        auth_data: AuthEntity = await auth_service.get_auth_data(credentials.credentials)
        await auth_service.get_fingerprint_by_access_token(auth_data.user_id, credentials.credentials)
        logger.debug(f"User request: user_id - {auth_data.user_id}")
        return auth_data


class JWTBearerAdmin:
    async def __call__(self, auth_data: AuthEntity = Depends(JWTBearer())) -> AuthEntity:
        if not auth_data.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return auth_data
