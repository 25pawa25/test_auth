import uuid
from abc import ABC, abstractmethod
from typing import Any, List, Optional

from schemas.entities.base_entity import BaseEntity


class ContextManagerRepository(ABC):
    @abstractmethod
    async def commit(self):
        ...

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.commit()


class BaseReadOnlyRepository(ABC):
    @abstractmethod
    async def get_or_create(self, **kwargs):
        ...

    @abstractmethod
    async def get_by(self, **kwargs) -> BaseEntity:
        ...

    @abstractmethod
    async def list(self, limit: Optional[int] = None, offset: Optional[int] = None, **filters) -> List[BaseEntity]:
        ...


class BaseWriteOnlyRepository(ContextManagerRepository):
    @abstractmethod
    async def add(self, other: BaseEntity) -> BaseEntity:
        ...

    @abstractmethod
    async def add_all(self, others: List[BaseEntity]) -> None:
        ...

    @abstractmethod
    async def remove(self, self_id: uuid) -> bool:
        ...

    @abstractmethod
    async def update(self, self_id: uuid.UUID, **params) -> BaseEntity:
        ...


class BaseRepository(BaseReadOnlyRepository, BaseWriteOnlyRepository, ABC):
    entity_class: BaseEntity = None

    def get_entity_class(self):
        if self.entity_class is None:
            raise NotImplementedError("Initialise `entity_class`")
        return self.entity_class

    def to_entity(self, obj: Any):
        return self.get_entity_class().from_orm(obj)
