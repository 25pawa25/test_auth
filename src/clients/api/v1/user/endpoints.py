from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from loguru import logger

from common.dependencies.auth import JWTBearer
from common.exceptions import UserException
from schemas.entities.auth_entity import AuthEntity
from schemas.request.user import UserChangeInfoSchema, UserChangePasswordSchema
from schemas.response.user import UserResponse
from services.user.abc_user import AbstractUserService

router = APIRouter(prefix="/user", tags=["User actions"])


@router.get("/info", summary="Profile", description="Getting user Information", response_model=UserResponse)
async def user_info(
        service: AbstractUserService = Depends(),
        auth_data: AuthEntity = Depends(JWTBearer()),
) -> UserResponse:
    """
    Getting authorized user Information
    Args:
        service: UserService
        auth_data: AuthEntity
    Returns:
        UserResponse
    """
    return await service.user_info(auth_data.user_id)


@router.patch(
    "/info",
    summary="Change user data",
    description="Changing information about user",
    response_model=UserResponse,
)
async def change_user_info(
        request_user_info: UserChangeInfoSchema,
        service: AbstractUserService = Depends(),
        auth_data: AuthEntity = Depends(JWTBearer()),
) -> UserResponse:
    """
    Changing information about authorized user
    Args:
        request_user_info: UserChangeInfoSchema
        service: UserService
        auth_data: AuthEntity
    Returns:
        UserResponse
    """
    try:
        user_response = await service.change_info(auth_data.user_id, request_user_info)
    except UserException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return user_response


@router.patch(
    "/password",
    summary="Change password",
    description="Changing the password of an authorized user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def password_change(
        request_change_password: UserChangePasswordSchema,
        user_service: AbstractUserService = Depends(),
        auth_data: AuthEntity = Depends(JWTBearer()),
):
    """
    Changing the password of an authorized user
    Args:
        request_change_password: new password scheme
        user_service: UserService
        auth_data: data of the user
    Returns:
        HTTP_204_NO_CONTENT
    """
    await user_service.verify_user_password(auth_data.user_id, request_change_password.password)
    await user_service.password_change(auth_data.user_id, request_change_password)
    logger.info(f"Change password complete: user_id - {auth_data.user_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
