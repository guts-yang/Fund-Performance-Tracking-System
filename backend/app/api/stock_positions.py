"""
基金股票持仓 API

提供基金股票持仓的查询和同步功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import logging
import pandas as pd
import json

from ..database import get_db
from .. import crud, schemas, models
from ..services.tushare_service import tushare_service
from ..utils.redis_client import redis_client
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stock-positions", tags=["stock-positions"])


@router.get("/funds/{fund_id}", response_model=List[schemas.FundStockPositionResponse])
def get_fund_stock_positions(
    fund_id: int,
    report_date: Optional[str] = None,
    update_names: bool = False,  # 新增参数：是否同时更新数据库
    db: Session = Depends(get_db)
):
    """
    获取基金股票持仓列表

    自动检查并修复股票名称：
    - 如果名称为空，从 Tushare 查询补充
    - 如果名称是乱码，尝试修复 GBK 编码问题
    - 使用内存缓存优化性能

    Args:
        fund_id: 基金 ID
        report_date: 报告期（可选），格式 YYYY-MM-DD
        update_names: 是否同时更新数据库中的名称（默认 False）

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

    # Redis缓存检查
    report_date_str = report_date_obj.isoformat() if report_date_obj else 'latest'
    cache_key = f"fund:positions:{fund_id}:{report_date_str}"
    ttl = settings.FUND_POSITIONS_CACHE_TTL_WITH_DATE if report_date_obj else settings.FUND_POSITIONS_CACHE_TTL_LATEST

    # 尝试从Redis获取
    if redis_client.is_available() and not update_names:
        cached_value = redis_client.get(cache_key)
        if cached_value:
            if cached_value == "NULL":
                logger.debug(f"[持仓缓存] 空值命中: fund_id={fund_id}")
                return []
            try:
                logger.debug(f"[持仓缓存] 命中: fund_id={fund_id}")
                positions_data = json.loads(cached_value)
                return [schemas.FundStockPositionResponse(**pos) for pos in positions_data]
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"[持仓缓存] 反序列化失败: fund_id={fund_id}, {e}")

    logger.info(f"[持仓缓存] 未命中: fund_id={fund_id}，查询数据库")

    # 获取持仓数据
    positions = crud.get_fund_stock_positions(db, fund_id, report_date_obj)

    # 转换为字典列表（便于 ensure_stock_names 处理）
    positions_dict = [
        {
            'id': p.id,
            'fund_id': fund_id,
            'stock_code': p.stock_code,
            'stock_name': p.stock_name,
            'shares': p.shares,
            'market_value': p.market_value,
            'weight': p.weight,
            'cost_price': p.cost_price,
            'report_date': p.report_date,
            'created_at': p.created_at,
            'updated_at': p.updated_at,
        }
        for p in positions
    ]

    # ✅ 新增：检查并修复股票名称
    if positions_dict:
        logger.info(f"[名称修复] 基金 {fund.fund_code}: 检查 {len(positions_dict)} 条持仓记录")
        fixed_positions = tushare_service.ensure_stock_names(positions_dict)

        # 可选：更新数据库
        if update_names:
            logger.info("[名称修复] 同时更新数据库")
            for fixed_pos in fixed_positions:
                db_position = db.query(models.FundStockPosition).filter(
                    models.FundStockPosition.id == fixed_pos['id']
                ).first()

                if db_position and db_position.stock_name != fixed_pos['stock_name']:
                    old_name = db_position.stock_name
                    db_position.stock_name = fixed_pos['stock_name']
                    logger.info(
                        f"[名称修复] 更新数据库: {db_position.stock_code} "
                        f"'{old_name}' → '{fixed_pos['stock_name']}'"
                    )

            db.commit()
            # 重新从数据库获取（包含更新的名称）
            positions = crud.get_fund_stock_positions(db, fund_id, report_date_obj)
        else:
            # 直接返回修复后的数据（不更新数据库）
            # 使用 schemas.FundStockPositionResponse 确保类型匹配
            positions = []
            for p in fixed_positions:
                positions.append(schemas.FundStockPositionResponse(
                    id=p['id'],
                    fund_id=p['fund_id'],
                    stock_code=p['stock_code'],
                    stock_name=p['stock_name'],
                    shares=p['shares'],
                    market_value=p['market_value'],
                    weight=p['weight'],
                    cost_price=p['cost_price'],
                    report_date=p['report_date'],
                    created_at=p['created_at'],
                    updated_at=p['updated_at']
                ))

    # 更新Redis缓存
    if redis_client.is_available() and positions:
        cache_value = json.dumps([
            {
                'id': p.id,
                'fund_id': p.fund_id,
                'stock_code': p.stock_code,
                'stock_name': p.stock_name,
                'shares': p.shares,
                'market_value': p.market_value,
                'weight': p.weight,
                'cost_price': p.cost_price,
                'report_date': p.report_date.isoformat() if p.report_date else None,
                'created_at': p.created_at.isoformat() if p.created_at else None,
                'updated_at': p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in positions
        ], ensure_ascii=False)

        redis_client.set(cache_key, cache_value, ttl=ttl)
        logger.debug(f"[持仓缓存] 已缓存: fund_id={fund_id}, {len(positions)} 条记录")
    elif redis_client.is_available() and not positions:
        redis_client.set(cache_key, "NULL", ttl=settings.FUND_POSITIONS_NULL_CACHE_TTL)

    return positions


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
        # 使用 Tushare API 获取持仓数据
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

        # v1.7.3: 批量查询股票名称（Tushare fund_portfolio API 不返回 name 字段）
        # 第一遍遍历：收集有效的股票代码
        stock_codes_list = []
        for idx, row in df.iterrows():
            stock_code = row.get('symbol', '')
            if not stock_code:
                continue
            if stock_code.endswith('.OF'):
                logger.error(f"[持仓同步] 错误：检测到基金代码 {stock_code}，应为股票代码，跳过该记录")
                continue
            if not stock_code.endswith(('.SH', '.SZ', '.BJ', '.HK')):
                continue
            stock_codes_list.append(stock_code)

        # 批量查询股票名称
        stock_name_mapping = {}
        if stock_codes_list:
            logger.info(f"[持仓同步] 正在批量查询 {len(stock_codes_list)} 只股票的名称")
            stock_name_mapping = tushare_service.get_stock_names_batch(stock_codes_list)
            logger.info(f"[持仓同步] 成功获取 {len([n for n in stock_name_mapping.values() if n])}/{len(stock_codes_list)} 只股票的名称")

        # 转换为持仓记录
        positions = []
        for idx, row in df.iterrows():
            # v1.7.1 修正：Tushare API 字段含义
            # ts_code = 基金代码（如 023754.OF）
            # symbol = 股票代码（如 688258.SH）
            # name = 股票名称（如 中芯国际）
            stock_code = row.get('symbol', '')  # ✅ v1.7.1: 使用 symbol 获取股票代码

            # 跳过空记录
            if not stock_code:
                logger.warning(f"[持仓同步] 第 {idx} 行股票代码为空，跳过")
                continue

            # v1.7.1: 添加字段验证，防止基金代码被误认为股票代码
            if stock_code.endswith('.OF'):
                logger.error(f"[持仓同步] 错误：检测到基金代码 {stock_code}，应为股票代码，跳过该记录")
                continue

            # 验证股票代码格式
            if not stock_code.endswith(('.SH', '.SZ', '.BJ', '.HK')):
                logger.warning(f"[持仓同步] 无效的股票代码格式: {stock_code}，跳过")
                continue

            # v1.7.3: 使用映射获取股票名称（Tushare fund_portfolio API 不返回 name 字段）
            stock_name = stock_name_mapping.get(stock_code, '')
            if not stock_name:
                logger.warning(f"[持仓同步] 股票 {stock_code} 名称查询失败，使用空字符串")

            logger.debug(f"[持仓同步] 处理股票 {stock_code} ({stock_name}): amount={row.get('amount')}, mkv={row.get('mkv')}, stk_mkv_ratio={row.get('stk_mkv_ratio')}")

            # 解析报告期日期（字符串 '20251231' → date 对象）
            report_date_str = row.get('end_date')
            report_date = None
            if pd.notna(report_date_str) and report_date_str:
                try:
                    report_date = datetime.strptime(str(report_date_str), '%Y%m%d').date()
                except ValueError:
                    logger.warning(f"[持仓同步] 无法解析日期 {report_date_str}")

            # Tushare 返回的 stk_mkv_ratio 是百分比形式（如 4.82），需要除以 100 转为小数
            weight_raw = row.get('stk_mkv_ratio')
            weight = None
            if pd.notna(weight_raw) and weight_raw:
                weight = float(weight_raw) / 100.0

            position = schemas.FundStockPositionCreate(
                stock_code=stock_code,  # ✅ v1.7.1: 股票代码（如 688258.SH）
                stock_name=stock_name,  # ✅ v1.7.1: 股票名称（如 中芯国际）
                shares=float(row.get('amount', 0)) if pd.notna(row.get('amount')) else None,  # 修正：使用 amount 字段
                market_value=float(row.get('mkv', 0)) if pd.notna(row.get('mkv')) else None,  # 修正：使用 mkv 字段
                weight=weight,  # 修正：百分比转小数
                cost_price=None,  # Tushare 不提供成本价格
                report_date=report_date  # 修正：字符串转 date 对象
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

        # 同步成功后，失效相关缓存
        _invalidate_positions_cache(fund_id)

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


@router.get("/funds/{fund_id}/quality")
def check_positions_quality(fund_id: int, db: Session = Depends(get_db)):
    """
    检查持仓数据质量

    Returns:
        {
            "total": 52,                    # 总记录数
            "with_name": 52,                # 有股票名称的记录数
            "with_weight": 52,              # 有权重数据的记录数
            "name_issues": 0,               # 名称问题记录数（乱码）
            "report_date": "2024-12-31",    # 最新报告期
            "last_update": "2025-01-15"     # 最后更新时间
        }
    """
    from ..utils.encoding import validate_chinese_name

    positions = crud.get_fund_stock_positions(db, fund_id)

    total = len(positions)
    with_name = sum(1 for p in positions if p.stock_name)
    with_weight = sum(1 for p in positions if p.weight)
    name_issues = sum(1 for p in positions if p.stock_name and not validate_chinese_name(p.stock_name))

    # 获取最新报告期
    report_dates = [p.report_date for p in positions if p.report_date]
    latest_report = max(report_dates).isoformat() if report_dates else None

    # 获取最后更新时间
    last_update = max((p.updated_at for p in positions), default=None)

    return {
        "total": total,
        "with_name": with_name,
        "with_weight": with_weight,
        "name_issues": name_issues,
        "report_date": latest_report,
        "last_update": last_update.isoformat() if last_update else None
    }


@router.post("/admin/fix-names", response_model=schemas.SyncResponse)
async def fix_all_stock_names(
    fund_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    管理员功能：批量修复股票名称

    扫描数据库中的所有持仓记录，修复缺失或乱码的股票名称。
    可选择修复特定基金或所有基金。

    Args:
        fund_id: 基金 ID（可选），不指定则修复所有基金

    Returns:
        修复结果统计
    """
    try:
        # 构建查询
        query = db.query(models.FundStockPosition)
        if fund_id:
            query = query.filter(models.FundStockPosition.fund_id == fund_id)

        positions = query.all()
        total_count = len(positions)

        logger.info(f"[批量修复] 开始处理 {total_count} 条持仓记录")

        # 转换为字典列表
        positions_dict = [
            {
                'id': p.id,
                'stock_code': p.stock_code,
                'stock_name': p.stock_name or '',
            }
            for p in positions
        ]

        # 批量修复名称
        fixed_positions = tushare_service.ensure_stock_names(positions_dict)

        # 统计修复数量
        updated_count = 0
        for fixed_pos in fixed_positions:
            db_position = db.query(models.FundStockPosition).filter(
                models.FundStockPosition.id == fixed_pos['id']
            ).first()

            if db_position and db_position.stock_name != fixed_pos['stock_name']:
                old_name = db_position.stock_name
                db_position.stock_name = fixed_pos['stock_name']
                updated_count += 1

                logger.info(
                    f"[批量修复] {db_position.stock_code}: "
                    f"'{old_name}' → '{fixed_pos['stock_name']}'"
                )

        # 提交更改
        db.commit()

        logger.info(f"[批量修复] 完成: 共 {total_count} 条，更新 {updated_count} 条")

        return schemas.SyncResponse(
            success=True,
            message=f"成功修复 {updated_count}/{total_count} 条股票名称",
            funds_updated=updated_count,
            errors=[]
        )

    except Exception as e:
        logger.error(f"[批量修复] 失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return schemas.SyncResponse(
            success=False,
            message=f"批量修复失败: {str(e)}",
            funds_updated=0,
            errors=[str(e)]
        )


def _invalidate_positions_cache(fund_id: int, report_date: Optional[date] = None):
    """失效持仓缓存"""
    from ..utils.redis_client import redis_client

    if not redis_client.is_available():
        return

    report_date_str = report_date.isoformat() if report_date else 'latest'
    cache_key = f"fund:positions:{fund_id}:{report_date_str}"
    deleted = redis_client.delete(cache_key)

    if deleted:
        logger.info(f"[持仓缓存] 已失效缓存: {cache_key}")
