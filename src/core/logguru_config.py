import logging
import sys
import uuid
from contextvars import ContextVar

from fastapi import Request
from grpc.aio import ServerInterceptor
from loguru import logger

logger_request_id: ContextVar[uuid] = ContextVar("request_id")


async def logging_dependency(request: Request):
    request_id = request.headers.get("X-Request-Id", uuid.uuid4())
    body = await request.body() if "multipart/form-data" not in request.headers.get("content-type", "") else ""
    logger_request_id.set(request_id)
    local_logger = logger.bind(request_headers=dict(request.headers), request_body=body)
    local_logger.info(
        {
            "method": request.method,
            "url": request.url.path,
        }
    )


def format_record(record: dict) -> str:
    record["extra"]["request_id"] = logger_request_id.get()
    if record["exception"]:
        return "{exception}\n"
    return "{time} | {level} | {extra[request_id]} | {message}\n"


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def init_logging():
    loggers = (logging.getLogger(name) for name in logging.root.manager.loggerDict)
    intercept_handler = InterceptHandler()
    for runners_logger in loggers:
        runners_logger.propagate = False
        runners_logger.handlers = [intercept_handler]

    logger_request_id.set(uuid.uuid4())
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": logging.INFO,
                "format": format_record,
                "serialize": False,
            }
        ]
    )
    logger.info("Init logger")


class LoggingClientInterceptor(ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        request_headers = dict(handler_call_details.invocation_metadata)

        logger_request_id.set(request_headers.get("X-Request-ID", uuid.uuid4()))
        local_logger = logger.bind(request_headers=request_headers)
        local_logger.info(f"method: {handler_call_details.method}")

        return await continuation(handler_call_details)


logging_interceptor = LoggingClientInterceptor()
