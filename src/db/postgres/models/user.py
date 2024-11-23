from sqlalchemy import Boolean, PrimaryKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped

from db.postgres.models.base_model import BaseModel, Column
from db.postgres.models.mixins import IdMixin, TsMixinCreated, TsMixinUpdated


class AuthUser(BaseModel, IdMixin, TsMixinCreated, TsMixinUpdated):
    """Data model for user db table."""

    __tablename__ = "user"
    __table_args__ = (PrimaryKeyConstraint("id", name="user_pkey"), UniqueConstraint("email", name="user_email_unique"))

    first_name: Mapped[str] = Column(String(127), nullable=True)
    last_name: Mapped[str] = Column(String(127), nullable=True)
    email: Mapped[str] = Column(String(255), nullable=False)
    password: Mapped[str] = Column(String(127), nullable=False)
    is_superuser: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return (
            f"AuthUser(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, "
            f"email={self.email}, password={self.password}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})"
        )
