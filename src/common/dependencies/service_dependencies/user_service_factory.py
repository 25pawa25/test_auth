from common.dependencies.registrator import add_factory_to_mapper
from db.postgres.connection import get_async_session
from fastapi import Depends

from repository.grpc_implementation.transaction_repository import get_grpc_transaction_repository
from repository.postgres_implementation.user_repository import SQLUserRepository
from services.user.abc_user import AbstractUserService
from services.user.user import UserService
from sqlalchemy.ext.asyncio import AsyncSession


@add_factory_to_mapper(AbstractUserService)
def create_user_service(
    session: AsyncSession = Depends(get_async_session),
):
    return UserService(
        user_repository=SQLUserRepository(session=session),
        transaction_repository=get_grpc_transaction_repository(),
    )
