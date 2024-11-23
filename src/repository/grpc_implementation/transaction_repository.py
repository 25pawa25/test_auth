from functools import lru_cache

from grpc.aio import AioRpcError, insecure_channel

from clients.grpc.proto.transaction import transaction_pb2
from clients.grpc.proto.transaction.transaction_pb2_grpc import TransactionStub
from common.exceptions.grpc import GRPCConnectionException
from core.config import settings
from repository.interfaces.grpc.abc_transaction_repository import AbstractTransactionRepository


class GRPCTransactionRepository(AbstractTransactionRepository):
    def __init__(self):
        self.metadata = settings.transaction_grpc.metadata

    @property
    def channel(self):
        return insecure_channel(settings.transaction_grpc.url)

    @property
    def stub(self):
        return TransactionStub(self.channel)

    async def create_user_balance(self, user_id: str):
        """
        create_user_balance
        Args:
            user_id: id of the user
        """
        try:
            balance_id = await self.stub.CreateUserBalance(
                transaction_pb2.CreateUserBalanceRequest(user_id=user_id), metadata=self.metadata
            )
            return balance_id
        except AioRpcError:
            raise GRPCConnectionException("Error while creating user balance")


@lru_cache()
def get_grpc_transaction_repository() -> AbstractTransactionRepository:
    return GRPCTransactionRepository()
