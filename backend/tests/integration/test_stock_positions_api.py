"""
API 端点集成测试

测试持仓数据相关的 API 端点
"""
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock
import pandas as pd

from app.models import FundStockPosition
from app.schemas import FundStockPositionCreate
from app import crud


@pytest.mark.integration
class TestGetStockPositionsAPI:
    """测试获取持仓列表 API"""

    def test_get_positions_success(self, client, sample_fund_with_positions):
        """测试成功获取持仓"""
        fund_id = sample_fund_with_positions.id
        response = client.get(f"/api/stock-positions/funds/{fund_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # 验证响应结构
        position = data[0]
        assert "stock_code" in position
        assert "stock_name" in position
        assert "id" in position
        assert "fund_id" in position

    def test_get_positions_empty(self, client, sample_fund):
        """测试获取空持仓列表"""
        fund_id = sample_fund.id
        response = client.get(f"/api/stock-positions/funds/{fund_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_positions_fund_not_found(self, client, sample_fund, test_db):
        """测试获取不存在的基金"""
        # 删除基金，确保它不存在
        test_db.delete(sample_fund)
        test_db.commit()

        # 现在尝试获取已删除的基金
        response = client.get(f"/api/stock-positions/funds/{sample_fund.id}")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "不存在" in data["detail"]

    def test_get_positions_invalid_date_format(self, client, sample_fund):
        """测试无效的日期格式"""
        fund_id = sample_fund.id
        response = client.get(
            f"/api/stock-positions/funds/{fund_id}",
            params={"report_date": "invalid-date"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "格式错误" in data["detail"]

    def test_get_positions_valid_date(self, client, sample_fund, test_db):
        """测试有效的日期过滤"""
        fund_id = sample_fund.id

        # 创建不同日期的持仓
        positions = [
            FundStockPositionCreate(
                stock_code="000001.SZ",
                stock_name="平安银行",
                weight=Decimal("0.05"),
                report_date=date(2024, 3, 31)
            ),
            FundStockPositionCreate(
                stock_code="600000.SH",
                stock_name="浦发银行",
                weight=Decimal("0.06"),
                report_date=date(2024, 6, 30)
            ),
        ]

        for position_data in positions:
            crud.create_fund_stock_position(test_db, position_data, fund_id)

        # 查询特定日期
        response = client.get(
            f"/api/stock-positions/funds/{fund_id}",
            params={"report_date": "2024-03-31"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["report_date"] == "2024-03-31"

    def test_get_positions_ordering(self, client, sample_fund, test_db):
        """测试持仓按权重降序排列"""
        fund_id = sample_fund.id

        # 创建不同权重的持仓
        positions = [
            FundStockPositionCreate(
                stock_code="000001.SZ",
                weight=Decimal("0.03"),
                report_date=date(2024, 3, 31)
            ),
            FundStockPositionCreate(
                stock_code="600000.SH",
                weight=Decimal("0.10"),
                report_date=date(2024, 3, 31)
            ),
            FundStockPositionCreate(
                stock_code="000002.SZ",
                weight=Decimal("0.05"),
                report_date=date(2024, 3, 31)
            ),
        ]

        for position_data in positions:
            crud.create_fund_stock_position(test_db, position_data, fund_id)

        response = client.get(f"/api/stock-positions/funds/{fund_id}")

        assert response.status_code == 200
        data = response.json()
        weights = [float(pos["weight"]) for pos in data if pos["weight"] is not None]
        assert weights == sorted(weights, reverse=True)
        assert weights[0] == 0.10

    def test_response_data_types(self, client, sample_fund, test_db):
        """验证 API 返回的数据类型正确（Decimal 字段应序列化为数字）"""
        fund_id = sample_fund.id

        # 创建包含所有数值字段的测试数据
        position_data = FundStockPositionCreate(
            stock_code="000001.SZ",
            stock_name="平安银行",
            shares=Decimal("1000000.1234"),
            market_value=Decimal("50000000.56"),
            weight=Decimal("0.055"),
            cost_price=Decimal("10.1234"),
            report_date=date(2024, 3, 31)
        )
        crud.create_fund_stock_position(test_db, position_data, fund_id)

        # 发送请求
        response = client.get(f"/api/stock-positions/funds/{fund_id}")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1

        position = data[0]

        # 验证 Decimal 字段已正确序列化为数字类型（int 或 float）
        # 而不是字符串或其他类型
        assert isinstance(position["shares"], (int, float)), \
            f"shares 应该是数字类型，但得到 {type(position['shares'])}"
        assert isinstance(position["market_value"], (int, float)), \
            f"market_value 应该是数字类型，但得到 {type(position['market_value'])}"
        assert isinstance(position["weight"], (int, float)), \
            f"weight 应该是数字类型，但得到 {type(position['weight'])}"
        assert isinstance(position["cost_price"], (int, float)), \
            f"cost_price 应该是数字类型，但得到 {type(position['cost_price'])}"

        # 验证数值正确（精度可能会丢失，但应该在合理范围内）
        assert abs(position["shares"] - 1000000.1234) < 0.01
        assert abs(position["market_value"] - 50000000.56) < 0.01
        assert abs(position["weight"] - 0.055) < 0.0001
        assert abs(position["cost_price"] - 10.1234) < 0.0001


@pytest.mark.integration
class TestSyncStockPositionsAPI:
    """测试同步持仓数据 API"""

    @patch('app.api.stock_positions.sina_finance_service')
    @patch('app.api.stock_positions.tushare_service')
    def test_sync_positions_sina_success(
        self, mock_tushare, mock_sina, client, sample_fund
    ):
        """测试通过东方财富网成功同步"""
        # Mock 东方财富网返回数据
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame({
            'ts_code': ['000001.OF', '000001.OF'],
            'symbol': ['000001.SZ', '000002.SZ'],
            'name': ['平安银行', '万科A'],
            'amount': [1000000, 2000000],
            'mkv': [50000000, 60000000],
            'stk_mkv_ratio': [5.0, 6.0],
            'end_date': ['20240331', '20240331']
        })

        fund_id = sample_fund.id
        response = client.post(f"/api/stock-positions/funds/{fund_id}/sync")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["funds_updated"] == 2
        assert len(data["errors"]) == 0

        # 验证东方财富网被调用
        mock_sina.get_fund_portfolio.assert_called_once()

    @patch('app.api.stock_positions.sina_finance_service')
    @patch('app.api.stock_positions.tushare_service')
    def test_sync_positions_fallback_to_tushare(
        self, mock_tushare, mock_sina, client, sample_fund
    ):
        """测试东方财富失败，降级到 Tushare"""
        # Mock 东方财富网返回空数据
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame()

        # Mock Tushare 返回数据
        mock_tushare.get_fund_portfolio.return_value = pd.DataFrame({
            'ts_code': ['000001.OF'],
            'symbol': ['000001.SZ'],
            'name': ['平安银行'],
            'amount': [1000000],
            'mkv': [50000000],
            'stk_mkv_ratio': [5.0],
            'end_date': ['20240331']
        })

        fund_id = sample_fund.id
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
    def test_sync_positions_all_apis_empty(
        self, mock_tushare, mock_sina, client, sample_fund
    ):
        """测试两个 API 都返回空数据"""
        # 两个 API 都返回空数据
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame()
        mock_tushare.get_fund_portfolio.return_value = pd.DataFrame()

        fund_id = sample_fund.id
        response = client.post(f"/api/stock-positions/funds/{fund_id}/sync")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["funds_updated"] == 0
        assert len(data["errors"]) > 0

    @patch('app.api.stock_positions.sina_finance_service')
    @patch('app.api.stock_positions.tushare_service')
    def test_sync_positions_fund_not_found(
        self, mock_tushare, mock_sina, client, sample_fund, test_db
    ):
        """测试同步不存在的基金"""
        # 删除基金，确保它不存在
        test_db.delete(sample_fund)
        test_db.commit()

        response = client.post(f"/api/stock-positions/funds/{sample_fund.id}/sync")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

        # 验证服务未被调用
        mock_sina.get_fund_portfolio.assert_not_called()
        mock_tushare.get_fund_portfolio.assert_not_called()

    @patch('app.api.stock_positions.sina_finance_service')
    @patch('app.api.stock_positions.tushare_service')
    def test_sync_positions_filters_fund_codes(
        self, mock_tushare, mock_sina, client, sample_fund
    ):
        """测试过滤基金代码（.OF）"""
        # Mock 返回包含基金代码的数据
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame({
            'ts_code': ['000001.OF', '000001.OF', '000001.OF'],
            'symbol': ['000001.OF', '000001.SZ', '600000.SH'],
            'name': ['伪装成股票', '平安银行', '浦发银行'],
            'amount': [1000000, 1000000, 1500000],
            'mkv': [50000000, 50000000, 55000000],
            'stk_mkv_ratio': [5.0, 5.0, 5.5],
            'end_date': ['20240331', '20240331', '20240331']
        })

        fund_id = sample_fund.id
        response = client.post(f"/api/stock-positions/funds/{fund_id}/sync")

        assert response.status_code == 200
        data = response.json()
        # 应该只同步有效的股票代码（过滤掉 .OF）
        assert data["success"] is True
        assert data["funds_updated"] == 2

    @patch('app.api.stock_positions.sina_finance_service')
    @patch('app.api.stock_positions.tushare_service')
    def test_sync_positions_handles_null_values(
        self, mock_tushare, mock_sina, client, sample_fund
    ):
        """测试处理空值"""
        # Mock 返回包含空值的数据
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame({
            'ts_code': ['000001.OF', '000001.OF'],
            'symbol': ['000001.SZ', None],
            'name': ['平安银行', None],
            'amount': [1000000, None],
            'mkv': [50000000, None],
            'stk_mkv_ratio': [5.0, None],
            'end_date': ['20240331', None]
        })

        fund_id = sample_fund.id
        response = client.post(f"/api/stock-positions/funds/{fund_id}/sync")

        assert response.status_code == 200
        data = response.json()
        # 只同步有效的记录
        assert data["success"] is True
        assert data["funds_updated"] == 1

    @patch('app.api.stock_positions.sina_finance_service')
    def test_sync_positions_exception_handling(
        self, mock_sina, client, sample_fund
    ):
        """测试异常处理"""
        # Mock 抛出异常
        mock_sina.get_fund_portfolio.side_effect = Exception("API Error")

        fund_id = sample_fund.id
        response = client.post(f"/api/stock-positions/funds/{fund_id}/sync")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "API Error" in data["message"] or "同步失败" in data["message"]


@pytest.mark.integration
class TestStockPositionsDataValidation:
    """测试持仓数据验证"""

    @patch('app.api.stock_positions.sina_finance_service')
    def test_validate_weight_conversion(self, mock_sina, client, sample_fund, test_db):
        """测试权重百分比转换（API 返回百分比，需要除以 100）"""
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame({
            'ts_code': ['000001.OF'],
            'symbol': ['000001.SZ'],
            'name': ['平安银行'],
            'amount': [1000000],
            'mkv': [50000000],
            'stk_mkv_ratio': [5.5],  # 5.5% 应该转为 0.055
            'end_date': ['20240331']
        })

        fund_id = sample_fund.id
        response = client.post(f"/api/stock-positions/funds/{fund_id}/sync")

        assert response.status_code == 200

        # 验证数据已正确保存
        positions = crud.get_fund_stock_positions(test_db, fund_id)
        assert len(positions) == 1
        # 权重应该被转换为小数
        assert positions[0].weight == Decimal("0.055")

    @patch('app.api.stock_positions.sina_finance_service')
    def test_validate_date_parsing(self, mock_sina, client, sample_fund, test_db):
        """测试日期解析（字符串 '20240331' → date 对象）"""
        mock_sina.get_fund_portfolio.return_value = pd.DataFrame({
            'ts_code': ['000001.OF'],
            'symbol': ['000001.SZ'],
            'name': ['平安银行'],
            'amount': [1000000],
            'mkv': [50000000],
            'stk_mkv_ratio': [5.0],
            'end_date': ['20240331']
        })

        fund_id = sample_fund.id
        response = client.post(f"/api/stock-positions/funds/{fund_id}/sync")

        assert response.status_code == 200

        # 验证日期已正确解析
        positions = crud.get_fund_stock_positions(test_db, fund_id)
        assert len(positions) == 1
        assert positions[0].report_date == date(2024, 3, 31)
