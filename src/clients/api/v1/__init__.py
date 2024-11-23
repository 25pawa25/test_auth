from clients.api.v1.auth import auth_routers
from clients.api.v1.user import user_routers
from fastapi import APIRouter

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(auth_routers)
v1_router.include_router(user_routers)
