from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from ..database import get_db
from .. import crud, schemas
from ..services.fund_fetcher import FundDataFetcher

router = APIRouter(prefix="/api/nav", tags=["nav"])

# 简单内存缓存（60秒有效期）
_realtime_cache = {}


@router.get("/{fund_code}", response_model=schemas.NavHistoryResponse)
def get_latest_nav(fund_code: str, db: Session = Depends(get_db)):
    """获取基金最新净值"""
    fund = crud.get_fund_by_code(db, fund_code)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金代码 {fund_code} 不存在"
        )

    nav = crud.get_latest_nav(db, fund.id)
    if not nav:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 {fund_code} 没有净值数据"
        )
    return nav


@router.get("/{fund_code}/history", response_model=List[schemas.NavHistoryResponse])
def get_nav_history(
    fund_code: str,
    start_date: date = None,
    end_date: date = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取基金历史净值"""
    fund = crud.get_fund_by_code(db, fund_code)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金代码 {fund_code} 不存在"
        )

    return crud.get_nav_history(db, fund.id, start_date, end_date, limit)


@router.post("/sync-all", response_model=schemas.SyncResponse)
def sync_all_nav(db: Session = Depends(get_db)):
    """同步所有基金最新净值"""
    result = crud.sync_all_funds(db)

    return schemas.SyncResponse(
        success=True,
        message=f"成功同步 {result['updated_count']}/{result['total_count']} 只基金",
        funds_updated=result['updated_count'],
        errors=result['errors']
    )


@router.get("/{fund_code}/realtime", response_model=schemas.RealtimeNavResponse)
async def get_realtime_valuation(
    fund_code: str,
    db: Session = Depends(get_db)
):
    """
    获取基金实时涨跌幅（支持场内和场外基金）

    场内基金（ETF/LOF）：返回实时股价和实际涨跌幅
    场外基金：返回估算涨跌幅

    返回:
    - data_source: 数据源（stock/estimate/nav）
    - is_listed_fund: 是否为场内基金
    - current_price: 实时股价（场内基金）
    - increase_rate: 涨跌幅(%)
    - latest_nav_unit_nav: 最新正式净值
    - estimate_time: 估算时间
    - is_trading_time: 是否是交易时间
    """
    fetcher = FundDataFetcher()
    is_trading = fetcher.is_trading_time()

    # 非交易时间返回最新正式净值
    if not is_trading:
        fund = crud.get_fund_by_code(db, fund_code)
        if not fund:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"基金代码 {fund_code} 不存在"
            )

        latest_nav = crud.get_latest_nav(db, fund.id)
        return schemas.RealtimeNavResponse(
            fund_code=fund_code,
            data_source="nav",
            is_listed_fund=False,
            increase_rate=float(latest_nav.daily_growth * 100) if latest_nav and latest_nav.daily_growth else None,
            estimate_time=None,
            latest_nav_date=latest_nav.date if latest_nav else None,
            latest_nav_unit_nav=float(latest_nav.unit_nav) if latest_nav else None,
            is_trading_time=False
        )

    # 交易时间获取实时涨跌幅
    # 检查缓存（60秒有效期）
    cache_key = f"realtime_{fund_code}"
    if cache_key in _realtime_cache:
        cached_data, cached_time = _realtime_cache[cache_key]
        if (datetime.now() - cached_time).seconds < 60:
            return cached_data

    # 获取基金信息（包含类型）
    fund = crud.get_fund_by_code(db, fund_code)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金代码 {fund_code} 不存在"
        )

    # 获取实时估值（传入基金类型）
    realtime_data = fetcher.get_fund_realtime_valuation(
        fund_code,
        fund_type=fund.fund_type
    )

    if not realtime_data:
        # 如果获取失败，返回最新正式净值的日增长率
        latest_nav = crud.get_latest_nav(db, fund.id)
        return schemas.RealtimeNavResponse(
            fund_code=fund_code,
            data_source="nav",
            is_listed_fund=False,
            increase_rate=float(latest_nav.daily_growth * 100) if latest_nav and latest_nav.daily_growth else None,
            estimate_time=None,
            latest_nav_date=latest_nav.date if latest_nav else None,
            latest_nav_unit_nav=float(latest_nav.unit_nav) if latest_nav else None,
            is_trading_time=True
        )

    # 获取最新正式净值
    latest_nav_unit_nav = None
    latest_nav_date = None

    latest_nav = crud.get_latest_nav(db, fund.id)
    if latest_nav:
        latest_nav_unit_nav = float(latest_nav.unit_nav)
        latest_nav_date = latest_nav.date

    response = schemas.RealtimeNavResponse(
        fund_code=fund_code,
        data_source=realtime_data.get("data_source"),
        is_listed_fund=realtime_data.get("is_listed_fund", False),
        current_price=realtime_data.get("current_price"),
        increase_rate=realtime_data.get("increase_rate"),
        estimate_time=realtime_data.get("estimate_time"),
        latest_nav_date=realtime_data.get("latest_nav_date") or latest_nav_date,
        latest_nav_unit_nav=latest_nav_unit_nav,
        is_trading_time=True
    )

    # 更新缓存
    _realtime_cache[cache_key] = (response, datetime.now())

    return response


@router.post("/realtime/batch", response_model=schemas.BatchRealtimeNavResponse)
async def get_batch_realtime_valuation(
    fund_codes: List[str],
    db: Session = Depends(get_db)
):
    """
    批量获取多只基金实时涨跌幅（支持场内和场外基金）

    用于仪表盘和基金列表页面
    """
    fetcher = FundDataFetcher()
    is_trading = fetcher.is_trading_time()

    valuations = []

    if is_trading:
        # 获取基金信息（包含类型）
        funds = crud.get_funds_by_codes(db, fund_codes)
        fund_types = {f.fund_code: f.fund_type for f in funds}
        fund_id_map = {f.fund_code: f.id for f in funds}

        # 批量获取实时估值（传入类型字典）
        realtime_data_list = fetcher.get_all_funds_realtime_valuation(
            fund_codes,
            fund_types=fund_types
        )

        for realtime_data in realtime_data_list:
            fund_id = fund_id_map.get(realtime_data["fund_code"])
            latest_nav_unit_nav = None
            latest_nav_date = None

            if fund_id:
                latest_nav = crud.get_latest_nav(db, fund_id)
                if latest_nav:
                    latest_nav_unit_nav = float(latest_nav.unit_nav)
                    latest_nav_date = latest_nav.date

            valuations.append(schemas.RealtimeNavItem(
                fund_code=realtime_data["fund_code"],
                data_source=realtime_data.get("data_source"),
                is_listed_fund=realtime_data.get("is_listed_fund", False),
                current_price=realtime_data.get("current_price"),
                increase_rate=realtime_data.get("increase_rate"),
                estimate_time=realtime_data.get("estimate_time"),
                latest_nav_date=realtime_data.get("latest_nav_date") or latest_nav_date,
                latest_nav_unit_nav=latest_nav_unit_nav
            ))
    else:
        # 非交易时间返回最新正式净值的日增长率
        funds = crud.get_funds_by_codes(db, fund_codes)
        for fund in funds:
            latest_nav = crud.get_latest_nav(db, fund.id)
            valuations.append(schemas.RealtimeNavItem(
                fund_code=fund.fund_code,
                data_source="nav",
                is_listed_fund=False,
                increase_rate=float(latest_nav.daily_growth * 100) if latest_nav and latest_nav.daily_growth else None,
                estimate_time=None,
                latest_nav_date=latest_nav.date if latest_nav else None,
                latest_nav_unit_nav=float(latest_nav.unit_nav) if latest_nav else None
            ))

    return schemas.BatchRealtimeNavResponse(
        valuations=valuations,
        update_time=datetime.now(),
        is_trading_time=is_trading
    )
