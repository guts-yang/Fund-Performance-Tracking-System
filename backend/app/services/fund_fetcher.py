import efinance as ef
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class FundDataFetcher:
    """基金数据获取服务 - 使用 efinance (东方财富)"""

    @staticmethod
    def get_fund_info(fund_code: str) -> Dict[str, Any]:
        """
        获取基金基本信息

        Args:
            fund_code: 基金代码 (6位)

        Returns:
            基金信息字典
        """
        try:
            # 使用 get_base_info 获取基金基本信息
            fund_info = ef.fund.get_base_info(fund_code)

            if fund_info is None or fund_info.empty:
                logger.warning(f"基金 {fund_code} 未找到数据")
                return {
                    "fund_code": fund_code,
                    "fund_name": f"基金{fund_code}",
                    "fund_type": "开放式基金",
                    "latest_nav": 0,
                }

            return {
                "fund_code": fund_code,
                "fund_name": fund_info.get("基金简称", f"基金{fund_code}"),
                "fund_type": fund_info.get("基金类型", "开放式基金"),
                "latest_nav": fund_info.get("最新净值", 0),
            }

        except Exception as e:
            logger.error(f"获取基金 {fund_code} 信息失败: {str(e)}")
            return {
                "fund_code": fund_code,
                "fund_name": f"基金{fund_code}",
                "fund_type": "开放式基金",
                "latest_nav": 0,
            }

    @staticmethod
    def get_fund_nav(fund_code: str) -> Optional[Dict[str, Any]]:
        """
        获取基金最新净值

        Args:
            fund_code: 基金代码 (6位)

        Returns:
            净值信息字典
        """
        try:
            # 使用 get_quote_history 获取历史净值数据
            # pz=40000 表示获取全部历史数据
            history_df = ef.fund.get_quote_history(fund_code, pz=1)

            if history_df is None or history_df.empty:
                logger.warning(f"基金 {fund_code} 没有净值数据")
                return None

            # 获取最新一条（第一条是最新的）
            latest = history_df.iloc[0]

            # 解析日期
            nav_date = latest.get("日期")
            if nav_date is None:
                nav_date = datetime.now().date()
            elif isinstance(nav_date, str):
                nav_date = datetime.strptime(nav_date, "%Y-%m-%d").date()
            elif isinstance(nav_date, pd.Timestamp):
                nav_date = nav_date.date()

            # 解析单位净值
            unit_nav = latest.get("单位净值")
            if unit_nav is None or pd.isna(unit_nav):
                unit_nav = 0

            # 解析累计净值
            accumulated_nav = latest.get("累计净值")
            if accumulated_nav is None or pd.isna(accumulated_nav):
                accumulated_nav = unit_nav

            # 解析日增长率
            daily_growth_str = latest.get("涨跌幅")
            if daily_growth_str is None or pd.isna(daily_growth_str):
                daily_growth = Decimal("0")
            else:
                if isinstance(daily_growth_str, str):
                    daily_growth_str = daily_growth_str.replace("%", "").strip()
                daily_growth = Decimal(str(daily_growth_str)) / 100

            return {
                "fund_code": fund_code,
                "date": nav_date,
                "unit_nav": Decimal(str(unit_nav)),
                "accumulated_nav": Decimal(str(accumulated_nav)),
                "daily_growth": daily_growth,
            }

        except Exception as e:
            logger.error(f"获取基金 {fund_code} 净值失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    @staticmethod
    def get_fund_history(fund_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        获取基金历史净值数据

        Args:
            fund_code: 基金代码 (6位)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            历史净值列表
        """
        try:
            # 使用 get_quote_history 获取历史净值数据
            history_df = ef.fund.get_quote_history(fund_code, pz=40000)

            if history_df is None or history_df.empty:
                logger.warning(f"基金 {fund_code} 没有历史数据")
                return []

            result = []
            for _, row in history_df.iterrows():
                nav_date = row.get("日期")
                if nav_date is None:
                    continue

                if isinstance(nav_date, str):
                    nav_date = datetime.strptime(nav_date, "%Y-%m-%d").date()
                elif isinstance(nav_date, pd.Timestamp):
                    nav_date = nav_date.date()

                # 日期过滤
                if start_date:
                    start = datetime.strptime(start_date, "%Y-%m-%d").date()
                    if nav_date < start:
                        continue
                if end_date:
                    end = datetime.strptime(end_date, "%Y-%m-%d").date()
                    if nav_date > end:
                        continue

                # 解析净值
                unit_nav = row.get("单位净值")
                if unit_nav is None or pd.isna(unit_nav):
                    unit_nav = 0

                # 解析累计净值
                accumulated_nav = row.get("累计净值")
                if accumulated_nav is None or pd.isna(accumulated_nav):
                    accumulated_nav = unit_nav

                # 解析日增长率
                daily_growth_val = row.get("涨跌幅", "0")
                if isinstance(daily_growth_val, str):
                    daily_growth_val = daily_growth_val.replace("%", "").strip()
                elif pd.isna(daily_growth_val):
                    daily_growth_val = "0"

                result.append({
                    "date": nav_date,
                    "unit_nav": Decimal(str(unit_nav)),
                    "accumulated_nav": Decimal(str(accumulated_nav)),
                    "daily_growth": Decimal(str(daily_growth_val)) / 100,
                })

            return result

        except Exception as e:
            logger.error(f"获取基金 {fund_code} 历史数据失败: {str(e)}")
            return []

    @staticmethod
    def search_fund(keyword: str) -> list[Dict[str, Any]]:
        """
        搜索基金

        Args:
            keyword: 搜索关键词（基金代码或名称）

        Returns:
            基金列表
        """
        try:
            # efinance 的搜索功能
            # 通过 get_fund_codes 获取所有基金，然后筛选
            funds_df = ef.fund.get_fund_codes()

            if funds_df is None or funds_df.empty:
                return []

            # 根据关键词筛选
            if keyword.isdigit():
                # 按代码搜索
                filtered = funds_df[funds_df["基金代码"].str.contains(keyword)]
            else:
                # 按名称搜索
                filtered = funds_df[funds_df["基金简称"].str.contains(keyword, na=False)]

            result = []
            for _, row in filtered.head(10).iterrows():
                result.append({
                    "fund_code": row.get("基金代码", ""),
                    "fund_name": row.get("基金简称", ""),
                    "fund_type": "开放式基金",
                })

            return result

        except Exception as e:
            logger.error(f"搜索基金 {keyword} 失败: {str(e)}")
            return []

    @staticmethod
    def is_trading_day() -> bool:
        """
        判断今天是否是交易日

        Returns:
            是否是交易日
        """
        try:
            today = datetime.now().date()

            # 简单判断：周末不是交易日
            if today.weekday() >= 5:  # 5=周六, 6=周日
                return False

            # TODO: 可以接入更复杂的节假日判断API
            return True

        except Exception as e:
            logger.error(f"判断交易日失败: {str(e)}")
            return True  # 默认返回True
