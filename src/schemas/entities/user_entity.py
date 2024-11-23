from datetime import datetime

from schemas.entities.base_entity import BaseEntity


class UserEntity(BaseEntity):
    first_name: str
    last_name: str
    email: str
    password: str
    is_superuser: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
