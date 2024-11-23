import uuid
from datetime import datetime
from typing import Union

from passlib.context import CryptContext

from common.exceptions import UserAlreadyExists, IntegrityDataError
from common.exceptions.auth import WrongPassword
from db.postgres.connection import get_postgres_session
from repository.grpc_implementation.transaction_repository import get_grpc_transaction_repository
from repository.interfaces.entity.abc_user_repository import AbstractUserRepository
from repository.interfaces.grpc.abc_transaction_repository import AbstractTransactionRepository
from repository.postgres_implementation.user_repository import SQLUserRepository
from schemas.entities.user_entity import UserEntity
from schemas.request.user import (
    UserLoginSchema,
    UserRegistrationSchema, UserChangeInfoSchema, UserChangePasswordSchema,
)
from schemas.response.user import UserResponse
from services.user.abc_user import AbstractUserService

pwd_context = CryptContext(schemes=["bcrypt"])


class UserService(AbstractUserService):
    def __init__(
            self,
            user_repository: AbstractUserRepository,
            transaction_repository: AbstractTransactionRepository,
    ) -> None:
        self.user_repository = user_repository
        self.transaction_repository = transaction_repository
        self.class_entity = UserEntity

    @staticmethod
    def _verify_password(plan_password: str, hashed_password: str) -> bool:
        """Password validation."""
        return pwd_context.verify(plan_password, hashed_password)

    async def create_user(self, user_schema: UserRegistrationSchema) -> UserResponse:
        """Creating a user."""
        if await self.user_repository.get_user_by_field(email=user_schema.email, raise_if_notfound=False):
            raise UserAlreadyExists("This email has already been registered. Log in or reset the password.")
        user_schema.password = pwd_context.encrypt(user_schema.password)
        user_db = await self.user_repository.create_user(**user_schema.dict())
        await self.transaction_repository.create_user_balance(user_id=str(user_db.id))
        return UserResponse.from_orm(user_db)

    async def login(self, login_schema: UserLoginSchema) -> UserResponse:
        """Authorization of user."""
        user_db = await self.user_repository.get_user_by_field(email=login_schema.email)
        if not self._verify_password(login_schema.password, user_db.password):
            raise WrongPassword("Incorrect email or password.")
        return UserResponse.from_orm(user_db)

    async def change_info(self, user_id: Union[str, uuid.UUID], info_schema: UserChangeInfoSchema) -> UserResponse:
        """Changing user information"""
        user_db = await self.user_repository.get_user_by_field(return_entity=False, id=user_id)
        schema = {
            key: getattr(info_schema, key)
            for key in info_schema.__annotations__
            if getattr(info_schema, key) is not None
        }
        await self.user_repository.update_user_fields(user_db, **schema)
        return UserResponse.from_orm(user_db)

    async def password_change(self, user_id: Union[str, uuid.UUID], password_schema: UserChangePasswordSchema):
        """Changing the user's password"""
        user_db = await self.user_repository.get_user_by_field(return_entity=False, id=user_id)
        await self.user_repository.update_user_fields(
            user_db, password=pwd_context.encrypt(password_schema.new_password), updated_at=datetime.utcnow()
        )

    async def user_info(self, user_id: Union[str, uuid.UUID]) -> UserResponse:
        """Getting user information"""
        user_db = await self.user_repository.get_user_by_field(id=user_id)
        return UserResponse.from_orm(user_db)

    async def verify_user_password(self, user_id: Union[str, uuid.UUID], password: str):
        """
        Verifying the user's password
        Args:
            user_id: id of user
            password: password to verify
        """
        user_db = await self.user_repository.get_user_by_field(id=user_id)
        if not self._verify_password(password, user_db.password):
            raise WrongPassword("Incorrect password.")

    async def check_user_existing(self, user_id: str) -> UserResponse:
        try:
            uuid.UUID(user_id)
        except ValueError:
            raise IntegrityDataError("Invalid user id.")
        if user_db := await self.user_repository.get_user_by_field(id=user_id, raise_if_notfound=False):
            return UserResponse.from_orm(user_db)


async def get_user_service():
    session = await get_postgres_session()
    return UserService(
        user_repository=SQLUserRepository(session=session),
        transaction_repository=get_grpc_transaction_repository()
    )
