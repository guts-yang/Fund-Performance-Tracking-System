from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.post("/buy", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def buy_fund(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    """买入基金"""
    # 验证交易类型
    if transaction.transaction_type != "buy":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="交易类型必须是 buy"
        )

    # 验证买入金额
    if not transaction.amount or transaction.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="买入金额必须大于0"
        )

    try:
        result = crud.execute_buy_transaction(db, transaction.fund_id, transaction.amount)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/sell", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def sell_fund(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    """卖出基金"""
    # 验证交易类型
    if transaction.transaction_type != "sell":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="交易类型必须是 sell"
        )

    # 验证卖出参数（金额或份额至少提供一个）
    if not transaction.amount and not transaction.shares:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须提供卖出金额或卖出份额"
        )

    if transaction.amount and transaction.shares:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能提供卖出金额或卖出份额之一"
        )

    try:
        result = crud.execute_sell_transaction(
            db,
            transaction.fund_id,
            transaction.amount,
            transaction.shares
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{fund_id}", response_model=List[schemas.TransactionResponse])
def get_transactions(fund_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取基金交易历史"""
    return crud.get_transactions(db, fund_id, skip=skip, limit=limit)
