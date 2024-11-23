from clients.api.main import setup_routers
from common.dependencies.main import setup_dependencies
from common.exception_handlers.init_handlers import init_handlers
from common.swagger_ui.tags_metadata import tags_metadata
from core.logguru_config import init_logging
from fastapi import FastAPI
from lifespan import lifespan


def create_app():
    init_logging()
    app = FastAPI(openapi_tags=tags_metadata, lifespan=lifespan)
    setup_routers(app)
    setup_dependencies(app)
    init_handlers(app)
    return app


app = create_app()
