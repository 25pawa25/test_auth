import uuid
from abc import ABC, abstractmethod
from typing import Optional, Union

from repository.interfaces.entity.abc_user_repository import AbstractUserRepository
from schemas.request.user import (
    UserChangeInfoSchema,
    UserLoginSchema,
    UserRegistrationSchema, UserChangePasswordSchema,
)
from schemas.response.user import UserResponse


class AbstractUserService(ABC):
    user_repository: Optional[AbstractUserRepository] = None

    @abstractmethod
    async def create_user(self, user_schema: UserRegistrationSchema) -> UserResponse:
        ...

    @abstractmethod
    async def login(self, user: UserLoginSchema) -> UserResponse:
        ...

    @abstractmethod
    async def change_info(self, user_id: Union[str, uuid.UUID], info_schema: UserChangeInfoSchema) -> UserResponse:
        ...

    @abstractmethod
    async def user_info(self, user_id: Union[str, uuid.UUID]) -> UserResponse:
        ...

    @abstractmethod
    async def check_user_existing(self, user_id: str) -> UserResponse:
        ...

    @abstractmethod
    async def password_change(self, user_id: Union[str, uuid.UUID], password_schema: UserChangePasswordSchema):
        ...

    @abstractmethod
    async def verify_user_password(self, user_id: Union[str, uuid.UUID], password: str):
        ...
