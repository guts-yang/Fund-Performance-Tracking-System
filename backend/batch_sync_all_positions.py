"""
批量同步所有基金的股票持仓

使用 Tushare API 获取所有基金的最新持仓数据
"""
import sys
import os

# 确保可以导入 app 模块
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import Fund
from app.services.tushare_service import tushare_service
from app import crud, schemas
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sync_all_fund_positions():
    """批量同步所有基金的股票持仓"""
    db = SessionLocal()

    try:
        # 获取所有基金
        funds = db.query(Fund).all()
        total_funds = len(funds)

        logger.info(f"=" * 60)
        logger.info(f"开始批量同步 {total_funds} 只基金的股票持仓")
        logger.info(f"=" * 60)

        # 统计结果
        success_count = 0
        skip_count = 0
        error_count = 0
        total_positions = 0
        total_weight_filled = 0  # v1.7.3: 统计权重数据完整性

        # 遍历所有基金
        for idx, fund in enumerate(funds, 1):
            fund_code = fund.fund_code
            fund_name = fund.fund_name

            logger.info(f"\n[{idx}/{total_funds}] 正在同步: {fund_code} - {fund_name}")

            try:
                # 调用 Tushare API 获取持仓
                df = tushare_service.get_fund_portfolio(fund_code)

                if df.empty:
                    logger.warning(f"  [跳过] {fund_code} 没有持仓数据")
                    skip_count += 1
                    continue

                # v1.7.3: 批量查询股票名称（Tushare fund_portfolio API 不返回 name 字段）
                # 第一遍遍历：收集有效的股票代码
                stock_codes_list = []
                for _, row in df.iterrows():
                    stock_code = row.get('symbol', '')
                    if not stock_code:
                        continue
                    if not stock_code.endswith(('.SH', '.SZ', '.BJ', '.HK')):
                        continue
                    stock_codes_list.append(stock_code)

                # 批量查询股票名称
                stock_name_mapping = {}
                if stock_codes_list:
                    stock_name_mapping = tushare_service.get_stock_names_batch(stock_codes_list)
                    found_names = len([n for n in stock_name_mapping.values() if n])
                    logger.info(f"  [股票名称] 查询到 {found_names}/{len(stock_codes_list)} 只股票名称")

                # 解析持仓数据
                positions = []
                for _, row in df.iterrows():
                    stock_code = row.get('symbol', '')

                    # 跳过空记录
                    if not stock_code:
                        continue

                    # 验证股票代码格式
                    if not stock_code.endswith(('.SH', '.SZ', '.BJ', '.HK')):
                        continue

                    # v1.7.3: 使用映射获取股票名称（Tushare fund_portfolio API 不返回 name 字段）
                    stock_name = stock_name_mapping.get(stock_code, '')

                    # 解析报告期
                    report_date_str = row.get('end_date')
                    report_date = None
                    import pandas as pd
                    if pd.notna(report_date_str) and report_date_str:
                        try:
                            from datetime import datetime
                            report_date = datetime.strptime(str(report_date_str), '%Y%m%d').date()
                        except ValueError:
                            pass

                    # 权重百分比转小数
                    weight_raw = row.get('stk_mkv_ratio')
                    weight = None
                    if pd.notna(weight_raw) and weight_raw:
                        weight = float(weight_raw) / 100.0

                    position = schemas.FundStockPositionCreate(
                        stock_code=stock_code,
                        stock_name=stock_name,
                        shares=float(row.get('amount', 0)) if pd.notna(row.get('amount')) else None,
                        market_value=float(row.get('mkv', 0)) if pd.notna(row.get('mkv')) else None,
                        weight=weight,
                        cost_price=None,
                        report_date=report_date
                    )
                    positions.append(position)

                if not positions:
                    logger.warning(f"  [跳过] {fund_code} 所有持仓记录解析失败")
                    skip_count += 1
                    continue

                # 保存到数据库
                count = crud.update_fund_stock_positions(db, fund.id, positions)
                db.commit()

                # v1.7.3: 统计权重数据完整性
                weight_filled = sum(1 for p in positions if p.weight is not None)
                total_weight_filled += weight_filled

                logger.info(f"  [成功] {fund_code} 同步了 {count} 条持仓记录（权重完整: {weight_filled}/{count}）")
                success_count += 1
                total_positions += count

            except Exception as e:
                logger.error(f"  [错误] {fund_code} 同步失败: {str(e)}")
                error_count += 1
                db.rollback()

        # 输出统计结果
        logger.info(f"\n" + "=" * 60)
        logger.info(f"批量同步完成！")
        logger.info(f"=" * 60)
        logger.info(f"总基金数: {total_funds}")
        logger.info(f"同步成功: {success_count}")
        logger.info(f"跳过: {skip_count}")
        logger.info(f"失败: {error_count}")
        logger.info(f"总持仓记录: {total_positions}")
        logger.info(f"权重数据完整: {total_weight_filled}/{total_positions} ({100*total_weight_filled/total_positions if total_positions > 0 else 0:.1f}%)")
        logger.info(f"=" * 60)

    except Exception as e:
        logger.error(f"批量同步过程出错: {str(e)}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    sync_all_fund_positions()
