from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/api/pnl", tags=["pnl"])


@router.get("/summary", response_model=schemas.PortfolioSummary)
def get_portfolio_summary(db: Session = Depends(get_db)):
    """获取投资组合汇总（包含累计总收益）"""

    # 获取实时计算的投资组合汇总
    summary = crud.get_portfolio_summary(db)

    # 获取累计总收益（每日收益叠加）
    cumulative = crud.get_portfolio_cumulative_profit(db)

    # 合并返回结果
    return {
        **summary,
        "cumulative_profit": cumulative["cumulative_profit"],
        "daily_profits_history": cumulative["daily_profits"]
    }


@router.get("/daily/{fund_id}", response_model=List[schemas.DailyPnLResponse])
def get_daily_pnl(fund_id: int, limit: int = 30, db: Session = Depends(get_db)):
    """获取基金每日收益"""
    # Check if fund exists
    fund = crud.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 不存在"
        )

    return crud.get_daily_pnl_history(db, fund_id, limit)


@router.get("/chart/{fund_id}")
def get_pnl_chart_data(fund_id: int, limit: int = 30, db: Session = Depends(get_db)):
    """获取收益图表数据"""
    # Check if fund exists
    fund = crud.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 不存在"
        )

    pnl_history = crud.get_daily_pnl_history(db, fund_id, limit)

    # Format for chart
    dates = [pnl.date.strftime("%Y-%m-%d") for pnl in pnl_history]
    profits = [float(pnl.profit) for pnl in pnl_history]
    profit_rates = [float(pnl.profit_rate) for pnl in pnl_history]
    market_values = [float(pnl.market_value) for pnl in pnl_history]

    return {
        "fund_id": fund_id,
        "fund_code": fund.fund_code,
        "fund_name": fund.fund_name,
        "dates": dates,
        "profits": profits,
        "profit_rates": profit_rates,
        "market_values": market_values
    }
