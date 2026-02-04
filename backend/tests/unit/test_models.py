"""
数据库模型单元测试

测试 SQLAlchemy 模型的创建、验证和约束
"""
import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app.models import Fund, FundStockPosition


class TestFundModel:
    """测试 Fund 模型"""

    def test_fund_creation(self, test_db):
        """测试创建基金记录"""
        fund = Fund(
            fund_code="000001",
            fund_name="测试基金",
            fund_type="股票型"
        )
        test_db.add(fund)
        test_db.commit()
        test_db.refresh(fund)

        assert fund.id is not None
        assert fund.fund_code == "000001"
        assert fund.fund_name == "测试基金"
        assert fund.fund_type == "股票型"
        assert fund.created_at is not None

    def test_fund_unique_constraint(self, test_db):
        """测试基金代码唯一约束"""
        fund1 = Fund(fund_code="000001", fund_name="基金1")
        test_db.add(fund1)
        test_db.commit()

        # 尝试创建相同代码的基金
        fund2 = Fund(fund_code="000001", fund_name="基金2")
        test_db.add(fund2)

        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_fund_relationships(self, test_db):
        """测试基金关联关系"""
        fund = Fund(fund_code="000001", fund_name="测试基金")
        test_db.add(fund)
        test_db.commit()
        test_db.refresh(fund)

        # 验证关联关系存在
        assert hasattr(fund, 'stock_positions')
        assert hasattr(fund, 'holdings')
        assert hasattr(fund, 'nav_history')


class TestFundStockPositionModel:
    """测试 FundStockPosition 模型"""

    def test_position_creation(self, test_db, sample_fund):
        """测试创建持仓记录"""
        position = FundStockPosition(
            fund_id=sample_fund.id,
            stock_code="000001.SZ",
            stock_name="平安银行",
            shares=Decimal("1000000"),
            market_value=Decimal("50000000.00"),
            weight=Decimal("0.05"),
            report_date=date(2024, 3, 31)
        )
        test_db.add(position)
        test_db.commit()
        test_db.refresh(position)

        assert position.id is not None
        assert position.stock_code == "000001.SZ"
        assert position.stock_name == "平安银行"
        assert position.shares == Decimal("1000000")
        assert position.market_value == Decimal("50000000.00")
        assert position.weight == Decimal("0.05")
        assert position.report_date == date(2024, 3, 31)

    def test_position_optional_fields(self, test_db, sample_fund):
        """测试可选字段"""
        position = FundStockPosition(
            fund_id=sample_fund.id,
            stock_code="000001.SZ"
            # 其他字段都是可选的
        )
        test_db.add(position)
        test_db.commit()
        test_db.refresh(position)

        assert position.stock_name is None
        assert position.shares is None
        assert position.market_value is None
        assert position.weight is None
        assert position.report_date is None

    def test_unique_constraint_violation(self, test_db, sample_fund):
        """测试唯一约束（fund_id + stock_code + report_date）"""
        # 创建第一条记录
        position1 = FundStockPosition(
            fund_id=sample_fund.id,
            stock_code="000001.SZ",
            report_date=date(2024, 3, 31)
        )
        test_db.add(position1)
        test_db.commit()

        # 尝试创建重复记录
        position2 = FundStockPosition(
            fund_id=sample_fund.id,
            stock_code="000001.SZ",
            report_date=date(2024, 3, 31)
        )
        test_db.add(position2)

        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_unique_constraint_different_dates(self, test_db, sample_fund):
        """测试相同基金和股票但不同报告期可以共存"""
        position1 = FundStockPosition(
            fund_id=sample_fund.id,
            stock_code="000001.SZ",
            report_date=date(2024, 3, 31)
        )
        test_db.add(position1)
        test_db.commit()

        # 相同基金和股票，但报告期不同 - 应该成功
        position2 = FundStockPosition(
            fund_id=sample_fund.id,
            stock_code="000001.SZ",
            report_date=date(2024, 6, 30)
        )
        test_db.add(position2)
        test_db.commit()

        assert position2.id is not None

    def test_unique_constraint_different_stocks(self, test_db, sample_fund):
        """测试相同基金和报告期但不同股票可以共存"""
        position1 = FundStockPosition(
            fund_id=sample_fund.id,
            stock_code="000001.SZ",
            report_date=date(2024, 3, 31)
        )
        test_db.add(position1)
        test_db.commit()

        # 相同基金和报告期，但股票不同 - 应该成功
        position2 = FundStockPosition(
            fund_id=sample_fund.id,
            stock_code="600000.SH",
            report_date=date(2024, 3, 31)
        )
        test_db.add(position2)
        test_db.commit()

        assert position2.id is not None

    def test_fund_cascade_delete(self, test_db):
        """测试基金删除时持仓级联删除"""
        fund = Fund(fund_code="000001", fund_name="测试基金")
        test_db.add(fund)
        test_db.commit()

        position = FundStockPosition(
            fund_id=fund.id,
            stock_code="000001.SZ"
        )
        test_db.add(position)
        test_db.commit()

        position_id = position.id

        # 删除基金
        test_db.delete(fund)
        test_db.commit()

        # 验证持仓已被级联删除
        deleted_position = test_db.query(FundStockPosition).filter(
            FundStockPosition.id == position_id
        ).first()
        assert deleted_position is None

    def test_position_repr(self, test_db, sample_fund):
        """测试 __repr__ 方法"""
        position = FundStockPosition(
            fund_id=sample_fund.id,
            stock_code="000001.SZ"
        )
        test_db.add(position)
        test_db.commit()

        repr_str = repr(position)
        assert "FundStockPosition" in repr_str
        assert str(position.id) in repr_str
        assert "000001.SZ" in repr_str
