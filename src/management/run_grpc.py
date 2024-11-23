import asyncio

import grpc
from clients.grpc.proto.auth import auth_pb2_grpc
from clients.grpc.servicer.auth import get_auth_servicer
from core.config import settings
from core.interceptor import signature_interceptor
from core.logguru_config import logging_interceptor
from loguru import logger
from management.base.base_command import BaseCommand


class Command(BaseCommand):
    help: str = "Run grpc"

    def add_arguments(self):
        self.parser.add_argument("--host", default=settings.grpc_server.host)
        self.parser.add_argument("--port", default=settings.grpc_server.port)

    async def start_server(self, host: str, port: int):
        servicer = await self.servicer
        server = grpc.aio.server(interceptors=(logging_interceptor, signature_interceptor))
        auth_pb2_grpc.add_AuthServicer_to_server(servicer, server)
        server.add_insecure_port(f"{host}:{port}")
        await server.start()
        logger.info(f"Server process start in {host}:{port}")
        await server.wait_for_termination()

    @property
    async def servicer(self):
        return await get_auth_servicer()

    def execute(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start_server(self.args.host, self.args.port))
