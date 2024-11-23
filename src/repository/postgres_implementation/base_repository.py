import uuid
from typing import List, Optional

from common.exceptions import IntegrityDataError
from common.exceptions.base import ObjectDoesNotExist
from db.postgres.models.base_model import BaseModel
from repository.base.abc_entity_repository import BaseRepository
from schemas.entities.base_entity import BaseEntity
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class SQLRepository(BaseRepository):
    class_model: BaseModel = None

    def __init__(self, session: AsyncSession):
        if not self.class_model:
            raise NotImplementedError("class_method not implement")
        self.session = session

    async def get_or_create(self, **kwargs) -> BaseEntity:
        instance = await self.get_by(**kwargs)
        if not instance:
            instance = self.class_model(**kwargs)
            self.session.add(instance)
            await self.commit()
        return self.to_entity(instance)

    async def list(self, limit: Optional[int] = None, offset: Optional[int] = None, **filters) -> List[BaseEntity]:
        query = select(self.class_model).filter_by(**filters)
        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        result = await self.session.execute(query)
        return [self.to_entity(obj) for obj in result.scalars().all()]

    async def add(self, other: BaseEntity) -> BaseEntity:
        try:
            model_obj = self.class_model(**other.dict(exclude_none=True))
            self.session.add(model_obj)
            await self.commit()
            return self.to_entity(model_obj)
        except IntegrityError as e:
            raise IntegrityDataError(self.class_model.__name__, e)

    async def add_all(self, data: List[BaseEntity]) -> None:
        try:
            self.session.add_all([self.class_model(**entity.dict(exclude_none=True)) for entity in data])
        except IntegrityError as e:
            raise IntegrityDataError(self.class_model.__name__, e)

    async def remove(self, self_id: uuid.UUID) -> None:
        try:
            query = select(self.class_model).filter_by(id=self_id)
            element = await self.session.scalar(query)
            if element is not None:
                await self.session.delete(element)
                await self.session.commit()
        except Exception:
            raise

    async def update(self, self_id: uuid.UUID, **params) -> BaseEntity:
        stmt = select(self.class_model).filter_by(id=self_id)
        instance = await self.session.scalar(stmt)
        if not instance:
            raise ObjectDoesNotExist("Object does not exist", id=str(self_id))
        for param in params:
            if hasattr(instance, param):
                setattr(instance, param, params[param])
        try:
            await self.session.commit()
        except IntegrityError as e:
            raise IntegrityDataError(self.class_model.__name__, e)

        await self.session.refresh(instance)
        return self.to_entity(instance)

    async def commit(self):
        await self.session.commit()

    async def get_by(self, **kwargs) -> Optional[BaseEntity]:
        stmt = select(self.class_model).filter_by(**kwargs)
        instance = await self.session.scalar(stmt)
        return self.to_entity(instance) if instance else None
