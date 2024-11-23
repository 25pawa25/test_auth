from abc import ABC, abstractmethod


class AbstractTransactionRepository(ABC):
    @abstractmethod
    async def create_user_balance(self, user_id: str):
        pass
