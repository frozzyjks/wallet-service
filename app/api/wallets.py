from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from pydantic import BaseModel, Field
from typing import Literal
from app.db.deps import get_db
from app.schemas.wallet import WalletOperation, WalletResponse
from app.services.wallet_service import WalletService
from app.models.wallet import Wallet

from uuid import UUID

logger = logging.getLogger(__name__)
router = APIRouter()


class OperationRequest(BaseModel):
    operation_type: Literal["DEPOSIT", "WITHDRAW"]
    amount: int = Field(gt=0, description="Сумма должна быть больше нуля")


@router.post("/{wallet_uuid}/operation")
async def wallet_operation(
        wallet_uuid: str,
        operation: OperationRequest,
        db: AsyncSession = Depends(get_db)
):
    try:
        wallet = await WalletService.operate(
            db=db,
            wallet_id=wallet_uuid,
            operation_type=operation.operation_type,
            amount=operation.amount
        )
        return wallet

    except ValueError as e:
        logger.warning(f"Business logic error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error during operation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Check logs for details."
        )


@router.get("/{wallet_uuid}")
async def get_wallet_balance(
        wallet_uuid: str,
        db: AsyncSession = Depends(get_db)
):
    wallet = await WalletService.get_wallet(db, wallet_uuid)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"wallet_id": wallet.id, "balance": wallet.balance}