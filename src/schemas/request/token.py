from pydantic import BaseModel


class RefreshSchema(BaseModel):
    refresh_token: str
