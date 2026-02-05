"""
Tushare Pro 数据获取服务

提供基金股票持仓查询和股票实时行情获取功能
使用新浪财经源获取实时股票数据
"""
import tushare as ts
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import logging
import time
from ..config import get_settings
from ..utils.encoding import clean_stock_name, validate_chinese_name

logger = logging.getLogger(__name__)
settings = get_settings()


class TushareService:
    """Tushare Pro 数据获取服务"""

    def __init__(self):
        """初始化 Tushare Pro 客户端"""
        if not settings.TUSHARE_TOKEN or settings.TUSHARE_TOKEN == "":
            raise ValueError("TUSHARE_TOKEN 未配置，请在 .env 文件中设置 TUSHARE_TOKEN")
        ts.set_token(settings.TUSHARE_TOKEN)
        self.pro = ts.pro_api()
        self.last_call_time = None  # 上次调用时间

    def _rate_limit_delay(self):
        """添加 API 调用延迟，避免频率限制"""
        if self.last_call_time:
            elapsed = time.time() - self.last_call_time
            if elapsed < 1.0:  # 两次调用间隔至少 1 秒
                sleep_time = 1.0 - elapsed
                logger.debug(f"[Tushare] 频率限制：等待 {sleep_time:.2f} 秒")
                time.sleep(sleep_time)

    def get_fund_portfolio(self, fund_code: str, period: str = None) -> pd.DataFrame:
        """
        获取基金股票持仓明细

        Args:
            fund_code: 基金代码（如：000001，会自动添加 .OF 后缀）
            period: 报告期（如：202401），默认获取最新

        Returns:
            DataFrame: 持仓明细数据
        """
        try:
            # 自动添加 .OF 后缀（如果还没有）
            if not fund_code.endswith('.OF'):
                fund_code = f"{fund_code}.OF"
                logger.info(f"[Tushare] 自动为基金代码添加 .OF 后缀: {fund_code}")

            # 频率限制延迟
            self._rate_limit_delay()

            logger.info(f"[Tushare] 正在调用 fund_portfolio API: {fund_code}")
            self.last_call_time = time.time()

            # 如果没有指定 period，获取最新季度的数据
            if period is None:
                # 默认使用空字符串，Tushare 会返回最新的数据
                df = self.pro.fund_portfolio(ts_code=fund_code)
            else:
                df = self.pro.fund_portfolio(ts_code=fund_code, period=period)

            # 检查返回数据
            if df.empty:
                logger.warning(f"[Tushare] {fund_code} 返回空数据，可能原因：")
                logger.warning(f"  1. 该基金暂无股票持仓披露")
                logger.warning(f"  2. Tushare API 暂无该基金数据")
                logger.warning(f"  3. API 调用频率限制（建议稍后重试）")
            else:
                logger.info(f"[Tushare] {fund_code} 成功获取 {len(df)} 条持仓记录")

            return df

        except Exception as e:
            error_str = str(e)
            logger.error(f"[Tushare] 获取基金持仓失败 {fund_code}: {e}")

            # 判断是否是频率限制错误
            if "限制" in error_str or "limit" in error_str.lower() or "额度" in error_str:
                logger.error(f"[Tushare] API 频率限制或积分不足，请稍后重试")
            elif "权限" in error_str or "permission" in error_str.lower():
                logger.error(f"[Tushare] API 权限不足，请检查 Tushare 账户权限")

            return pd.DataFrame()

    def get_stock_names_batch(self, stock_codes: List[str]) -> Dict[str, str]:
        """
        批量查询股票名称（带编码处理）

        使用 Tushare stock_basic API 批量获取股票名称

        Args:
            stock_codes: 股票代码列表（格式：000001.SZ）

        Returns:
            Dict[str, str]: 股票代码到名称的映射
            {
                '000001.SZ': '平安银行',
                '600519.SH': '贵州茅台',
                ...
            }
        """
        try:
            logger.info(f"[Tushare] 正在批量查询 {len(stock_codes)} 只股票的名称")

            # 调用 Tushare stock_basic API
            # 注意：stock_basic API 不支持一次查询多个股票，需要分批查询或使用其他方式
            # 这里使用单个调用查询所有股票列表，然后在内存中过滤
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,name,area,industry,list_date'
            )

            if df.empty:
                logger.warning(f"[Tushare] stock_basic 返回空数据")
                return {}

            # 构建股票代码到名称的映射，应用编码清理
            name_mapping = {}
            for _, row in df.iterrows():
                stock_code = row['ts_code']
                raw_name = row['name']

                # ✅ 编码处理：清理可能的乱码
                clean_name = clean_stock_name(str(raw_name))

                # 验证名称有效性
                if not clean_name or not validate_chinese_name(clean_name):
                    logger.debug(f"[Tushare] 股票 {stock_code} 名称无效: {raw_name}")
                    clean_name = f"股票{stock_code.split('.')[0]}"  # 使用备用名称

                name_mapping[stock_code] = clean_name

            # 过滤出我们需要的股票
            result = {code: name_mapping.get(code, '') for code in stock_codes}
            found_count = sum(1 for name in result.values() if name)

            logger.info(f"[Tushare] 成功获取 {found_count}/{len(stock_codes)} 只股票的名称")
            return result

        except Exception as e:
            logger.error(f"[Tushare] 批量查询股票名称失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}

    def get_stock_realtime(self, stock_codes: List[str]) -> Dict:
        """
        获取股票实时行情（多数据源：efinance 主，Tushare 备）

        优先使用 efinance，失败时降级到 Tushare 爬虫

        Args:
            stock_codes: 股票代码列表（格式：000001.SZ）

        Returns:
            Dict: 实时行情数据，key 为股票代码
        """
        # 方案1: efinance（主数据源）
        result = self._get_efinance_realtime(stock_codes)
        if result:
            return result

        # 方案2: Tushare 爬虫（备用）
        logger.warning("[数据源切换] efinance 失败，切换到 Tushare 爬虫接口")
        return self._get_tushare_realtime(stock_codes)

    def _get_efinance_realtime(self, stock_codes: List[str]) -> Dict:
        """使用 efinance 获取实时行情"""
        try:
            import efinance as ef

            logger.info(f"[Efinance] 正在获取 {len(stock_codes)} 只股票的实时行情")
            logger.debug(f"[Efinance] 股票代码列表: {stock_codes}")

            # 检查是否为交易时间，非交易时间 API 可能不可用
            now = datetime.now()
            if now.weekday() >= 5:  # 5=周六, 6=周日
                logger.warning(f"[Efinance] 当前是周末（{now.strftime('%Y-%m-%d %H:%M')}），非交易时间，API 可能不可用")
            elif not (9 <= now.hour < 15):  # 非交易时段
                logger.warning(f"[Efinance] 当前是非交易时间（{now.hour}点），API 可能不可用")

            # efinance API: 获取所有 A 股实时行情
            all_stocks_df = ef.stock.get_realtime_quotes()

            if all_stocks_df is None or all_stocks_df.empty:
                logger.warning(f"[Efinance] 获取股票实时行情失败：返回空数据")
                return {}

            # 构建股票代码映射（去除交易所后缀进行匹配）
            result = {}
            for stock_code in stock_codes:
                # 提取股票代码（去除 .SZ/.SH/.BJ 后缀）
                code_suffix_removed = stock_code.split('.')[0]

                # 在返回数据中查找匹配的股票
                matching_rows = all_stocks_df[
                    all_stocks_df['股票代码'] == code_suffix_removed
                ]

                if not matching_rows.empty:
                    row = matching_rows.iloc[0]
                    # ✅ 编码处理：清理股票名称
                    raw_name = row.get('股票名称', '')
                    clean_name = clean_stock_name(str(raw_name))

                    result[stock_code] = {
                        'code': stock_code,
                        'name': clean_name,
                        'price': float(row['最新价']) if pd.notna(row.get('最新价')) else None,
                        'change_pct': float(row['涨跌幅']) if pd.notna(row.get('涨跌幅')) else None,
                        'volume': int(row['成交量']) if pd.notna(row.get('成交量')) else None,
                        'amount': float(row['成交额']) if pd.notna(row.get('成交额')) else None,
                        'update_time': datetime.now(),
                        'data_source': 'efinance'
                    }

            logger.info(f"[Efinance] 成功获取 {len(result)}/{len(stock_codes)} 只股票的实时行情")
            return result

        except Exception as e:
            logger.error(f"[efinance] 获取实时行情失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}

    def _get_tushare_realtime(self, stock_codes: List[str]) -> Dict:
        """
        使用 Tushare 爬虫获取实时行情（备用方案）

        从新浪财经爬取实时股票数据
        """
        try:
            logger.info(f"[Tushare] 正在爬取 {len(stock_codes)} 只股票的实时行情")

            # 检查交易时间
            now = datetime.now()
            if now.weekday() >= 5:
                logger.warning(f"[Tushare] 当前是周末，非交易时间")
            elif not (9 <= now.hour < 15):
                logger.warning(f"[Tushare] 当前是非交易时间（{now.hour}点）")

            # 使用 Tushare realtime_quote 接口
            df = ts.realtime_quote(ts_code=','.join(stock_codes))

            if df.empty:
                logger.warning(f"[Tushare] realtime_quote 返回空数据")
                # 降级：尝试使用 daily 接口获取最新交易日数据
                return self._get_realtime_fallback(stock_codes)

            # 处理返回数据
            result = {}
            for _, row in df.iterrows():
                stock_code = row['ts_code']
                # ✅ 编码处理：清理股票名称
                raw_name = row.get('name', '')
                clean_name = clean_stock_name(str(raw_name))

                result[stock_code] = {
                    'code': stock_code,
                    'name': clean_name,
                    'price': float(row['price']) if pd.notna(row.get('price')) else None,
                    'change_pct': float(row['change_pct']) if pd.notna(row.get('change_pct')) else None,
                    'change': float(row['change']) if pd.notna(row.get('change')) else None,
                    'volume': int(row['volume']) if pd.notna(row.get('volume')) else None,
                    'amount': float(row['amount']) if pd.notna(row.get('amount')) else None,
                    'update_time': datetime.now(),
                    'data_source': 'tushare_realtime'
                }

            logger.info(f"[Tushare] 成功获取 {len(result)}/{len(stock_codes)} 只股票的实时行情")
            return result

        except Exception as e:
            logger.error(f"[Tushare] realtime_quote 接口失败: {e}")
            # 降级方案
            return self._get_realtime_fallback(stock_codes)

    def _get_realtime_fallback(self, stock_codes: List[str]) -> Dict:
        """
        实时行情降级方案：使用通用行情接口

        如果 realtime_quote 失败，尝试使用其他接口获取实时数据
        """
        try:
            logger.info(f"[Tushare] 使用降级方案获取 {len(stock_codes)} 只股票的最新数据")

            # 使用 daily 接口获取最新交易日数据
            today = datetime.now().strftime("%Y%m%d")

            df = self.pro.daily(
                ts_code=','.join(stock_codes),
                trade_date=today,
                fields='ts_code,close,open,high,low,vol,amount,pct_chg'
            )

            if df.empty:
                logger.warning(f"[Tushare] 降级方案：今天还没有交易数据")
                return {}

            result = {}
            for _, row in df.iterrows():
                stock_code = row['ts_code']
                # ✅ 编码处理：清理股票名称
                raw_name = row.get('name', '')
                clean_name = clean_stock_name(str(raw_name))

                result[stock_code] = {
                    'code': stock_code,
                    'name': clean_name,
                    'price': float(row['close']),
                    'change_pct': float(row['pct_chg']),
                    'volume': int(row['vol']),
                    'amount': float(row['amount']),
                    'update_time': datetime.now(),
                    'data_source': 'tushare_daily_fallback'
                }

            logger.info(f"[Tushare] 降级方案成功获取 {len(result)}/{len(stock_codes)} 只股票的最新数据")
            return result

        except Exception as e:
            logger.error(f"[Tushare] 降级方案也失败: {e}")
            return {}

    def calculate_fund_realtime_nav(
        self,
        fund_code: str,
        stock_positions: List[Dict],
        latest_nav: float
    ) -> Optional[Dict]:
        """
        根据股票持仓计算基金实时估值

        计算逻辑：
        1. 获取所有持仓股票的实时涨跌幅
        2. 按持仓占比加权平均
        3. 计算实时估值 = 最新净值 × (1 + 加权涨跌幅)

        Args:
            fund_code: 基金代码
            stock_positions: 股票持仓列表，格式：[{'stock_code': '000001.SZ', 'weight': 0.05}, ...]
            latest_nav: 最新单位净值

        Returns:
            Dict: 实时估值数据，包含：
                - fund_code: 基金代码
                - realtime_nav: 实时估值净值
                - increase_rate: 涨跌幅(%)
                - latest_nav: 最新正式净值
                - stock_count: 持仓股票数
                - update_time: 更新时间
                - data_source: 数据源标识
        """
        if not stock_positions:
            print(f"[Tushare] 基金 {fund_code} 没有持仓数据")
            return None

        # 提取股票代码
        stock_codes = [pos['stock_code'] for pos in stock_positions]

        # 获取股票实时行情
        realtime_quotes = self.get_stock_realtime(stock_codes)

        if not realtime_quotes:
            print(f"[Tushare] 无法获取股票实时行情")
            return None

        # 计算加权平均涨跌幅
        weighted_change_pct = 0.0
        valid_count = 0

        for position in stock_positions:
            code = position['stock_code']
            weight = float(position.get('weight', 0))

            if code in realtime_quotes and weight > 0:
                quote = realtime_quotes[code]
                change_pct = quote.get('change_pct')

                if change_pct is not None:
                    # 加权平均涨跌幅（change_pct 已经是百分比形式，如 2.5 表示 2.5%）
                    weighted_change_pct += weight * (change_pct / 100)
                    valid_count += 1

        # 计算实时净值估算
        realtime_nav = latest_nav * (1 + weighted_change_pct)

        return {
            'fund_code': fund_code,
            'realtime_nav': round(realtime_nav, 4),
            'increase_rate': round(weighted_change_pct * 100, 2),
            'latest_nav': latest_nav,
            'stock_count': valid_count,
            'update_time': datetime.now(),
            'data_source': 'efinance'
        }


# 全局单例实例
tushare_service = TushareService()
