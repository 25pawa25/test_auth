from clients.api import router as top_router
from core.logguru_config import logging_dependency
from fastapi import APIRouter, Depends, FastAPI


def setup_routers(app: FastAPI):
    root_router = APIRouter()
    root_router.include_router(top_router)
    app.include_router(root_router, dependencies=[Depends(logging_dependency)])
