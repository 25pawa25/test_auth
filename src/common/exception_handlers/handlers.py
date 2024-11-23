from fastapi import status

from common.exception_handlers import RequestIdJsonExceptionHandler
from common.exceptions import IntegrityDataError
from common.exceptions.auth import AuthException, TokenDoesNotTimedOut, TokenException
from common.exceptions.base import ObjectAlreadyExists, ObjectDoesNotExist
from common.exceptions.grpc import GRPCError


class ValidationExceptionHandler(RequestIdJsonExceptionHandler):
    status_code = status.HTTP_400_BAD_REQUEST
    exception = IntegrityDataError


class AuthExceptionHandler(RequestIdJsonExceptionHandler):
    status_code = status.HTTP_403_FORBIDDEN
    exception = AuthException


class TokenExceptionHandler(RequestIdJsonExceptionHandler):
    status_code = status.HTTP_401_UNAUTHORIZED
    exception = TokenException


class TokenDoesNotTimedOutHandler(RequestIdJsonExceptionHandler):
    status_code = status.HTTP_400_BAD_REQUEST
    exception = TokenDoesNotTimedOut


class ObjectDoesNotExistExceptionHandler(RequestIdJsonExceptionHandler):
    status_code = status.HTTP_404_NOT_FOUND
    exception = ObjectDoesNotExist


class ObjectAlreadyExistsExceptionHandler(RequestIdJsonExceptionHandler):
    status_code = status.HTTP_409_CONFLICT
    exception = ObjectAlreadyExists


class GRPCExceptionHandler(RequestIdJsonExceptionHandler):
    status_code = status.HTTP_502_BAD_GATEWAY
    exception = GRPCError
