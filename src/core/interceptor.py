import grpc

from core.config import settings


class SignatureValidationInterceptor(grpc.aio.ServerInterceptor):
    def __init__(self):
        self._auth_token = settings.grpc_server.auth_token
        self._auth_header_key = "authorization"
        self._auth_header_value = f"Bearer {self._auth_token}"

    async def intercept_service(self, continuation, handler_call_details):
        for key, value in handler_call_details.invocation_metadata:
            if not self._auth_token or (key == self._auth_header_key and value == self._auth_header_value):
                return await continuation(handler_call_details)

        async def abort_request(request, context):
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid token")

        return grpc.unary_unary_rpc_method_handler(abort_request)


signature_interceptor = SignatureValidationInterceptor()
