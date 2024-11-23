from common.exceptions import AppException
from common.exceptions.base import ObjectAlreadyExists, ObjectDoesNotExist


class UserException(AppException):
    """Base User Exception"""


class UserAlreadyExists(ObjectAlreadyExists):
    """User Already Exists"""


class UserNotExists(ObjectDoesNotExist):
    """User Not Exists"""
