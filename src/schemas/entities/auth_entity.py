from pydantic.main import BaseModel

from schemas.response.user import UserResponse


class AuthEntity(BaseModel):
    user_id: str
    is_superuser: bool = False

    @classmethod
    def from_userinfo(cls, user_info: UserResponse):
        return cls(
            user_id=str(user_info.id),
            is_superuser=user_info.is_superuser,
        )


class RefreshEntity(AuthEntity):
    refresh_token: str
