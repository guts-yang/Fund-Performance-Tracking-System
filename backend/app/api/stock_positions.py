"""
基金股票持仓 API

提供基金股票持仓的查询和同步功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import logging
import pandas as pd

from ..database import get_db
from .. import crud, schemas
from ..services.tushare_service import tushare_service

logger = logging.getLogger(__name__)

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
        logger.info(f"[持仓同步] 正在同步基金 {fund.fund_code} 的持仓数据")
        df = tushare_service.get_fund_portfolio(fund.fund_code)

        if df.empty:
            logger.warning(f"[持仓同步] 基金 {fund.fund_code} Tushare 返回空数据")
            return schemas.SyncResponse(
                success=False,
                message=f"无法获取基金 {fund.fund_code} 的持仓数据，可能该基金没有股票持仓披露",
                funds_updated=0,
                errors=["Tushare API 返回空数据"]
            )

        logger.info(f"[持仓同步] Tushare 返回 {len(df)} 条持仓记录")
        logger.debug(f"[持仓同步] 返回字段: {df.columns.tolist()}")

        # 转换为持仓记录
        positions = []
        for idx, row in df.iterrows():
            # 处理 Tushare 返回的数据字段
            stock_code = row.get('ts_code', '')

            # 跳过空记录
            if not stock_code:
                logger.warning(f"[持仓同步] 第 {idx} 行股票代码为空，跳过")
                continue

            logger.debug(f"[持仓同步] 处理股票 {stock_code}: symbol={row.get('symbol')}, amount={row.get('amount')}, mkv={row.get('mkv')}, stk_mkv_ratio={row.get('stk_mkv_ratio')}")

            position = schemas.FundStockPositionCreate(
                stock_code=stock_code,
                stock_name=row.get('symbol', ''),  # 修正：使用 symbol 字段
                shares=float(row.get('amount', 0)) if pd.notna(row.get('amount')) else None,  # 修正：使用 amount 字段
                market_value=float(row.get('mkv', 0)) if pd.notna(row.get('mkv')) else None,  # 修正：使用 mkv 字段
                weight=float(row.get('stk_mkv_ratio', 0)) if pd.notna(row.get('stk_mkv_ratio')) else None,  # 修正：使用 stk_mkv_ratio 字段
                cost_price=None,  # Tushare 不提供成本价格
                report_date=row.get('end_date')
            )
            positions.append(position)

        logger.info(f"[持仓同步] 成功解析 {len(positions)} 条持仓记录")

        if not positions:
            logger.error(f"[持仓同步] 所有持仓记录解析失败")
            return schemas.SyncResponse(
                success=False,
                message=f"Tushare 返回的数据无效",
                funds_updated=0,
                errors=["无法解析持仓数据"]
            )

        # 更新数据库
        count = crud.update_fund_stock_positions(db, fund_id, positions)
        logger.info(f"[持仓同步] 成功保存 {count} 条持仓记录到数据库")

        return schemas.SyncResponse(
            success=True,
            message=f"成功同步 {count} 条持仓记录",
            funds_updated=count,
            errors=[]
        )

    except Exception as e:
        logger.error(f"[持仓同步] 同步失败: {str(e)}", exc_info=True)
        return schemas.SyncResponse(
            success=False,
            message=f"同步失败: {str(e)}",
            funds_updated=0,
            errors=[str(e)]
        )
