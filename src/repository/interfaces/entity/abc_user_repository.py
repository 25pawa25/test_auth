from abc import abstractmethod
from typing import Optional

from db.postgres.models.user import AuthUser
from repository.base.abc_entity_repository import BaseRepository
from schemas.entities.base_entity import BaseEntity


class AbstractUserRepository(BaseRepository):
    @abstractmethod
    async def get_user_by_field(
        self, raise_if_notfound: bool = True, return_entity: bool = False, **fields
    ) -> Optional[BaseEntity]:
        pass

    @abstractmethod
    async def update_user_fields(self, user_db: AuthUser, **fields) -> None:
        pass

    @abstractmethod
    async def create_user(self, **fields) -> BaseEntity:
        pass

    @abstractmethod
    async def delete_user(self, user_id: str):
        pass
