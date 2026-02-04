"""
Tushare API Mock 数据

提供模拟的 Tushare API 响应数据
"""
import pandas as pd
from typing import Optional
from unittest.mock import MagicMock


class MockTushareAPI:
    """Tushare API Mock 类"""

    @staticmethod
    def mock_fund_portfolio_success() -> pd.DataFrame:
        """成功的持仓响应（标准数据）"""
        return pd.DataFrame({
            'ts_code': ['000001.OF', '000001.OF', '000001.OF'],
            'symbol': ['000001.SZ', '000002.SZ', '600000.SH'],
            'name': ['平安银行', '万科A', '浦发银行'],
            'amount': [1000000, 2000000, 1500000],
            'mkv': [50000000, 60000000, 55000000],
            'stk_mkv_ratio': [5.0, 6.0, 5.5],
            'end_date': ['20240331', '20240331', '20240331']
        })

    @staticmethod
    def mock_fund_portfolio_with_fund_code() -> pd.DataFrame:
        """包含基金代码的响应（用于测试过滤逻辑）"""
        return pd.DataFrame({
            'ts_code': ['000001.OF'],
            'symbol': ['000001.OF'],  # 错误：基金代码被误认为股票代码
            'name': ['伪装成股票的基金'],
            'amount': [1000000],
            'mkv': [50000000],
            'stk_mkv_ratio': [5.0],
            'end_date': ['20240331']
        })

    @staticmethod
    def mock_fund_portfolio_empty() -> pd.DataFrame:
        """空响应"""
        return pd.DataFrame()

    @staticmethod
    def mock_fund_portfolio_malformed() -> pd.DataFrame:
        """格式错误响应（缺少必要字段）"""
        return pd.DataFrame({
            'wrong_field': ['data']
        })

    @staticmethod
    def mock_fund_portfolio_with_null_values() -> pd.DataFrame:
        """包含空值的响应"""
        return pd.DataFrame({
            'ts_code': ['000001.OF', '000001.OF'],
            'symbol': ['000001.SZ', None],
            'name': ['平安银行', None],
            'amount': [1000000, None],
            'mkv': [50000000, None],
            'stk_mkv_ratio': [5.0, None],
            'end_date': ['20240331', None]
        })

    @staticmethod
    def mock_fund_portfolio_large_dataset() -> pd.DataFrame:
        """大数据集响应（50条记录）"""
        symbols = [f"{str(i).zfill(6)}.SZ" for i in range(1, 51)]
        names = [f"股票{i}" for i in range(1, 51)]
        amounts = [1000000 * i for i in range(1, 51)]
        mkvs = [50000000 * i for i in range(1, 51)]
        ratios = [5.0 + i * 0.1 for i in range(50)]

        return pd.DataFrame({
            'ts_code': ['000001.OF'] * 50,
            'symbol': symbols,
            'name': names,
            'amount': amounts,
            'mkv': mkvs,
            'stk_mkv_ratio': ratios,
            'end_date': ['20240331'] * 50
        })

    @staticmethod
    def mock_realtime_quote_success() -> pd.DataFrame:
        """成功的实时行情响应"""
        return pd.DataFrame({
            'ts_code': ['000001.SZ', '600000.SH', '000002.SZ'],
            'name': ['平安银行', '浦发银行', '万科A'],
            'price': [12.5, 8.3, 15.2],
            'change_pct': [2.5, -1.2, 0.8],
            'volume': [1000000, 800000, 1200000],
            'amount': [12500000, 6640000, 18240000]
        })

    @staticmethod
    def mock_realtime_quote_empty() -> pd.DataFrame:
        """空实时行情响应"""
        return pd.DataFrame()


def create_mock_tushare_service(response_df: Optional[pd.DataFrame] = None):
    """
    创建 Mock 的 TushareService

    Args:
        response_df: 要返回的 DataFrame，默认为成功响应

    Returns:
        MagicMock: Mock 的 TushareService 实例
    """
    if response_df is None:
        response_df = MockTushareAPI.mock_fund_portfolio_success()

    mock_service = MagicMock()
    mock_service.get_fund_portfolio.return_value = response_df
    mock_service.get_stock_realtime.return_value = {
        '000001.SZ': {
            'code': '000001.SZ',
            'name': '平安银行',
            'price': 12.5,
            'change_pct': 2.5,
            'volume': 1000000,
            'amount': 12500000
        }
    }

    return mock_service
