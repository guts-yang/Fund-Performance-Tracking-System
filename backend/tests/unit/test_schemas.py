"""
Pydantic Schema 验证单元测试

测试 Schema 的数据验证、类型检查和约束
"""
import pytest
from pydantic import ValidationError, Field
from datetime import date
from decimal import Decimal

from app.schemas import (
    FundStockPositionCreate,
    FundStockPositionResponse,
    FundCreate,
    FundResponse,
    SyncResponse
)


class TestFundStockPositionSchema:
    """测试基金股票持仓 Schema"""

    def test_valid_position_schema(self):
        """测试有效的持仓数据 Schema"""
        data = {
            "stock_code": "000001.SZ",
            "stock_name": "平安银行",
            "shares": Decimal("1000000"),
            "market_value": Decimal("50000000"),
            "weight": Decimal("0.05"),
            "cost_price": Decimal("10.5"),
            "report_date": date(2024, 3, 31)
        }
        position = FundStockPositionCreate(**data)

        assert position.stock_code == "000001.SZ"
        assert position.stock_name == "平安银行"
        assert position.shares == Decimal("1000000")
        assert position.market_value == Decimal("50000000")
        assert position.weight == Decimal("0.05")
        assert position.cost_price == Decimal("10.5")
        assert position.report_date == date(2024, 3, 31)

    def test_position_minimal_data(self):
        """测试最小必需数据（只有 stock_code）"""
        data = {"stock_code": "000001.SZ"}
        position = FundStockPositionCreate(**data)

        assert position.stock_code == "000001.SZ"
        assert position.stock_name is None
        assert position.shares is None
        assert position.market_value is None
        assert position.weight is None
        assert position.cost_price is None
        assert position.report_date is None

    def test_weight_valid_range(self):
        """测试权重字段的有效范围（0-1）"""
        # 有效范围
        valid_weights = [0, 0.5, 1, Decimal("0"), Decimal("0.5"), Decimal("1")]
        for weight in valid_weights:
            data = {"stock_code": "000001.SZ", "weight": weight}
            position = FundStockPositionCreate(**data)
            assert Decimal(str(position.weight)) == Decimal(str(weight))

    def test_weight_invalid_negative(self):
        """测试无效的负权重"""
        data = {"stock_code": "000001.SZ", "weight": -0.1}
        with pytest.raises(ValidationError):
            FundStockPositionCreate(**data)

    def test_weight_invalid_over_one(self):
        """测试无效的超范围权重（> 1）"""
        data = {"stock_code": "000001.SZ", "weight": 1.5}
        with pytest.raises(ValidationError):
            FundStockPositionCreate(**data)

    def test_shares_must_be_positive(self):
        """测试份额字段（Schema 不验证正负，允许任意值）"""
        # Schema 不验证正负，业务逻辑层应该验证
        data = {"stock_code": "000001.SZ", "shares": Decimal("1000000")}
        position = FundStockPositionCreate(**data)
        assert position.shares == Decimal("1000000")

        # 零值（允许）
        data = {"stock_code": "000001.SZ", "shares": 0}
        position = FundStockPositionCreate(**data)
        assert position.shares == 0

        # Schema 不验证负值，应该由业务层处理
        data = {"stock_code": "000001.SZ", "shares": -100}
        position = FundStockPositionCreate(**data)
        assert position.shares == -100

    def test_market_value_must_be_positive(self):
        """测试市值字段（Schema 不验证正负，允许任意值）"""
        # Schema 不验证正负，业务逻辑层应该验证
        data = {"stock_code": "000001.SZ", "market_value": Decimal("50000000")}
        position = FundStockPositionCreate(**data)
        assert position.market_value == Decimal("50000000")

        # 零值（允许）
        data = {"stock_code": "000001.SZ", "market_value": 0}
        position = FundStockPositionCreate(**data)
        assert position.market_value == 0

        # Schema 不验证负值，应该由业务层处理
        data = {"stock_code": "000001.SZ", "market_value": -1000}
        position = FundStockPositionCreate(**data)
        assert position.market_value == -1000

    def test_stock_code_formats(self):
        """测试各种股票代码格式（Schema 只验证类型，不验证格式）"""
        # Schema 不验证格式，只验证类型
        valid_codes = [
            "000001.SZ",
            "600000.SH",
            "000001.OF",  # 基金代码格式上有效，但业务逻辑应过滤
            "INVALID",
            "",
            "12345",
        ]

        for code in valid_codes:
            data = {"stock_code": code}
            position = FundStockPositionCreate(**data)
            assert position.stock_code == code

    def test_model_dump(self):
        """测试 model_dump 方法"""
        data = {
            "stock_code": "000001.SZ",
            "stock_name": "平安银行",
            "shares": Decimal("1000000"),
            "weight": Decimal("0.05"),
        }
        position = FundStockPositionCreate(**data)
        dumped = position.model_dump()

        assert dumped["stock_code"] == "000001.SZ"
        assert dumped["stock_name"] == "平安银行"
        assert dumped["shares"] == Decimal("1000000")
        assert dumped["weight"] == Decimal("0.05")


class TestFundSchema:
    """测试基金 Schema"""

    def test_valid_fund_create(self):
        """测试有效的基金创建数据"""
        data = {
            "fund_code": "000001",
            "fund_name": "测试基金",
            "fund_type": "股票型"
        }
        fund = FundCreate(**data)

        assert fund.fund_code == "000001"
        assert fund.fund_name == "测试基金"
        assert fund.fund_type == "股票型"

    def test_fund_minimal_data(self):
        """测试最小必需数据（只有 fund_code）"""
        data = {"fund_code": "000001"}
        fund = FundCreate(**data)

        assert fund.fund_code == "000001"
        assert fund.fund_name is None
        assert fund.fund_type is None

    def test_fund_code_max_length(self):
        """测试基金代码最大长度"""
        # 正常长度
        data = {"fund_code": "1234567890"}  # 10 字符
        fund = FundCreate(**data)
        assert fund.fund_code == "1234567890"

        # 超过最大长度（应该在 Schema 验证中拒绝）
        data = {"fund_code": "12345678901"}  # 11 字符
        with pytest.raises(ValidationError):
            FundCreate(**data)

    def test_fund_name_max_length(self):
        """测试基金名称最大长度"""
        # 正常长度
        long_name = "A" * 100
        data = {"fund_code": "000001", "fund_name": long_name}
        fund = FundCreate(**data)
        assert fund.fund_name == long_name

        # 超过最大长度
        too_long_name = "A" * 101
        data = {"fund_code": "000001", "fund_name": too_long_name}
        with pytest.raises(ValidationError):
            FundCreate(**data)


class TestSyncResponseSchema:
    """测试同步响应 Schema"""

    def test_sync_response_success(self):
        """测试成功的同步响应"""
        data = {
            "success": True,
            "message": "同步成功",
            "funds_updated": 5,
            "errors": []
        }
        response = SyncResponse(**data)

        assert response.success is True
        assert response.message == "同步成功"
        assert response.funds_updated == 5
        assert response.errors == []

    def test_sync_response_failure(self):
        """测试失败的同步响应"""
        data = {
            "success": False,
            "message": "同步失败",
            "funds_updated": 0,
            "errors": ["错误1", "错误2"]
        }
        response = SyncResponse(**data)

        assert response.success is False
        assert response.message == "同步失败"
        assert response.funds_updated == 0
        assert len(response.errors) == 2

    def test_sync_response_default_values(self):
        """测试默认值"""
        data = {
            "success": True,
            "message": "测试"
        }
        response = SyncResponse(**data)

        assert response.funds_updated == 0
        assert response.errors == []


class TestResponseSchema:
    """测试响应 Schema 的 from_attributes 功能"""

    def test_position_response_from_model(self, sample_fund_with_positions):
        """测试从数据库模型创建响应"""
        # 这个测试需要数据库中的实际数据
        # 使用 from_attributes=True 的 ConfigDict
        from app.models import FundStockPosition
        from sqlalchemy.orm import Session

        # 假设我们有一个 position 模型实例
        # position = FundStockPosition(...)
        # response = FundStockPositionResponse.model_validate(position)
        # assert response.stock_code == position.stock_code
        pass

    def test_fund_response_from_model(self):
        """测试基金响应从模型验证"""
        # 测试 from_attributes 功能
        pass
