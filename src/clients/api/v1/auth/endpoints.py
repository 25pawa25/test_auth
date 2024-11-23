from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import Response
from loguru import logger

from common.dependencies.auth import JWTBearer, Fingerprint
from schemas.entities.auth_entity import AuthEntity
from schemas.request.token import RefreshSchema
from schemas.request.user import UserLoginSchema, UserRegistrationSchema
from schemas.response.token import TokensResponse
from schemas.response.user import UserResponse
from services.auth.abc_auth import AbstractAuthService
from services.user.abc_user import AbstractUserService

router = APIRouter(prefix="/auth", tags=["Auth actions"])


@router.post(
    "/registration",
    summary="Registration",
    description="Registration of users in the system",
    response_model=TokensResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registration(
        request_user: UserRegistrationSchema,
        auth_service: AbstractAuthService = Depends(),
        user_service: AbstractUserService = Depends(),
        fp: dict = Depends(Fingerprint()),
):
    """
    Registers a new user in the system
    Args:
        request_user: UserRegistrationSchema
        auth_service: AuthService
        user_service: UserService
        fp: data of the fingerprint
    Returns:
        JWT tokens
    """
    logger.info(f"Registration: {request_user.safe_data()}")
    user_response = await user_service.create_user(request_user)
    token_response: TokensResponse = await auth_service.create_token_pair(
        AuthEntity.from_userinfo(user_response), auth_service.encode_fingerprint(fp)
    )
    logger.info(f"User created {user_response.id}")
    return token_response


@router.post("/login", summary="Login", description="User login to the account")
async def login(
        request_login: UserLoginSchema,
        auth_service: AbstractAuthService = Depends(),
        user_service: AbstractUserService = Depends(),
        fp: dict = Depends(Fingerprint()),
):
    """
    Login
    Args:
        request_login: UserLoginSchema
        auth_service: AuthService
        user_service: UserService
        fp: data of the fingerprint
    Returns:
        JWT tokens
    """
    logger.info(f"Login: {request_login.json(exclude={'password'})}")
    user_response: UserResponse = await user_service.login(request_login)
    token_response: TokensResponse = await auth_service.create_token_pair(
        AuthEntity.from_userinfo(user_response), auth_service.encode_fingerprint(fp)
    )
    logger.info(f"Login complete: {user_response.json(include={'email'})}")
    return token_response


@router.post("/refresh", summary="Regeneration tokens")
async def refresh_token(
        payload: RefreshSchema,
        user_service: AbstractUserService = Depends(),
        auth_service: AbstractAuthService = Depends(),
        fp: dict = Depends(Fingerprint()),
) -> TokensResponse:
    """
    Refresh tokens of user
    Args:
        payload: RefreshSchema
        user_service: UserService
        auth_service: AuthService
        fp: data of the fingerprint
    Returns:
        JWT tokens
    """
    auth_data: AuthEntity = await auth_service.validate_refresh_token(refresh_token=payload.refresh_token)
    new_auth_data = AuthEntity.from_userinfo(await user_service.user_info(auth_data.user_id))
    return await auth_service.refresh_tokens(payload.refresh_token, new_auth_data, auth_service.encode_fingerprint(fp))


@router.get(
    "/logout", summary="Logout of the account", description="Logout of the user account", status_code=status.HTTP_200_OK
)
async def logout(
        request: Request,
        auth_service: AbstractAuthService = Depends(),
        auth_data: AuthEntity = Depends(JWTBearer()),
):
    """
    Logout of the user
    Args:
        request: Request
        auth_service: AuthService
        auth_data: AuthEntity
    Returns:
        HTTP_204_NO_CONTENT
    """
    access_token = request.headers.get("Authorization").replace("Bearer ", "")
    await auth_service.revoke_refresh_token(auth_data.user_id, access_token)
    logger.info(f"Logout: user_id - {auth_data.user_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
