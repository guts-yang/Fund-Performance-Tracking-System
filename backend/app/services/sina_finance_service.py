"""
东方财富网数据获取服务

提供基金股票持仓查询功能
使用爬虫技术从东方财富网获取数据
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import logging
import time
import re

logger = logging.getLogger(__name__)


class SinaFinanceService:
    """东方财富网数据获取服务"""

    def __init__(self):
        """初始化服务"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.last_call_time = None

    def _rate_limit_delay(self):
        """添加请求延迟，避免被封"""
        if self.last_call_time:
            elapsed = time.time() - self.last_call_time
            if elapsed < 0.5:  # 两次请求间隔至少 0.5 秒
                sleep_time = 0.5 - elapsed
                logger.debug(f"[东方财富] 频率限制：等待 {sleep_time:.2f} 秒")
                time.sleep(sleep_time)

    def get_fund_portfolio(self, fund_code: str) -> pd.DataFrame:
        """
        从东方财富网获取基金股票持仓明细

        Args:
            fund_code: 基金代码（如：012043，不需要带 .OF 后缀）

        Returns:
            DataFrame: 持仓明细数据，包含字段：
                - ts_code: 股票代码（如：000001.SZ）
                - symbol: 股票名称
                - amount: 持仓数量
                - mkv: 持仓市值
                - stk_mkv_ratio: 持仓市值占比（百分比）
                - end_date: 报告期
        """
        try:
            # 频率限制延迟
            self._rate_limit_delay()

            logger.info(f"[东方财富] 正在获取基金 {fund_code} 的持仓数据")

            # 方案1: 使用东方财富网API
            url = "http://api.fund.eastmoney.com/cc/LSPositionService"
            params = {
                'fundCode': fund_code,
                'type': 'LSPosition',
                'sortBy': 'stockNumber',
                'sortDirection': 'desc'
            }

            self.last_call_time = time.time()
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code != 200:
                logger.error(f"[东方财富] API 请求失败: {response.status_code}")
                return pd.DataFrame()

            data = response.json()

            # 检查返回数据
            if data.get('ErrCode') != 0:
                logger.error(f"[东方财富] API 返回错误: {data.get('ErrMsg', '未知错误')}")
                return pd.DataFrame()

            # 解析数据
            positions_data = data.get('Data', [])
            if not positions_data:
                logger.warning(f"[东方财富] 基金 {fund_code} 返回空数据，可能该基金没有股票持仓披露")
                return pd.DataFrame()

            # 转换为 DataFrame
            df_data = []
            for item in positions_data:
                # 股票代码需要添加后缀
                stock_code = item.get('StockCode', '')
                market = item.get('Market', '')

                # 市场代码转换
                if market == 1 or market == '1':
                    stock_code_full = f"{stock_code}.SH"
                elif market == 0 or market == '0':
                    stock_code_full = f"{stock_code}.SZ"
                else:
                    # 尝试从其他渠道获取市场信息
                    stock_code_full = stock_code

                df_data.append({
                    'ts_code': stock_code_full,
                    'symbol': item.get('StockName', ''),
                    'amount': item.get('StockNumber', 0),
                    'mkv': item.get('MarketValue', 0),
                    'stk_mkv_ratio': item.get('Weight', 0),  # 已经是百分比形式
                    'end_date': item.get('ReportDate', '')
                })

            df = pd.DataFrame(df_data)

            if not df.empty:
                logger.info(f"[东方财富] {fund_code} 成功获取 {len(df)} 条持仓记录")
            else:
                logger.warning(f"[东方财富] {fund_code} 解析后返回空数据")

            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"[东方财富] 网络请求失败 {fund_code}: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"[东方财富] 获取基金持仓失败 {fund_code}: {e}", exc_info=True)
            return pd.DataFrame()

    def get_fund_portfolio_backup(self, fund_code: str) -> pd.DataFrame:
        """
        备用方案：从天天基金网获取基金持仓（如果东方财富失败）

        Args:
            fund_code: 基金代码

        Returns:
            DataFrame: 持仓明细数据
        """
        try:
            logger.info(f"[天天基金] 正在获取基金 {fund_code} 的持仓数据（备用方案）")

            url = f"http://fundf10.eastmoney.com/ccmx_{fund_code}.html"

            self.last_call_time = time.time()
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                logger.error(f"[天天基金] 页面请求失败: {response.status_code}")
                return pd.DataFrame()

            # 解析页面中的 JSON 数据
            content = response.text
            # 查找包含持仓数据的 JSON
            pattern = r'var\s+Data_StockCodeChange\s*=\s*(\{.*?\});'
            match = re.search(pattern, content, re.DOTALL)

            if not match:
                logger.warning(f"[天天基金] 未找到持仓数据")
                return pd.DataFrame()

            import json
            data_str = match.group(1)
            data = json.loads(data_str)

            # 解析持仓数据
            positions_data = data.get('data', [])
            if not positions_data:
                logger.warning(f"[天天基金] 基金 {fund_code} 返回空数据")
                return pd.DataFrame()

            # 转换为 DataFrame（格式与东方财富API一致）
            df_data = []
            for item in positions_data:
                stock_code = item.get('code', '')
                # 判断市场
                if stock_code.startswith('6'):
                    stock_code_full = f"{stock_code}.SH"
                elif stock_code.startswith('0') or stock_code.startswith('3'):
                    stock_code_full = f"{stock_code}.SZ"
                else:
                    stock_code_full = stock_code

                df_data.append({
                    'ts_code': stock_code_full,
                    'symbol': item.get('name', ''),
                    'amount': item.get('amount', 0),
                    'mkv': item.get('value', 0),
                    'stk_mkv_ratio': item.get('ratio', 0),
                    'end_date': item.get('date', '')
                })

            df = pd.DataFrame(df_data)
            logger.info(f"[天天基金] {fund_code} 成功获取 {len(df)} 条持仓记录")

            return df

        except Exception as e:
            logger.error(f"[天天基金] 获取基金持仓失败 {fund_code}: {e}")
            return pd.DataFrame()


# 全局单例实例
sina_finance_service = SinaFinanceService()
