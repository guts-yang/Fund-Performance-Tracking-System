from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
import logging
import efinance as ef

from ..database import get_db
from .. import crud, schemas
from ..services.fund_fetcher import FundDataFetcher

logger = logging.getLogger(__name__)

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


@router.get("/{fund_code}/realtime-stock", response_model=schemas.StockRealtimeNavResponse)
async def get_fund_realtime_nav_by_stocks(
    fund_code: str,
    db: Session = Depends(get_db)
):
    """
    基于股票持仓计算基金实时估值

    使用 Tushare 新浪财经源获取股票实时行情，
    根据基金持仓占比加权平均计算实时估值和涨跌幅

    计算逻辑：
    1. 获取基金的股票持仓数据
    2. 获取所有持仓股票的实时涨跌幅
    3. 按持仓占比加权平均
    4. 实时估值 = 最新净值 × (1 + 加权涨跌幅)

    Args:
        fund_code: 基金代码

    Returns:
        实时估值数据，包含实时净值、涨跌幅等
    """
    from ..services.tushare_service import tushare_service

    fund = crud.get_fund_by_code(db, fund_code)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金代码 {fund_code} 不存在"
        )

    # 获取最新正式净值
    latest_nav_record = crud.get_latest_nav(db, fund.id)
    if not latest_nav_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 {fund_code} 没有净值数据"
        )

    latest_nav = float(latest_nav_record.unit_nav)

    # 获取股票持仓
    stock_positions = crud.get_fund_stock_positions(db, fund.id)

    if not stock_positions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 {fund_code} 没有股票持仓数据，请先同步持仓"
        )

    # 转换为字典列表
    positions_data = [
        {
            'stock_code': pos.stock_code,
            'weight': float(pos.weight) if pos.weight else 0
        }
        for pos in stock_positions
    ]

    # 计算实时估值
    result = tushare_service.calculate_fund_realtime_nav(
        fund_code,
        positions_data,
        latest_nav
    )

    if not result:
        logger.warning(f"[实时估值] 基金 {fund_code} 无法获取股票实时行情，可能原因：非交易时间/网络问题/API不可用")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,  # v1.7.2: 改为 503 表示服务暂时不可用
            detail="无法获取股票实时行情。请确认：1) 是否为交易时间（工作日 9:30-15:00）；2) 网络连接正常。非交易时间请使用正式净值数据。"
        )

    return schemas.StockRealtimeNavResponse(**result)


@router.post("/realtime/batch-stock", response_model=schemas.BatchRealtimeNavResponse)
async def get_batch_realtime_valuation_by_stocks(
    fund_codes: List[str],
    db: Session = Depends(get_db)
):
    """
    批量获取多只基金实时估值（基于股票持仓计算）

    使用 Tushare 新浪财经源获取股票实时行情，
    根据基金持仓占比加权平均计算实时估值

    优先级：
    1. 场内基金（ETF/LOF）：使用实时股价
    2. 有股票持仓的基金：使用股票持仓估值
    3. 降级方案：使用最新正式净值的日增长率

    Args:
        fund_codes: 基金代码列表

    Returns:
        批量实时估值数据
    """
    from ..services.tushare_service import tushare_service

    fetcher = FundDataFetcher()
    is_trading = fetcher.is_trading_time()

    valuations = []

    # 获取基金信息
    funds = crud.get_funds_by_codes(db, fund_codes)
    fund_id_map = {f.fund_code: f.id for f in funds}
    fund_types = {f.fund_code: f.fund_type for f in funds}

    if is_trading:
        # ========== 交易时间处理 ==========

        # 1. 分离场内和场外基金
        listed_funds = []
        offshore_funds = []

        for fund_code in fund_codes:
            fund_type = fund_types.get(fund_code)
            if FundDataFetcher.is_listed_fund(fund_type):
                listed_funds.append(fund_code)
            else:
                offshore_funds.append(fund_code)

        # 2. 处理场内基金（实时股价）
        if listed_funds:
            try:
                etf_data = ef.stock.get_realtime_quotes('ETF')
                lof_data = ef.stock.get_realtime_quotes('LOF')

                # 合并数据
                listed_data = None
                if etf_data is not None and not etf_data.empty:
                    if lof_data is not None and not lof_data.empty:
                        import pandas as pd
                        listed_data = pd.concat([etf_data, lof_data], ignore_index=True)
                    else:
                        listed_data = etf_data
                elif lof_data is not None and not lof_data.empty:
                    listed_data = lof_data

                if listed_data is not None:
                    for code in listed_funds:
                        fund_row = listed_data[listed_data['股票代码'] == code]
                        if not fund_row.empty:
                            row = fund_row.iloc[0]
                            fund_id = fund_id_map.get(code)
                            latest_nav = crud.get_latest_nav(db, fund_id) if fund_id else None
                            valuations.append(schemas.RealtimeNavItem(
                                fund_code=code,
                                data_source="stock",
                                is_listed_fund=True,
                                current_price=float(row['最新价']),
                                increase_rate=float(row['涨跌幅']),
                                estimate_time=datetime.now(),
                                latest_nav_date=latest_nav.date if latest_nav else None,
                                latest_nav_unit_nav=float(latest_nav.unit_nav) if latest_nav else None
                            ))
                        else:
                            # 场内基金未找到，降级到场外处理
                            offshore_funds.append(code)
            except Exception as e:
                logger.error(f"获取场内基金实时股价失败: {e}")
                offshore_funds.extend(listed_funds)

        # 3. 处理场外基金（基于股票持仓）
        for fund_code in offshore_funds:
            fund_id = fund_id_map.get(fund_code)
            if not fund_id:
                continue

            latest_nav = crud.get_latest_nav(db, fund_id)
            if not latest_nav:
                # 没有净值数据，跳过
                continue

            latest_nav_value = float(latest_nav.unit_nav)

            # 获取股票持仓
            stock_positions = crud.get_fund_stock_positions(db, fund_id)

            if stock_positions:
                # 有持仓数据，使用股票持仓估值
                positions_data = [
                    {
                        'stock_code': pos.stock_code,
                        'weight': float(pos.weight) if pos.weight else 0
                    }
                    for pos in stock_positions
                ]

                result = tushare_service.calculate_fund_realtime_nav(
                    fund_code,
                    positions_data,
                    latest_nav_value
                )

                if result:
                    valuations.append(schemas.RealtimeNavItem(
                        fund_code=fund_code,
                        data_source="tushare_sina",
                        is_listed_fund=False,
                        current_price=None,
                        increase_rate=result.get('increase_rate'),
                        estimate_time=result.get('update_time'),
                        latest_nav_date=latest_nav.date,
                        latest_nav_unit_nav=latest_nav_value
                    ))
                else:
                    # 股票持仓估值失败，使用efinance降级
                    await _append_efinance_fallback(fund_code, fund_id, valuations, db)
            else:
                # 没有持仓数据，使用efinance降级
                await _append_efinance_fallback(fund_code, fund_id, valuations, db)
    else:
        # ========== 非交易时间处理 ==========
        # 返回最新正式净值的日增长率
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


async def _append_efinance_fallback(fund_code: str, fund_id: int, valuations: List, db: Session):
    """efinance 降级方案"""
    latest_nav = crud.get_latest_nav(db, fund_id)

    try:
        realtime_data = FundDataFetcher.get_fund_realtime_valuation(fund_code)

        if realtime_data and realtime_data.get("increase_rate") is not None:
            valuations.append(schemas.RealtimeNavItem(
                fund_code=fund_code,
                data_source=realtime_data.get("data_source", "estimate"),
                is_listed_fund=False,
                current_price=realtime_data.get("current_price"),
                increase_rate=realtime_data.get("increase_rate"),
                estimate_time=realtime_data.get("estimate_time"),
                latest_nav_date=realtime_data.get("latest_nav_date") or (latest_nav.date if latest_nav else None),
                latest_nav_unit_nav=float(latest_nav.unit_nav) if latest_nav else None
            ))
        else:
            # efinance也失败，使用正式净值
            valuations.append(schemas.RealtimeNavItem(
                fund_code=fund_code,
                data_source="nav",
                is_listed_fund=False,
                increase_rate=float(latest_nav.daily_growth * 100) if latest_nav and latest_nav.daily_growth else None,
                estimate_time=None,
                latest_nav_date=latest_nav.date if latest_nav else None,
                latest_nav_unit_nav=float(latest_nav.unit_nav) if latest_nav else None
            ))
    except Exception as e:
        logger.error(f"efinance 降级失败 {fund_code}: {e}")
        # 最终降级：使用正式净值
        valuations.append(schemas.RealtimeNavItem(
            fund_code=fund_code,
            data_source="nav",
            is_listed_fund=False,
            increase_rate=float(latest_nav.daily_growth * 100) if latest_nav and latest_nav.daily_growth else None,
            estimate_time=None,
            latest_nav_date=latest_nav.date if latest_nav else None,
            latest_nav_unit_nav=float(latest_nav.unit_nav) if latest_nav else None
        ))
