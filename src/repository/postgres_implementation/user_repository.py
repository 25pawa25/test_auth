from datetime import datetime
from typing import Optional

from loguru import logger
from sqlalchemy import desc, select

from common.exceptions.user import UserNotExists
from db.postgres.models.user import AuthUser
from repository.interfaces.entity.abc_user_repository import AbstractUserRepository
from repository.postgres_implementation.base_repository import SQLRepository
from schemas.entities.base_entity import BaseEntity
from schemas.entities.user_entity import UserEntity


class SQLUserRepository(SQLRepository, AbstractUserRepository):
    class_model = AuthUser
    entity_class = UserEntity

    async def get_user_by_field(
            self, raise_if_notfound: bool = True, return_entity: bool = True, **fields
    ) -> Optional[BaseEntity]:
        """
        Getting a user by field if it exists
        Args:
            raise_if_notfound: raise if user not found
            return_entity: return instance or entity
            **fields: fields of user
        Returns:
            user instance
        """
        stmt = select(self.class_model).filter_by(**fields)
        if instance := await self.session.scalar(stmt):
            return self.to_entity(instance) if return_entity else instance
        if raise_if_notfound:
            logger.error(f"User does not exists: {fields}")
            raise UserNotExists("User does not exists", **fields)

    async def update_user_fields(self, user_db: AuthUser, **fields) -> None:
        """
        Updating a user
        Args:
            user_db: user instance
            **fields: fields of user
        """
        for field, value in fields.items():
            if hasattr(user_db, field):
                setattr(user_db, field, value)
        user_db.updated_at = datetime.utcnow()
        await self.session.commit()

    async def create_user(self, **fields) -> BaseEntity:
        """
        Creating a user
        Args:
            **fields: fields of user

        Returns:
            user instance
        """
        db_user = self.class_model(**fields)
        self.session.add(db_user)

        await self.session.commit()

        result = await self.session.scalars(
            select(self.class_model)
            .order_by(desc(self.class_model.created_at))
        )
        return result.first()

    async def delete_user(self, user_id: str):
        """
        Deleting a user
        Args:
            user_id: id of the user
        """
        db_user = await self.get_user_by_field(id=user_id)
        await self.session.delete(db_user)
        await self.session.commit()
