"""
Tushare 服务集成测试

测试 TushareService 的数据获取和频率限制功能
"""
import pytest
import time
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.services.tushare_service import TushareService


@pytest.mark.integration
class TestTushareService:
    """测试 Tushare 服务"""

    @pytest.fixture
    def tushare_service(self, monkeypatch):
        """创建 Tushare 服务实例（使用 Mock token）"""
        monkeypatch.setenv("TUSHARE_TOKEN", "test_token_12345")
        # 需要重新导入以获取新的环境变量
        from app import config
        # 重新加载配置
        config.get_settings.cache_clear()

        # Mock tushare.set_token 和 ts.pro_api
        with patch('tushare.set_token'):
            with patch('tushare.pro_api') as mock_pro_api:
                mock_pro_instance = MagicMock()
                mock_pro_api.return_value = mock_pro_instance
                service = TushareService.__new__(TushareService)
                service.pro = mock_pro_instance
                service.last_call_time = None
                yield service, mock_pro_instance

    def test_get_fund_portfolio_success(self, tushare_service):
        """测试成功获取基金持仓"""
        service, mock_pro = tushare_service

        # Mock API 响应
        mock_df = pd.DataFrame({
            'ts_code': ['000001.OF', '000001.OF'],
            'symbol': ['000001.SZ', '000002.SZ'],
            'name': ['平安银行', '万科A'],
            'amount': [1000000, 2000000],
            'mkv': [50000000, 60000000],
            'stk_mkv_ratio': [5.0, 6.0],
            'end_date': ['20240331', '20240331']
        })
        mock_pro.fund_portfolio.return_value = mock_df

        df = service.get_fund_portfolio("000001")

        assert not df.empty
        assert len(df) == 2
        assert df.iloc[0]['symbol'] == '000001.SZ'
        mock_pro.fund_portfolio.assert_called_once()

    def test_get_fund_portfolio_with_period(self, tushare_service):
        """测试带 period 参数的获取"""
        service, mock_pro = tushare_service

        mock_df = pd.DataFrame({
            'ts_code': ['000001.OF'],
            'symbol': ['000001.SZ'],
            'name': ['平安银行'],
            'amount': [1000000],
            'mkv': [50000000],
            'stk_mkv_ratio': [5.0],
            'end_date': ['20240331']
        })
        mock_pro.fund_portfolio.return_value = mock_df

        df = service.get_fund_portfolio("000001", period="202401")

        assert not df.empty
        mock_pro.fund_portfolio.assert_called_once_with(ts_code='000001.OF', period='202401')

    def test_get_fund_portfolio_auto_add_suffix(self, tushare_service):
        """测试自动添加 .OF 后缀"""
        service, mock_pro = tushare_service

        mock_df = pd.DataFrame()
        mock_pro.fund_portfolio.return_value = mock_df

        # 不带后缀的基金代码
        service.get_fund_portfolio("000001")

        # 验证调用时自动添加了 .OF 后缀
        call_args = mock_pro.fund_portfolio.call_args
        assert call_args[1]['ts_code'] == '000001.OF'

    def test_get_fund_portfolio_empty_response(self, tushare_service):
        """测试 API 返回空数据"""
        service, mock_pro = tushare_service

        mock_df = pd.DataFrame()
        mock_pro.fund_portfolio.return_value = mock_df

        df = service.get_fund_portfolio("000001")

        assert df.empty

    def test_get_fund_portfolio_exception_handling(self, tushare_service):
        """测试异常处理"""
        service, mock_pro = tushare_service

        # Mock 抛出异常
        mock_pro.fund_portfolio.side_effect = Exception("API Error")

        df = service.get_fund_portfolio("000001")

        # 应该返回空 DataFrame 而不是抛出异常
        assert df.empty

    def test_rate_limiting(self, tushare_service):
        """测试频率限制（两次调用间隔至少 1 秒）"""
        service, mock_pro = tushare_service

        mock_df = pd.DataFrame()
        mock_pro.fund_portfolio.return_value = mock_df

        # 第一次调用
        service.get_fund_portfolio("000001")
        first_call_time = service.last_call_time

        # 立即第二次调用（应该被延迟）
        start = time.time()
        service.get_fund_portfolio("000002")
        elapsed = time.time() - start

        # 验证至少等待了 1 秒
        assert elapsed >= 0.9  # 允许 0.1 秒误差

    def test_get_stock_realtime_success(self, tushare_service):
        """测试获取股票实时行情"""
        service, mock_pro = tushare_service

        # Mock ts.realtime_quote
        with patch('tushare.realtime_quote') as mock_realtime:
            mock_df = pd.DataFrame({
                'ts_code': ['000001.SZ', '600000.SH'],
                'name': ['平安银行', '浦发银行'],
                'price': [12.5, 8.3],
                'change_pct': [2.5, -1.2],
                'volume': [1000000, 800000],
                'amount': [12500000, 6640000]
            })
            mock_realtime.return_value = mock_df

            result = service.get_stock_realtime(['000001.SZ', '600000.SH'])

            assert len(result) == 2
            assert '000001.SZ' in result
            assert result['000001.SZ']['price'] == 12.5
            assert result['000001.SZ']['change_pct'] == 2.5

    def test_get_stock_realtime_empty(self, tushare_service):
        """测试实时行情空响应"""
        service, _ = tushare_service

        with patch('tushare.realtime_quote') as mock_realtime:
            mock_realtime.return_value = pd.DataFrame()

            result = service.get_stock_realtime(['000001.SZ'])

            assert result == {}

    def test_calculate_fund_realtime_nav(self, tushare_service):
        """测试计算基金实时估值"""
        service, _ = tushare_service

        with patch('tushare.realtime_quote') as mock_realtime:
            # Mock 股票实时行情
            mock_df = pd.DataFrame({
                'ts_code': ['000001.SZ', '600000.SH'],
                'name': ['平安银行', '浦发银行'],
                'price': [12.5, 8.3],
                'change_pct': [2.5, -1.2],
                'volume': [1000000, 800000],
                'amount': [12500000, 6640000]
            })
            mock_realtime.return_value = mock_df

            # 股票持仓数据
            stock_positions = [
                {'stock_code': '000001.SZ', 'weight': 0.05},
                {'stock_code': '600000.SH', 'weight': 0.03}
            ]
            latest_nav = 1.5

            result = service.calculate_fund_realtime_nav(
                "000001",
                stock_positions,
                latest_nav
            )

            assert result is not None
            assert result['fund_code'] == "000001"
            assert result['latest_nav'] == 1.5
            assert result['stock_count'] == 2
            assert 'realtime_nav' in result
            assert 'increase_rate' in result

    def test_calculate_fund_realtime_nav_no_positions(self, tushare_service):
        """测试没有持仓数据时的估值计算"""
        service, _ = tushare_service

        result = service.calculate_fund_realtime_nav("000001", [], 1.5)

        assert result is None

    def test_calculate_fund_realtime_nav_no_quotes(self, tushare_service):
        """测试没有实时行情数据时的估值计算"""
        service, _ = tushare_service

        with patch('tushare.realtime_quote') as mock_realtime:
            mock_realtime.return_value = pd.DataFrame()

            stock_positions = [
                {'stock_code': '000001.SZ', 'weight': 0.05}
            ]
            latest_nav = 1.5

            result = service.calculate_fund_realtime_nav(
                "000001",
                stock_positions,
                latest_nav
            )

            assert result is None
