class AppException(Exception):
    """Base Exception"""

    def __init__(self, msg, **params):
        if not hasattr(self, "params"):
            self.params = {}
        self.params.update(params)


class ObjectDoesNotExist(AppException):
    """Does not exist Exception"""


class IntegrityDataError(Exception):
    """Integrity Data Exception"""


class ObjectAlreadyExists(AppException):
    """Object already exists Exception"""
