"""
端到端测试 - 完整同步流程

测试从 API 调用到数据库更新的完整数据流
"""
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import patch
import pandas as pd

from app.models import FundStockPosition
from app import crud


@pytest.mark.e2e
@pytest.mark.integration
class TestCompleteSyncWorkflow:
    """测试完整的同步工作流"""

    @patch('app.api.stock_positions.sina_finance_service')
    def test_complete_sync_and_retrieve_workflow(
        self, mock_sina, client, test_db, sample_fund
    ):
        """
        测试完整的同步工作流：
        1. 创建基金
        2. 同步持仓数据
        3. 验证数据已保存到数据库
        4. 通过 API 获取持仓数据
        5. 验证数据完整性
        """
        fund_id = sample_fund.id
        fund_code = sample_fund.fund_code

        # Mock 东方财富网返回数据
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame({
            'ts_code': ['000001.OF', '000001.OF', '000001.OF'],
            'symbol': ['000001.SZ', '000002.SZ', '600000.SH'],
            'name': ['平安银行', '万科A', '浦发银行'],
            'amount': [1000000, 2000000, 1500000],
            'mkv': [50000000, 60000000, 55000000],
            'stk_mkv_ratio': [5.0, 6.0, 5.5],
            'end_date': ['20240331', '20240331', '20240331']
        })

        # 1. 同步持仓
        sync_response = client.post(f"/api/stock-positions/funds/{fund_id}/sync")
        assert sync_response.status_code == 200
        sync_data = sync_response.json()
        assert sync_data["success"] is True
        assert sync_data["funds_updated"] == 3

        # 2. 获取同步后的持仓
        get_response = client.get(f"/api/stock-positions/funds/{fund_id}")
        assert get_response.status_code == 200
        positions = get_response.json()
        assert len(positions) == 3

        # 3. 验证数据完整性
        stock_codes = {pos["stock_code"] for pos in positions}
        assert stock_codes == {"000001.SZ", "000002.SZ", "600000.SH"}

        for pos in positions:
            assert "stock_code" in pos
            assert "stock_name" in pos
            assert pos["stock_code"].endswith(('.SH', '.SZ'))
            assert pos["report_date"] == "2024-03-31"

            # 验证权重已正确转换（百分比 → 小数）
            if pos.get("weight"):
                assert 0 <= pos["weight"] <= 1
                # 5.0% → 0.05
                assert pos["weight"] < 1

    @patch('app.api.stock_positions.sina_finance_service')
    @patch('app.api.stock_positions.tushare_service')
    def test_fallback_workflow(
        self, mock_tushare, mock_sina, client, sample_fund
    ):
        """
        测试降级流程：
        1. 东方财富网返回空数据
        2. 降级到 Tushare
        3. Tushare 返回数据
        4. 数据成功保存
        """
        fund_id = sample_fund.id

        # 东方财富网返回空数据
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame()

        # Tushare 返回数据
        mock_tushare.get_fund_portfolio.return_value = pd.DataFrame({
            'ts_code': ['000001.OF'],
            'symbol': ['000001.SZ'],
            'name': ['平安银行'],
            'amount': [1000000],
            'mkv': [50000000],
            'stk_mkv_ratio': [5.0],
            'end_date': ['20240331']
        })

        # 同步
        response = client.post(f"/api/stock-positions/funds/{fund_id}/sync")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["funds_updated"] == 1

        # 验证两个服务都被调用
        mock_sina.get_fund_portfolio.assert_called_once()
        mock_tushare.get_fund_portfolio.assert_called_once()

    @patch('app.api.stock_positions.sina_finance_service')
    @patch('app.api.stock_positions.tushare_service')
    def test_both_apis_fail(self, mock_tushare, mock_sina, client, sample_fund):
        """
        测试两个 API 都失败的情况：
        1. 东方财富网返回空数据
        2. Tushare 也返回空数据
        3. 返回错误响应
        """
        fund_id = sample_fund.id

        # 两个 API 都返回空数据
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame()
        mock_tushare.get_fund_portfolio.return_value = pd.DataFrame()

        # 同步
        response = client.post(f"/api/stock-positions/funds/{fund_id}/sync")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["funds_updated"] == 0
        assert len(data["errors"]) > 0

    @patch('app.api.stock_positions.sina_finance_service')
    def test_data_validation_workflow(self, mock_sina, client, sample_fund):
        """
        测试数据验证流程：
        1. API 返回包含无效数据的混合数据
        2. 系统过滤掉无效数据
        3. 只保存有效数据
        """
        fund_id = sample_fund.id

        # Mock 返回包含无效代码的数据
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame({
            'ts_code': ['000001.OF', '000001.OF', '000001.OF', '000001.OF'],
            'symbol': ['000001.OF', 'INVALID', '000001.SZ', '600000.SH'],
            'name': ['伪装成股票', '无效代码', '平安银行', '浦发银行'],
            'amount': [1000000, 1000000, 1000000, 1500000],
            'mkv': [50000000, 50000000, 50000000, 55000000],
            'stk_mkv_ratio': [5.0, 5.0, 5.0, 5.5],
            'end_date': ['20240331', '20240331', '20240331', '20240331']
        })

        # 同步
        response = client.post(f"/api/stock-positions/funds/{fund_id}/sync")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # 只同步了 2 条有效数据
        assert data["funds_updated"] == 2

        # 验证只有有效数据被保存
        positions = crud.get_fund_stock_positions(test_db, fund_id)
        assert len(positions) == 2
        stock_codes = {pos.stock_code for pos in positions}
        assert stock_codes == {"000001.SZ", "600000.SH"}

    @patch('app.api.stock_positions.sina_finance_service')
    def test_replace_existing_data(self, mock_sina, client, test_db, sample_fund):
        """
        测试数据替换流程：
        1. 首次同步保存数据
        2. 再次同步替换数据
        3. 验证旧数据被删除
        """
        fund_id = sample_fund.id

        # 第一次同步
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame({
            'ts_code': ['000001.OF', '000001.OF'],
            'symbol': ['000001.SZ', '000002.SZ'],
            'name': ['平安银行', '万科A'],
            'amount': [1000000, 2000000],
            'mkv': [50000000, 60000000],
            'stk_mkv_ratio': [5.0, 6.0],
            'end_date': ['20240331', '20240331']
        })

        response1 = client.post(f"/api/stock-positions/funds/{fund_id}/sync")
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["funds_updated"] == 2

        positions1 = crud.get_fund_stock_positions(test_db, fund_id)
        assert len(positions1) == 2

        # 第二次同步（不同的数据）
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame({
            'ts_code': ['000001.OF'],
            'symbol': ['600000.SH'],
            'name': ['浦发银行'],
            'amount': [1500000],
            'mkv': [55000000],
            'stk_mkv_ratio': [5.5],
            'end_date': ['20240331']
        })

        response2 = client.post(f"/api/stock-positions/funds/{fund_id}/sync")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["funds_updated"] == 1

        # 验证旧数据被替换
        positions2 = crud.get_fund_stock_positions(test_db, fund_id)
        assert len(positions2) == 1
        assert positions2[0].stock_code == "600000.SH"

    @patch('app.api.stock_positions.sina_finance_service')
    def test_multiple_funds_sync(self, mock_sina, client, test_db, sample_funds):
        """
        测试多基金同步流程：
        1. 同步多个基金的持仓
        2. 验证各自的数据独立
        """
        funds = sample_funds  # [fund1, fund2, fund3]

        # Mock 返回不同的数据
        def mock_get_portfolio(fund_code):
            if fund_code == "000001":
                return pd.DataFrame({
                    'ts_code': ['000001.OF'],
                    'symbol': ['000001.SZ'],
                    'name': ['平安银行'],
                    'amount': [1000000],
                    'mkv': [50000000],
                    'stk_mkv_ratio': [5.0],
                    'end_date': ['20240331']
                })
            elif fund_code == "110022":
                return pd.DataFrame({
                    'ts_code': ['110022.OF'],
                    'symbol': ['600000.SH'],
                    'name': ['浦发银行'],
                    'amount': [1500000],
                    'mkv': [55000000],
                    'stk_mkv_ratio': [5.5],
                    'end_date': ['20240331']
                })
            else:
                return pd.DataFrame()

        mock_sina.get_fund_portfolio.side_effect = mock_get_portfolio

        # 同步所有基金
        for fund in funds:
            response = client.post(f"/api/stock-positions/funds/{fund.id}/sync")
            assert response.status_code == 200

        # 验证各自的数据
        fund1_positions = crud.get_fund_stock_positions(test_db, funds[0].id)
        fund2_positions = crud.get_fund_stock_positions(test_db, funds[1].id)
        fund3_positions = crud.get_fund_stock_positions(test_db, funds[2].id)

        assert len(fund1_positions) == 1
        assert len(fund2_positions) == 1
        assert len(fund3_positions) == 0

        assert fund1_positions[0].stock_code == "000001.SZ"
        assert fund2_positions[0].stock_code == "600000.SH"


@pytest.mark.e2e
@pytest.mark.integration
class TestErrorRecoveryWorkflow:
    """测试错误恢复流程"""

    @patch('app.api.stock_positions.sina_finance_service')
    def test_exception_handling(self, mock_sina, client, sample_fund):
        """测试异常处理"""
        fund_id = sample_fund.id

        # Mock 抛出异常
        mock_sina.get_fund_portfolio.side_effect = Exception("Network error")

        # 同步应该返回成功=False，但不应该抛出异常
        response = client.post(f"/api/stock-positions/funds/{fund_id}/sync")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Network error" in data["message"] or "同步失败" in data["message"]
