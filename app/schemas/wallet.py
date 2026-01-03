from enum import Enum
from pydantic import BaseModel, Field


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletOperation(BaseModel):
    operation_type: OperationType
    amount: int = Field(gt=0)


class WalletResponse(BaseModel):
    wallet_id: str
    balance: int
