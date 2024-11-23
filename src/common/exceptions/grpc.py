from common.exceptions import AppException


class GRPCError(AppException):
    pass


class GRPCConnectionException(GRPCError):
    pass
