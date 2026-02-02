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

            if fund_info is None:
                logger.warning(f"基金 {fund_code} 未找到数据")
                return {
                    "fund_code": fund_code,
                    "fund_name": f"基金{fund_code}",
                    "fund_type": "开放式基金",
                    "latest_nav": 0,
                }

            # 处理不同类型的返回值 (dict 或 pandas Series)
            if hasattr(fund_info, 'empty') and fund_info.empty:
                logger.warning(f"基金 {fund_code} 数据为空")
                return {
                    "fund_code": fund_code,
                    "fund_name": f"基金{fund_code}",
                    "fund_type": "开放式基金",
                    "latest_nav": 0,
                }

            # 安全地获取基金信息
            fund_name = f"基金{fund_code}"
            fund_type = "开放式基金"
            latest_nav = 0

            if hasattr(fund_info, 'get'):
                # 是 dict 或 pandas Series
                fund_name = fund_info.get("基金简称", f"基金{fund_code}")
                fund_type = fund_info.get("基金类型", "开放式基金")
                latest_nav = fund_info.get("最新净值", 0)
            elif isinstance(fund_info, dict):
                fund_name = fund_info.get("基金简称", f"基金{fund_code}")
                fund_type = fund_info.get("基金类型", "开放式基金")
                latest_nav = fund_info.get("最新净值", 0)

            return {
                "fund_code": fund_code,
                "fund_name": fund_name,
                "fund_type": fund_type,
                "latest_nav": float(latest_nav) if latest_nav else 0,
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
            # 修复：移除错误的 pz 参数
            history_df = ef.fund.get_quote_history(fund_code)

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

    @staticmethod
    def is_trading_time() -> bool:
        """
        判断当前是否是交易时间（盘中）

        基金交易时间：
        - 工作日 9:30-15:00
        - 排除周末和节假日

        Returns:
            是否是交易时间
        """
        try:
            now = datetime.now()

            # 判断是否是工作日（周一到周五）
            if now.weekday() >= 5:  # 5=周六, 6=周日
                return False

            # 判断时间是否在 9:30-15:00
            current_time = now.time()
            start_time = datetime.strptime("09:30", "%H:%M").time()
            end_time = datetime.strptime("15:00", "%H:%M").time()

            return start_time <= current_time <= end_time

        except Exception as e:
            logger.error(f"判断交易时间失败: {str(e)}")
            return False

    @staticmethod
    def get_fund_realtime_valuation(fund_code: str) -> Optional[Dict[str, Any]]:
        """
        获取基金盘中实时估值

        Args:
            fund_code: 基金代码 (6位)

        Returns:
            实时估值信息字典
            - realtime_nav: 实时估算净值
            - increase_rate: 实时估算涨跌幅
            - estimate_time: 估算时间
            - latest_nav_date: 最新净值日期
        """
        try:
            # 使用 efinance 的实时估值 API
            result = ef.fund.get_realtime_increase_rate(fund_code)

            if result is None or (hasattr(result, 'empty') and result.empty):
                logger.warning(f"基金 {fund_code} 暂无实时估值数据")
                return None

            # 获取第一条数据
            if hasattr(result, 'iloc'):
                latest = result.iloc[0]
            else:
                latest = result

            # 获取最新净值和涨跌幅
            latest_nav = None
            increase_rate = Decimal("0")

            # 处理不同格式的返回数据
            if hasattr(latest, 'get'):
                latest_nav = latest.get("最新净值")
                increase_rate_val = latest.get("估算涨跌幅", 0)
            elif isinstance(latest, dict):
                latest_nav = latest.get("最新净值")
                increase_rate_val = latest.get("估算涨跌幅", 0)
            else:
                # 如果是 pandas Series，尝试通过索引获取
                try:
                    latest_nav = latest["最新净值"] if "最新净值" in latest.index else None
                    increase_rate_val = latest["估算涨跌幅"] if "估算涨跌幅" in latest.index else 0
                except:
                    pass

            # 处理涨跌幅
            if increase_rate_val is None or pd.isna(increase_rate_val):
                increase_rate = Decimal("0")
            else:
                if isinstance(increase_rate_val, str):
                    increase_rate_val = increase_rate_val.replace("%", "").strip()
                increase_rate = Decimal(str(increase_rate_val))

            # 计算实时估算净值
            realtime_nav = None
            if latest_nav and not pd.isna(latest_nav):
                latest_nav_value = float(latest_nav)
                realtime_nav = Decimal(str(latest_nav_value * (1 + float(increase_rate) / 100)))

            return {
                "fund_code": fund_code,
                "realtime_nav": realtime_nav,
                "increase_rate": increase_rate,
                "estimate_time": datetime.now(),
                "latest_nav_date": latest.get("最新净值公开日期") if hasattr(latest, 'get') else None
            }

        except Exception as e:
            logger.error(f"获取基金 {fund_code} 实时估值失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    @staticmethod
    def get_all_funds_realtime_valuation(fund_codes: list) -> list[Dict[str, Any]]:
        """
        批量获取多只基金的实时估值

        Args:
            fund_codes: 基金代码列表

        Returns:
            实时估值列表
        """
        try:
            # efinance 支持批量获取
            result = ef.fund.get_realtime_increase_rate(fund_codes)

            if result is None or (hasattr(result, 'empty') and result.empty):
                return []

            valuations = []
            for idx in range(len(result)):
                row = result.iloc[idx] if hasattr(result, 'iloc') else result[idx]

                fund_code = None
                latest_nav = None
                increase_rate_val = 0

                # 提取数据
                if hasattr(row, 'get'):
                    fund_code = row.get("基金代码")
                    latest_nav = row.get("最新净值")
                    increase_rate_val = row.get("估算涨跌幅", 0)
                elif isinstance(row, dict):
                    fund_code = row.get("基金代码")
                    latest_nav = row.get("最新净值")
                    increase_rate_val = row.get("估算涨跌幅", 0)
                elif hasattr(row, '__getitem__'):
                    # pandas Series
                    if "基金代码" in row.index:
                        fund_code = row["基金代码"]
                    if "最新净值" in row.index:
                        latest_nav = row["最新净值"]
                    if "估算涨跌幅" in row.index:
                        increase_rate_val = row["估算涨跌幅"]

                if not fund_code:
                    continue

                # 处理涨跌幅
                if increase_rate_val is None or pd.isna(increase_rate_val):
                    increase_rate = Decimal("0")
                else:
                    if isinstance(increase_rate_val, str):
                        increase_rate_val = increase_rate_val.replace("%", "").strip()
                    increase_rate = Decimal(str(increase_rate_val))

                # 计算实时估算净值
                realtime_nav = None
                if latest_nav and not pd.isna(latest_nav):
                    latest_nav_value = float(latest_nav)
                    realtime_nav = Decimal(str(latest_nav_value * (1 + float(increase_rate) / 100)))

                valuations.append({
                    "fund_code": fund_code,
                    "realtime_nav": realtime_nav,
                    "increase_rate": increase_rate,
                    "estimate_time": datetime.now(),
                    "latest_nav_date": row.get("最新净值公开日期") if hasattr(row, 'get') else None
                })

            return valuations

        except Exception as e:
            logger.error(f"批量获取实时估值失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
