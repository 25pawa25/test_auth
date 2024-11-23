from typing import Optional

from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.networks import EmailStr

regex_password = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,32}$"


class UserEmailSchema(BaseModel):
    email: EmailStr


class UserRegistrationSchema(UserEmailSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str = Field(..., regex=regex_password)

    def safe_data(self):
        return self.dict(exclude={"password"})


class UserLoginSchema(UserEmailSchema):
    password: str

    class Config:
        schema_extra = {"example": {"email": "user@example.com", "password": "1234QWer"}}


class UserChangeInfoSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_superuser: Optional[bool] = None
    is_active: Optional[bool] = None


class UserChangePasswordSchema(BaseModel):
    password: str
    new_password: str = Field(..., regex=regex_password)

    class Config:
        schema_extra = {"example": {"password": "1234QWer", "new_password": "4321QWer"}}
