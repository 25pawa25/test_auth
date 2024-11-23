from functools import lru_cache
from typing import Optional

import grpc
from loguru import logger

from clients.grpc.proto.auth import auth_pb2
from clients.grpc.proto.auth.auth_pb2_grpc import AuthServicer
from common.exceptions.user import UserNotExists
from schemas.response.user import UserResponse
from services.user.abc_user import AbstractUserService
from services.user.user import get_user_service


class AuthServicer(AuthServicer):
    def __init__(self):
        self.user_service: Optional[AbstractUserService] = None

    async def init_services(self):
        self.user_service = await get_user_service()

    async def CheckUserExisting(self, request, context) -> auth_pb2.CheckUserExistingResponse:
        """
        GRPC check user existing by user_id method
        Args:
            request: GRPC request object
            context: GRPC context object for response
        Returns:
            CheckUserExistingResponse
            context INTERNAL if error in service working
        """
        try:
            if user_info := await self.user_service.check_user_existing(request.user_id):
                return auth_pb2.CheckUserExistingResponse(**UserResponse.to_grpc(user_info))
            return auth_pb2.CheckUserExistingResponse()
        except UserNotExists as e:
            error_msg = "Error occurred: " + str(e)
            context.set_details(error_msg)
            logger.warning(error_msg)
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
        except Exception as e:
            error_msg = "Error occurred: " + str(e)
            context.set_details(error_msg)
            logger.opt(exception=e).error(error_msg)
            context.set_code(grpc.StatusCode.INTERNAL)


@lru_cache
async def get_auth_servicer():
    servicer = AuthServicer()
    await servicer.init_services()
    return servicer
