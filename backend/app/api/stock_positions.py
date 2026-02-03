"""
基金股票持仓 API

提供基金股票持仓的查询和同步功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from .. import crud, schemas
from ..services.tushare_service import tushare_service

router = APIRouter(prefix="/api/stock-positions", tags=["stock-positions"])


@router.get("/funds/{fund_id}", response_model=List[schemas.FundStockPositionResponse])
def get_fund_stock_positions(
    fund_id: int,
    report_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取基金股票持仓列表

    Args:
        fund_id: 基金 ID
        report_date: 报告期（可选），格式 YYYY-MM-DD

    Returns:
        股票持仓列表，按持仓占比降序排列
    """
    fund = crud.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 不存在"
        )

    # 转换日期格式
    report_date_obj = None
    if report_date:
        try:
            report_date_obj = date.fromisoformat(report_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="报告期格式错误，应为 YYYY-MM-DD"
            )

    return crud.get_fund_stock_positions(db, fund_id, report_date_obj)


@router.post("/funds/{fund_id}/sync", response_model=schemas.SyncResponse)
async def sync_fund_stock_positions(
    fund_id: int,
    db: Session = Depends(get_db)
):
    """
    从 Tushare Pro 同步基金股票持仓

    从 Tushare Pro 获取基金最新的股票持仓数据，并更新到数据库

    Args:
        fund_id: 基金 ID

    Returns:
        同步结果，包含成功数量和错误信息
    """
    fund = crud.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 不存在"
        )

    try:
        # 从 Tushare 获取持仓数据
        df = tushare_service.get_fund_portfolio(fund.fund_code)

        if df.empty:
            return schemas.SyncResponse(
                success=False,
                message=f"无法获取基金 {fund.fund_code} 的持仓数据，可能该基金没有股票持仓披露",
                funds_updated=0,
                errors=["Tushare API 返回空数据"]
            )

        # 转换为持仓记录
        positions = []
        for _, row in df.iterrows():
            # 处理 Tushare 返回的数据字段
            stock_code = row.get('ts_code', '')

            # 跳过空记录
            if not stock_code:
                continue

            position = schemas.FundStockPositionCreate(
                stock_code=stock_code,
                stock_name=row.get('stk_name', ''),
                shares=float(row.get('stk_share', 0)) if row.get('stk_share') else None,
                market_value=float(row.get('market_value', 0)) if row.get('market_value') else None,
                weight=float(row.get('stk_share_ratio', 0)) if row.get('stk_share_ratio') else None,
                cost_price=float(row.get('stk_price', 0)) if row.get('stk_price') else None,
                report_date=row.get('end_date')
            )
            positions.append(position)

        if not positions:
            return schemas.SyncResponse(
                success=False,
                message=f"Tushare 返回的数据无效",
                funds_updated=0,
                errors=["无法解析持仓数据"]
            )

        # 更新数据库
        count = crud.update_fund_stock_positions(db, fund_id, positions)

        return schemas.SyncResponse(
            success=True,
            message=f"成功同步 {count} 条持仓记录",
            funds_updated=count,
            errors=[]
        )

    except Exception as e:
        return schemas.SyncResponse(
            success=False,
            message=f"同步失败: {str(e)}",
            funds_updated=0,
            errors=[str(e)]
        )
