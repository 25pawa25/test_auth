import uuid
from abc import ABC
from typing import Optional

from pydantic import BaseModel


class BaseEntity(BaseModel, ABC):
    id: Optional[uuid.UUID]

    class Config:
        orm_mode = True
