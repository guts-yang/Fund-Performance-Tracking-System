from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/api/holdings", tags=["holdings"])


@router.post("/", response_model=schemas.HoldingResponse, status_code=status.HTTP_201_CREATED)
def create_holding(holding: schemas.HoldingCreate, db: Session = Depends(get_db)):
    """添加持仓

    新功能：auto_fetch_nav=True 时自动获取基金最新净值计算份额
    """
    # Check if fund exists
    fund = crud.get_fund(db, holding.fund_id)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {holding.fund_id} 不存在"
        )

    # 自动获取净值模式
    if holding.auto_fetch_nav:
        if not holding.amount or holding.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必须提供持有金额"
            )

        from ..services.fund_fetcher import FundDataFetcher
        fetcher = FundDataFetcher()
        nav_data = fetcher.get_fund_nav(fund.fund_code)

        if nav_data and nav_data.get("unit_nav"):
            latest_nav = nav_data["unit_nav"]
            holding.shares = (holding.amount / latest_nav).quantize(Decimal("0.0001"))
            holding.cost_price = latest_nav
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取净值失败，请稍后重试"
            )
    else:
        # 灵活计算逻辑：输入任意两个字段，自动计算第三个
        # 统计已提供的字段数量（None 和 0 不算）
        provided_fields = 0
        if holding.amount and holding.amount > 0:
            provided_fields += 1
        if holding.shares and holding.shares > 0:
            provided_fields += 1
        if holding.cost_price and holding.cost_price > 0:
            provided_fields += 1

        # 根据提供的字段进行计算
        if provided_fields >= 2:
            # 输入金额和成本价，计算份额
            if holding.amount and holding.cost_price and not holding.shares:
                holding.shares = holding.amount / holding.cost_price
            # 输入金额和份额，计算成本价
            elif holding.amount and holding.shares and not holding.cost_price:
                holding.cost_price = holding.amount / holding.shares
            # 输入份额和成本价，计算金额
            elif holding.shares and holding.cost_price and not holding.amount:
                holding.amount = holding.shares * holding.cost_price
        elif provided_fields == 0 or provided_fields == 1:
            # 如果只提供了1个或没有提供字段，使用默认值
            if not holding.shares:
                holding.shares = Decimal("0")
            if not holding.cost_price:
                holding.cost_price = Decimal("0")

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
    """修改持仓

    新功能：auto_fetch_nav=True 时自动获取基金最新净值计算份额
    """
    # Check if fund exists
    fund = crud.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 不存在"
        )

    # 自动获取净值模式
    if holding.auto_fetch_nav:
        if not holding.amount or holding.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必须提供持有金额"
            )

        from ..services.fund_fetcher import FundDataFetcher
        fetcher = FundDataFetcher()
        nav_data = fetcher.get_fund_nav(fund.fund_code)

        if nav_data and nav_data.get("unit_nav"):
            latest_nav = nav_data["unit_nav"]
            holding.shares = (holding.amount / latest_nav).quantize(Decimal("0.0001"))
            holding.cost_price = latest_nav
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取净值失败，请稍后重试"
            )
    else:
        # 灵活计算逻辑：输入任意两个字段，自动计算第三个
        # 统计已提供的字段数量（None 和 0 不算）
        provided_fields = 0
        if holding.amount and holding.amount > 0:
            provided_fields += 1
        if holding.shares and holding.shares > 0:
            provided_fields += 1
        if holding.cost_price and holding.cost_price > 0:
            provided_fields += 1

        # 根据提供的字段进行计算
        if provided_fields >= 2:
            # 输入金额和成本价，计算份额
            if holding.amount and holding.cost_price and not holding.shares:
                holding.shares = holding.amount / holding.cost_price
            # 输入金额和份额，计算成本价
            elif holding.amount and holding.shares and not holding.cost_price:
                holding.cost_price = holding.amount / holding.shares
            # 输入份额和成本价，计算金额
            elif holding.shares and holding.cost_price and not holding.amount:
                holding.amount = holding.shares * holding.cost_price

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
