"""
CRUD 操作单元测试

测试数据库 CRUD 函数的正确性
"""
import pytest
from datetime import date
from decimal import Decimal

from app import crud
from app.models import Fund, FundStockPosition
from app.schemas import FundStockPositionCreate, FundCreate


class TestFundCRUD:
    """测试基金 CRUD 操作"""

    def test_get_fund(self, test_db):
        """测试获取单个基金"""
        fund = Fund(fund_code="000001", fund_name="测试基金")
        test_db.add(fund)
        test_db.commit()

        retrieved_fund = crud.get_fund(test_db, fund.id)
        assert retrieved_fund is not None
        assert retrieved_fund.fund_code == "000001"
        assert retrieved_fund.fund_name == "测试基金"

    def test_get_fund_not_found(self, test_db):
        """测试获取不存在的基金"""
        fund = crud.get_fund(test_db, 99999)
        assert fund is None

    def test_get_fund_by_code(self, test_db):
        """测试根据代码获取基金"""
        fund = Fund(fund_code="000001", fund_name="测试基金")
        test_db.add(fund)
        test_db.commit()

        retrieved_fund = crud.get_fund_by_code(test_db, "000001")
        assert retrieved_fund is not None
        assert retrieved_fund.id == fund.id

    def test_create_fund(self, test_db):
        """测试创建基金"""
        fund_data = FundCreate(
            fund_code="000001",
            fund_name="测试基金",
            fund_type="股票型"
        )
        fund = crud.create_fund(test_db, fund_data)

        assert fund.id is not None
        assert fund.fund_code == "000001"
        assert fund.fund_name == "测试基金"
        assert fund.fund_type == "股票型"

    def test_delete_fund(self, test_db):
        """测试删除基金"""
        fund = Fund(fund_code="000001", fund_name="测试基金")
        test_db.add(fund)
        test_db.commit()

        fund_id = fund.id
        result = crud.delete_fund(test_db, fund_id)

        assert result is True
        deleted_fund = crud.get_fund(test_db, fund_id)
        assert deleted_fund is None


class TestFundStockPositionCRUD:
    """测试基金股票持仓 CRUD 操作"""

    def test_get_positions_no_data(self, test_db, sample_fund):
        """测试获取持仓（无数据）"""
        positions = crud.get_fund_stock_positions(test_db, sample_fund.id)
        assert isinstance(positions, list)
        assert len(positions) == 0

    def test_get_positions_no_filter(self, test_db, sample_fund, sample_positions):
        """测试获取持仓（无日期过滤）"""
        # 插入测试数据
        for position_data in sample_positions:
            crud.create_fund_stock_position(test_db, position_data, sample_fund.id)

        positions = crud.get_fund_stock_positions(test_db, sample_fund.id)
        assert len(positions) == len(sample_positions)

    def test_get_positions_with_date_filter(self, test_db, sample_fund):
        """测试获取持仓（带日期过滤）"""
        # 创建不同日期的持仓
        position1 = FundStockPositionCreate(
            stock_code="000001.SZ",
            stock_name="平安银行",
            report_date=date(2024, 3, 31)
        )
        position2 = FundStockPositionCreate(
            stock_code="600000.SH",
            stock_name="浦发银行",
            report_date=date(2024, 6, 30)
        )
        position3 = FundStockPositionCreate(
            stock_code="000002.SZ",
            stock_name="万科A",
            report_date=date(2024, 3, 31)
        )

        crud.create_fund_stock_position(test_db, position1, sample_fund.id)
        crud.create_fund_stock_position(test_db, position2, sample_fund.id)
        crud.create_fund_stock_position(test_db, position3, sample_fund.id)

        # 查询特定日期
        target_date = date(2024, 3, 31)
        positions = crud.get_fund_stock_positions(
            test_db,
            sample_fund.id,
            report_date=target_date
        )

        assert len(positions) == 2
        for pos in positions:
            assert pos.report_date == target_date

    def test_get_positions_ordering(self, test_db, sample_fund):
        """测试持仓按权重降序排列"""
        # 创建不同权重的持仓
        positions_data = [
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

        for position_data in positions_data:
            crud.create_fund_stock_position(test_db, position_data, sample_fund.id)

        positions = crud.get_fund_stock_positions(test_db, sample_fund.id)

        # 验证降序排列
        weights = [pos.weight for pos in positions if pos.weight is not None]
        assert weights == sorted(weights, reverse=True)
        assert weights[0] == Decimal("0.10")
        assert weights[-1] == Decimal("0.03")

    def test_create_fund_stock_position(self, test_db, sample_fund):
        """测试创建单个持仓记录"""
        position_data = FundStockPositionCreate(
            stock_code="000001.SZ",
            stock_name="平安银行",
            shares=Decimal("1000000"),
            market_value=Decimal("50000000"),
            weight=Decimal("0.05"),
            report_date=date(2024, 3, 31)
        )

        position = crud.create_fund_stock_position(
            test_db,
            position_data,
            sample_fund.id
        )

        assert position.id is not None
        assert position.fund_id == sample_fund.id
        assert position.stock_code == "000001.SZ"
        assert position.stock_name == "平安银行"
        assert position.shares == Decimal("1000000")
        assert position.market_value == Decimal("50000000")
        assert position.weight == Decimal("0.05")
        assert position.report_date == date(2024, 3, 31)

    def test_update_positions_insert_new(self, test_db, sample_fund):
        """测试更新持仓（插入新记录）"""
        positions_data = [
            FundStockPositionCreate(
                stock_code="000001.SZ",
                stock_name="平安银行",
                shares=Decimal("1000000"),
                market_value=Decimal("50000000"),
                weight=Decimal("0.05"),
                report_date=date(2024, 3, 31)
            )
        ]

        count = crud.update_fund_stock_positions(test_db, sample_fund.id, positions_data)
        assert count == 1

        # 验证数据已插入
        positions = crud.get_fund_stock_positions(test_db, sample_fund.id)
        assert len(positions) == 1
        assert positions[0].stock_code == "000001.SZ"

    def test_update_positions_replace_existing(self, test_db, sample_fund):
        """测试更新持仓（替换现有记录）"""
        # 插入第一条记录
        positions_data_1 = [
            FundStockPositionCreate(
                stock_code="000001.SZ",
                stock_name="平安银行",
                shares=Decimal("1000000"),
                weight=Decimal("0.05"),
                report_date=date(2024, 3, 31)
            )
        ]
        crud.update_fund_stock_positions(test_db, sample_fund.id, positions_data_1)

        # 验证插入成功
        positions = crud.get_fund_stock_positions(test_db, sample_fund.id)
        assert len(positions) == 1
        assert positions[0].shares == Decimal("1000000")

        # 插入新的数据集（会删除旧数据）
        positions_data_2 = [
            FundStockPositionCreate(
                stock_code="000001.SZ",
                stock_name="平安银行",
                shares=Decimal("2000000"),  # 不同的份额
                weight=Decimal("0.06"),
                report_date=date(2024, 3, 31)
            )
        ]
        count = crud.update_fund_stock_positions(test_db, sample_fund.id, positions_data_2)

        # 应该替换，而不是新增
        assert count == 1
        positions = crud.get_fund_stock_positions(test_db, sample_fund.id)
        assert len(positions) == 1
        assert positions[0].shares == Decimal("2000000")
        assert positions[0].weight == Decimal("0.06")

    def test_update_positions_multiple(self, test_db, sample_fund):
        """测试批量更新多个持仓"""
        # 插入初始数据
        initial_data = [
            FundStockPositionCreate(
                stock_code="000001.SZ",
                stock_name="平安银行",
                weight=Decimal("0.05")
            )
        ]
        crud.update_fund_stock_positions(test_db, sample_fund.id, initial_data)

        # 替换为新的多个持仓
        new_data = [
            FundStockPositionCreate(
                stock_code="600000.SH",
                stock_name="浦发银行",
                weight=Decimal("0.06")
            ),
            FundStockPositionCreate(
                stock_code="000002.SZ",
                stock_name="万科A",
                weight=Decimal("0.04")
            ),
            FundStockPositionCreate(
                stock_code="000001.SZ",
                stock_name="平安银行",
                weight=Decimal("0.05")
            ),
        ]

        count = crud.update_fund_stock_positions(test_db, sample_fund.id, new_data)
        assert count == 3

        # 验证所有数据都被替换
        positions = crud.get_fund_stock_positions(test_db, sample_fund.id)
        assert len(positions) == 3
        stock_codes = {pos.stock_code for pos in positions}
        assert stock_codes == {"600000.SH", "000002.SZ", "000001.SZ"}

    def test_update_positions_empty_list(self, test_db, sample_fund):
        """测试更新持仓（空列表）"""
        # 先插入一些数据
        initial_data = [
            FundStockPositionCreate(
                stock_code="000001.SZ",
                stock_name="平安银行",
                weight=Decimal("0.05")
            )
        ]
        crud.update_fund_stock_positions(test_db, sample_fund.id, initial_data)

        # 验证有数据
        positions = crud.get_fund_stock_positions(test_db, sample_fund.id)
        assert len(positions) == 1

        # 用空列表更新（应该删除所有数据）
        count = crud.update_fund_stock_positions(test_db, sample_fund.id, [])
        assert count == 0

        # 验证数据已被删除
        positions = crud.get_fund_stock_positions(test_db, sample_fund.id)
        assert len(positions) == 0

    def test_update_positions_isolation(self, test_db, sample_funds):
        """测试不同基金的持仓互不影响"""
        fund1, fund2, fund3 = sample_funds

        # 为基金1添加持仓
        positions1 = [
            FundStockPositionCreate(
                stock_code="000001.SZ",
                stock_name="平安银行",
                weight=Decimal("0.05")
            )
        ]
        crud.update_fund_stock_positions(test_db, fund1.id, positions1)

        # 为基金2添加持仓
        positions2 = [
            FundStockPositionCreate(
                stock_code="600000.SH",
                stock_name="浦发银行",
                weight=Decimal("0.06")
            )
        ]
        crud.update_fund_stock_positions(test_db, fund2.id, positions2)

        # 验证各自的数据
        fund1_positions = crud.get_fund_stock_positions(test_db, fund1.id)
        fund2_positions = crud.get_fund_stock_positions(test_db, fund2.id)
        fund3_positions = crud.get_fund_stock_positions(test_db, fund3.id)

        assert len(fund1_positions) == 1
        assert len(fund2_positions) == 1
        assert len(fund3_positions) == 0

        assert fund1_positions[0].stock_code == "000001.SZ"
        assert fund2_positions[0].stock_code == "600000.SH"
