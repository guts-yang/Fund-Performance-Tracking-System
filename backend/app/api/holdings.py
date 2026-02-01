from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/api/holdings", tags=["holdings"])


@router.post("/", response_model=schemas.HoldingResponse, status_code=status.HTTP_201_CREATED)
def create_holding(holding: schemas.HoldingCreate, db: Session = Depends(get_db)):
    """添加持仓"""
    # Check if fund exists
    fund = crud.get_fund(db, holding.fund_id)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {holding.fund_id} 不存在"
        )

    # If shares not provided, calculate from amount and cost_price
    if holding.shares is None and holding.cost_price and holding.cost_price > 0:
        holding.shares = holding.amount / holding.cost_price
    elif holding.shares is None:
        holding.shares = Decimal("0")

    return crud.create_or_update_holding(db=db, holding=holding)


@router.get("/", response_model=List[schemas.HoldingResponse])
def get_holdings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有持仓"""
    return crud.get_holdings(db, skip=skip, limit=limit)


@router.get("/{fund_id}", response_model=schemas.HoldingResponse)
def get_holding(fund_id: int, db: Session = Depends(get_db)):
    """获取特定基金持仓"""
    holding = crud.get_holding(db, fund_id)
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 的持仓不存在"
        )
    return holding


@router.put("/{fund_id}", response_model=schemas.HoldingResponse)
def update_holding(fund_id: int, holding: schemas.HoldingUpdate, db: Session = Depends(get_db)):
    """修改持仓金额"""
    # Check if fund exists
    fund = crud.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 不存在"
        )

    # If shares not provided, calculate from amount and cost_price
    if holding.shares is None and holding.cost_price and holding.cost_price > 0:
        holding.shares = holding.amount / holding.cost_price
    elif holding.shares is None:
        holding.shares = Decimal("0")

    updated_holding = crud.update_holding(db, fund_id, holding)
    if not updated_holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 的持仓不存在"
        )
    return updated_holding


@router.delete("/{fund_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(fund_id: int, db: Session = Depends(get_db)):
    """删除持仓"""
    success = crud.delete_holding(db, fund_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 的持仓不存在"
        )
    return None
