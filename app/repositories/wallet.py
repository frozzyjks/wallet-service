from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet
from app.schemas.wallet import OperationType


class WalletRepository:
    @staticmethod
    async def get_for_update(
        session: AsyncSession,
        wallet_id,
    ) -> Wallet | None:
        result = await session.execute(
            select(Wallet)
            .where(Wallet.id == wallet_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    @staticmethod
    def apply_operation(
        wallet: Wallet,
        operation_type: OperationType,
        amount: int,
    ) -> None:
        if operation_type == OperationType.DEPOSIT:
            wallet.balance += amount
        else:
            if wallet.balance < amount:
                raise ValueError("Insufficient funds")
            wallet.balance -= amount
