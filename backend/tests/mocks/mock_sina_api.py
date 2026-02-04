"""
东方财富 API Mock 数据

提供模拟的东方财富 API 响应数据
"""
import pandas as pd
from typing import Optional
from unittest.mock import Mock
import json


class MockSinaFinanceAPI:
    """东方财富 API Mock 类"""

    @staticmethod
    def mock_success_response():
        """成功的 API 响应（HTTP 响应对象）"""
        mock_response = Mock()
        mock_response.status_code = 200

        data = {
            'ErrCode': 0,
            'ErrMsg': '',
            'Data': [
                {
                    'StockCode': '000001',
                    'StockName': '平安银行',
                    'Market': 0,
                    'StockNumber': 1000000,
                    'MarketValue': 50000000,
                    'Weight': 5.0,
                    'ReportDate': '2024-03-31'
                },
                {
                    'StockCode': '600000',
                    'StockName': '浦发银行',
                    'Market': 1,
                    'StockNumber': 1500000,
                    'MarketValue': 55000000,
                    'Weight': 5.5,
                    'ReportDate': '2024-03-31'
                }
            ]
        }
        mock_response.json.return_value = data
        return mock_response

    @staticmethod
    def mock_empty_response():
        """空数据响应"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ErrCode': 0,
            'ErrMsg': '',
            'Data': []
        }
        return mock_response

    @staticmethod
    def mock_error_response():
        """API 错误响应"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ErrCode': -1,
            'ErrMsg': '参数错误',
            'Data': None
        }
        return mock_response

    @staticmethod
    def mock_http_error():
        """HTTP 错误响应"""
        mock_response = Mock()
        mock_response.status_code = 404
        return mock_response

    @staticmethod
    def mock_timeout_error():
        """超时错误"""
        import requests
        raise requests.exceptions.Timeout("Request timeout")

    @staticmethod
    def mock_success_dataframe() -> pd.DataFrame:
        """成功的 DataFrame 响应"""
        return pd.DataFrame({
            'ts_code': ['000001.SZ', '600000.SH'],
            'symbol': ['平安银行', '浦发银行'],
            'amount': [1000000, 1500000],
            'mkv': [50000000, 55000000],
            'stk_mkv_ratio': [5.0, 5.5],
            'end_date': ['2024-03-31', '2024-03-31']
        })


def create_mock_sina_service(response_df: Optional[pd.DataFrame] = None):
    """
    创建 Mock 的 SinaFinanceService

    Args:
        response_df: 要返回的 DataFrame，默认为成功响应

    Returns:
        MagicMock: Mock 的 SinaFinanceService 实例
    """
    if response_df is None:
        response_df = MockSinaFinanceAPI.mock_success_dataframe()

    mock_service = Mock()
    mock_service.get_fund_portfolio.return_value = response_df
    mock_service.get_fund_portfolio_backup.return_value = response_df

    return mock_service
