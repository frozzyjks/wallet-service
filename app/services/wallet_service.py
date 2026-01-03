from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.wallet import Wallet


class WalletService:
    @staticmethod
    async def operate(
            db: AsyncSession,
            wallet_id: str,
            operation_type: str,
            amount: int,
    ) -> Wallet:
        if amount <= 0:
            raise ValueError("Amount must be positive")

        async with db.begin_nested():
            result = await db.execute(
                select(Wallet).where(Wallet.id == wallet_id).with_for_update()
            )
            wallet = result.scalar_one_or_none()

            if not wallet:
                if operation_type == "DEPOSIT":
                    # СОЗДАЕМ кошелек, если его нет при депозите
                    wallet = Wallet(id=wallet_id, balance=0)
                    db.add(wallet)
                else:
                    raise ValueError("Wallet not found")

            if operation_type == "DEPOSIT":
                wallet.balance += amount
            elif operation_type == "WITHDRAW":
                if wallet.balance < amount:
                    raise ValueError("Insufficient funds")
                wallet.balance -= amount

        await db.commit()
        return wallet

    @staticmethod
    async def get_wallet(db: AsyncSession, wallet_id: str):
        result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
        return result.scalar_one_or_none()