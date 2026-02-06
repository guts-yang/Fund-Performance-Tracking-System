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
import json
from ..config import get_settings
from ..utils.encoding import clean_stock_name, validate_chinese_name
from ..services.efinance_client import efinance_client
from ..utils.retry_helper import APICallError
from ..utils.redis_client import redis_client

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

        # 检查 Redis 缓存是否可用
        if redis_client.is_available():
            logger.info("[TushareService] Redis 缓存已启用")
        else:
            logger.warning("[TushareService] Redis 缓存不可用，将每次调用 Tushare API")

    def _get_cache_key(self, stock_code: str) -> str:
        """生成股票名称缓存键"""
        return f"stock:name:{stock_code}"

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

    def ensure_stock_names(
        self,
        positions: List[Dict],
        code_field: str = 'stock_code',
        name_field: str = 'stock_name'
    ) -> List[Dict]:
        """
        确保持仓数据中的股票名称完整且有效

        检查每个持仓记录的股票名称：
        1. 如果为空，查询 Tushare 补充
        2. 如果是乱码，使用编码工具修复
        3. 使用 Redis 缓存避免重复查询

        Args:
            positions: 持仓记录列表
            code_field: 股票代码字段名（默认 'stock_code'）
            name_field: 股票名称字段名（默认 'stock_name'）

        Returns:
            修复后的持仓记录列表（不修改原列表）
        """
        from ..utils.encoding import fix_gbk_mojibake

        # 第一遍遍历：收集需要查询的股票代码
        missing_codes = []
        for pos in positions:
            stock_code = pos.get(code_field, '')
            stock_name = pos.get(name_field, '')

            # 检查名称是否有效
            if not stock_name or not validate_chinese_name(stock_name):
                if stock_code:
                    # 检查 Redis 缓存
                    cache_key = self._get_cache_key(stock_code)
                    cached_name = redis_client.get(cache_key)

                    if not cached_name:
                        missing_codes.append(stock_code)

        # 批量查询缺失的名称
        if missing_codes:
            logger.info(f"[名称补充] 正在查询 {len(missing_codes)} 只股票的名称")
            name_mapping = self.get_stock_names_batch(missing_codes)

            # 更新 Redis 缓存
            if name_mapping and redis_client.is_available():
                cache_data = {
                    self._get_cache_key(code): name
                    for code, name in name_mapping.items()
                    if name  # 只缓存有效名称
                }
                redis_client.mset(cache_data, ttl=settings.STOCK_NAME_CACHE_TTL)
                logger.info(f"[名称补充] 已缓存 {len(cache_data)} 只股票名称到 Redis")

            logger.info(
                f"[名称补充] 成功获取 {len([n for n in name_mapping.values() if n])}/"
                f"{len(missing_codes)} 只股票的名称"
            )

        # 第二遍遍历：修复或补充名称
        result = []
        for pos in positions:
            pos_copy = pos.copy()  # 避免修改原数据
            stock_code = pos_copy.get(code_field, '')
            stock_name = pos_copy.get(name_field, '')

            # 策略 1：名称为空，从 Redis 缓存获取
            if not stock_name:
                cache_key = self._get_cache_key(stock_code)
                cached_name = redis_client.get(cache_key)
                if cached_name:
                    pos_copy[name_field] = cached_name
                    logger.debug(f"[名称补充] {stock_code}: 使用 Redis 缓存")

            # 策略 2：名称存在但可能是乱码，尝试修复
            elif not validate_chinese_name(stock_name):
                logger.debug(f"[名称修复] {stock_code}: 检测到乱码 '{stock_name}'")

                # 尝试修复 GBK 乱码
                fixed_name = fix_gbk_mojibake(stock_name)
                if validate_chinese_name(fixed_name):
                    pos_copy[name_field] = fixed_name
                    logger.info(f"[名称修复] {stock_code}: '{stock_name}' → '{fixed_name}'")
                else:
                    # 修复失败，尝试清理
                    cleaned = clean_stock_name(stock_name)
                    if validate_chinese_name(cleaned):
                        pos_copy[name_field] = cleaned
                        logger.info(f"[名称修复] {stock_code}: 清理后 '{cleaned}'")
                    else:
                        # 仍然无效，从 Redis 缓存获取
                        cache_key = self._get_cache_key(stock_code)
                        cached_name = redis_client.get(cache_key)
                        if cached_name:
                            pos_copy[name_field] = cached_name
                            logger.info(f"[名称修复] {stock_code}: 使用 Redis 缓存名称替换乱码")

            result.append(pos_copy)

        return result

    def clear_name_cache(self) -> None:
        """清空股票名称缓存（Redis）"""
        if redis_client.is_available():
            deleted_count = redis_client.clear_pattern("stock:name:*")
            logger.info(f"[名称缓存] 已清空 Redis 缓存，删除 {deleted_count} 个键")
        else:
            logger.warning("[名称缓存] Redis 不可用，无法清空缓存")

    def get_stock_realtime(self, stock_codes: List[str]) -> Dict:
        """
        获取股票实时行情（带Redis缓存）

        优先使用 efinance，失败时降级到 Tushare 爬虫

        Args:
            stock_codes: 股票代码列表（格式：000001.SZ）

        Returns:
            Dict: 实时行情数据，key 为股票代码
        """
        import json
        from ..config import settings

        # 判断是否为交易时间
        is_trading = self._is_trading_time()
        ttl = settings.STOCK_REALTIME_CACHE_TTL_TRADING if is_trading else settings.STOCK_REALTIME_CACHE_TTL_NON_TRADING

        # 尝试从Redis批量获取
        cache_keys = [self._get_realtime_cache_key(code) for code in stock_codes]
        cached_values = redis_client.mget(cache_keys)

        results = {}
        missed_codes = []

        # 检查缓存命中情况
        for idx, code in enumerate(stock_codes):
            cached_value = cached_values[idx]
            if cached_value:
                if cached_value == "NULL":
                    logger.debug(f"[实时行情缓存] 空值命中: {code}")
                    continue
                try:
                    # 反序列化JSON
                    results[code] = json.loads(cached_value)
                    logger.debug(f"[实时行情缓存] 命中: {code}")
                except json.JSONDecodeError:
                    logger.warning(f"[实时行情缓存] 反序列化失败: {code}")
                    missed_codes.append(code)
            else:
                missed_codes.append(code)

        # 如果全部命中，直接返回
        if not missed_codes:
            logger.info(f"[实时行情缓存] 全部命中 {len(results)}/{len(stock_codes)} 只股票")
            return results

        # 缓存未命中的股票，调用API获取
        logger.info(f"[实时行情缓存] 未命中 {len(missed_codes)}/{len(stock_codes)} 只股票，调用API")

        # 优先使用 efinance
        fresh_data = self._get_efinance_realtime(missed_codes)
        if not fresh_data:
            # 降级到 Tushare
            logger.warning("[数据源切换] efinance 失败，切换到 Tushare 爬虫接口")
            fresh_data = self._get_tushare_realtime(missed_codes)

        # 更新Redis缓存
        if fresh_data and redis_client.is_available():
            cache_data = {}
            for code, quote_data in fresh_data.items():
                cache_key = self._get_realtime_cache_key(code)
                # 序列化为JSON（包含 datetime 对象需要自定义序列化器）
                cache_data[cache_key] = json.dumps(
                    quote_data,
                    default=self._json_serializer,
                    ensure_ascii=False
                )

            if cache_data:
                redis_client.mset(cache_data, ttl=ttl)
                logger.info(f"[实时行情缓存] 已更新 {len(cache_data)} 只股票到 Redis")

        # 合并缓存和新鲜数据
        results.update(fresh_data)
        return results

    def _get_efinance_realtime(self, stock_codes: List[str]) -> Dict:
        """使用 efinance 获取实时行情（带重试）"""
        try:
            logger.info(f"[Efinance] 正在获取 {len(stock_codes)} 只股票的实时行情")
            logger.debug(f"[Efinance] 股票代码列表: {stock_codes}")

            # 检查是否为交易时间，非交易时间 API 可能不可用
            now = datetime.now()
            if now.weekday() >= 5:  # 5=周六, 6=周日
                logger.warning(f"[Efinance] 当前是周末（{now.strftime('%Y-%m-%d %H:%M')}），非交易时间，API 可能不可用")
            elif not (9 <= now.hour < 15):  # 非交易时段
                logger.warning(f"[Efinance] 当前是非交易时间（{now.hour}点），API 可能不可用")

            # efinance API: 获取所有 A 股实时行情（带重试）
            all_stocks_df = efinance_client.get_realtime_quotes()

            if all_stocks_df is None or all_stocks_df.empty:
                logger.warning(f"[Efinance] 获取股票实时行情失败：返回空数据")
                # 空值缓存（防止穿透）
                if redis_client.is_available():
                    from ..config import settings
                    null_cache_data = {
                        self._get_realtime_cache_key(code): "NULL"
                        for code in stock_codes
                    }
                    redis_client.mset(null_cache_data, ttl=settings.STOCK_REALTIME_CACHE_NULL_TTL)
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

        except APICallError as e:
            logger.error(f"[Efinance] 获取实时行情失败: {e.message}, error_type={e.error_type}")
            return {}
        except Exception as e:
            logger.error(f"[Efinance] 获取实时行情失败: {e}")
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

    def _is_trading_time(self) -> bool:
        """判断当前是否是交易时间"""
        from datetime import datetime as dt

        now = datetime.now()

        # 周末不是交易日
        if now.weekday() >= 5:
            return False

        # 9:30-15:00 为交易时间
        current_time = now.time()
        start_time = dt.strptime("09:30", "%H:%M").time()
        end_time = dt.strptime("15:00", "%H:%M").time()

        return start_time <= current_time <= end_time

    def _get_realtime_cache_key(self, stock_code: str) -> str:
        """生成实时行情缓存键"""
        return f"stock:realtime:{stock_code}"

    def _json_serializer(self, obj):
        """JSON序列化器（处理 datetime 对象）"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")


# 全局单例实例
tushare_service = TushareService()
