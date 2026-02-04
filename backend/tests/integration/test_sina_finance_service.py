"""
东方财富服务集成测试

测试 SinaFinanceService 的数据获取和降级功能
"""
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from app.services.sina_finance_service import SinaFinanceService


@pytest.mark.integration
class TestSinaFinanceService:
    """测试东方财富服务"""

    @pytest.fixture
    def sina_service(self):
        """创建东方财富服务实例"""
        return SinaFinanceService()

    def test_get_fund_portfolio_success(self, sina_service):
        """测试成功获取基金持仓"""
        # Mock HTTP 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
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

        with patch.object(sina_service.session, 'get', return_value=mock_response):
            df = sina_service.get_fund_portfolio("000001")

            assert not df.empty
            assert len(df) == 2
            assert '000001.SZ' in df['ts_code'].values
            assert '600000.SH' in df['ts_code'].values

    def test_get_fund_portfolio_empty_response(self, sina_service):
        """测试 API 返回空数据"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ErrCode': 0,
            'ErrMsg': '',
            'Data': []
        }

        with patch.object(sina_service.session, 'get', return_value=mock_response):
            df = sina_service.get_fund_portfolio("000001")

            assert df.empty

    def test_get_fund_portfolio_api_error(self, sina_service):
        """测试 API 返回错误"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ErrCode': -1,
            'ErrMsg': '参数错误',
            'Data': None
        }

        with patch.object(sina_service.session, 'get', return_value=mock_response):
            df = sina_service.get_fund_portfolio("000001")

            assert df.empty

    def test_get_fund_portfolio_http_error(self, sina_service):
        """测试 HTTP 错误"""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch.object(sina_service.session, 'get', return_value=mock_response):
            df = sina_service.get_fund_portfolio("000001")

            assert df.empty

    def test_get_fund_portfolio_network_error(self, sina_service):
        """测试网络错误"""
        import requests

        with patch.object(sina_service.session, 'get', side_effect=requests.exceptions.ConnectionError()):
            df = sina_service.get_fund_portfolio("000001")

            assert df.empty

    def test_get_fund_portfolio_market_code_conversion(self, sina_service):
        """测试市场代码转换"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ErrCode': 0,
            'Data': [
                {
                    'StockCode': '000001',
                    'Market': 0,  # 深圳市场
                    'StockName': '平安银行',
                    'StockNumber': 1000000,
                    'MarketValue': 50000000,
                    'Weight': 5.0,
                    'ReportDate': '2024-03-31'
                },
                {
                    'StockCode': '600000',
                    'Market': 1,  # 上海市场
                    'StockName': '浦发银行',
                    'StockNumber': 1500000,
                    'MarketValue': 55000000,
                    'Weight': 5.5,
                    'ReportDate': '2024-03-31'
                },
                {
                    'StockCode': '000002',
                    'Market': '0',  # 字符串形式的深圳市场
                    'StockName': '万科A',
                    'StockNumber': 2000000,
                    'MarketValue': 60000000,
                    'Weight': 6.0,
                    'ReportDate': '2024-03-31'
                },
                {
                    'StockCode': '600036',
                    'Market': '1',  # 字符串形式的上海市场
                    'StockName': '招商银行',
                    'StockNumber': 1200000,
                    'MarketValue': 45000000,
                    'Weight': 4.5,
                    'ReportDate': '2024-03-31'
                }
            ]
        }

        with patch.object(sina_service.session, 'get', return_value=mock_response):
            df = sina_service.get_fund_portfolio("000001")

            assert len(df) == 4
            stock_codes = df['ts_code'].tolist()
            assert '000001.SZ' in stock_codes
            assert '600000.SH' in stock_codes
            assert '000002.SZ' in stock_codes
            assert '600036.SH' in stock_codes

    def test_rate_limiting(self, sina_service):
        """测试频率限制（两次请求间隔至少 0.5 秒）"""
        import time

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ErrCode': 0, 'Data': []}

        with patch.object(sina_service.session, 'get', return_value=mock_response):
            # 第一次调用
            sina_service.get_fund_portfolio("000001")

            # 立即第二次调用（应该被延迟）
            start = time.time()
            sina_service.get_fund_portfolio("000002")
            elapsed = time.time() - start

            # 验证至少等待了 0.5 秒
            assert elapsed >= 0.4  # 允许 0.1 秒误差

    def test_get_fund_portfolio_backup_success(self, sina_service):
        """测试备用方案成功获取数据"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
        <script>
        var Data_StockCodeChange = {
            "data": [
                {"code": "000001", "name": "平安银行", "amount": 1000000, "value": 50000000, "ratio": 5.0, "date": "2024-03-31"},
                {"code": "600000", "name": "浦发银行", "amount": 1500000, "value": 55000000, "ratio": 5.5, "date": "2024-03-31"}
            ]
        };
        </script>
        </html>
        '''

        with patch.object(sina_service.session, 'get', return_value=mock_response):
            df = sina_service.get_fund_portfolio_backup("000001")

            assert not df.empty
            assert len(df) == 2

    def test_get_fund_portfolio_backup_no_data(self, sina_service):
        """测试备用方案未找到数据"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>No data</body></html>'

        with patch.object(sina_service.session, 'get', return_value=mock_response):
            df = sina_service.get_fund_portfolio_backup("000001")

            assert df.empty

    def test_get_fund_portfolio_backup_exception_handling(self, sina_service):
        """测试备用方案异常处理"""
        import requests

        with patch.object(sina_service.session, 'get', side_effect=requests.exceptions.Timeout()):
            df = sina_service.get_fund_portfolio_backup("000001")

            assert df.empty
