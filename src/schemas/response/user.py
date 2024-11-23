from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_superuser: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

    @staticmethod
    def to_grpc(instance: "UserResponse"):
        return dict(
            id=str(instance.id),
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            is_superuser=instance.is_superuser,
            is_active=instance.is_active,
            created_at=str(instance.created_at),
            updated_at=str(instance.updated_at),
        )
