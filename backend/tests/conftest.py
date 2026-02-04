"""
Pytest 配置和共享 Fixtures

提供测试数据库、测试客户端和测试数据
"""
import pytest
import os
import sys
from typing import Generator
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from datetime import date
from decimal import Decimal

from app.database import Base, get_db
from app.main import app
from app.models import Fund, FundStockPosition
from app.schemas import FundStockPositionCreate
from app import crud

# 测试数据库 URL (使用 SQLite 内存数据库)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    创建测试数据库

    使用 SQLite 内存数据库，每个测试函数独立运行
    """
    from app import database

    # 保存原始引擎和函数
    original_engine = database.engine
    original_session_local = database.SessionLocal
    original_get_db = database.get_db

    # 创建测试引擎
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 替换数据库模块的引擎和 SessionLocal
    database.engine = engine
    database.SessionLocal = TestingSessionLocal

    # 创建新的 get_db 函数
    def test_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    database.get_db = test_get_db

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    yield TestingSessionLocal()

    # 清理：删除所有表
    Base.metadata.drop_all(bind=engine)

    # 恢复原始引擎和函数
    database.engine = original_engine
    database.SessionLocal = original_session_local
    database.get_db = original_get_db


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    创建测试客户端

    使用测试数据库覆盖依赖注入
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # 使用 with 语句确保 TestClient 正确使用依赖覆盖
    with TestClient(app) as test_client:
        yield test_client

    # 清理依赖覆盖
    app.dependency_overrides.clear()


@pytest.fixture
def sample_fund(test_db: Session) -> Fund:
    """
    创建测试基金

    Returns:
        Fund: 测试基金实例
    """
    fund = Fund(
        fund_code="000001",
        fund_name="测试基金",
        fund_type="股票型"
    )
    test_db.add(fund)
    test_db.commit()
    test_db.refresh(fund)
    return fund


@pytest.fixture
def sample_funds(test_db: Session) -> list[Fund]:
    """
    创建多个测试基金

    Returns:
        list[Fund]: 测试基金列表
    """
    funds = [
        Fund(fund_code="000001", fund_name="华夏成长混合", fund_type="混合型"),
        Fund(fund_code="110022", fund_name="易方达消费行业", fund_type="股票型"),
        Fund(fund_code="163406", fund_name="兴全合润分级", fund_type="混合型"),
    ]
    for fund in funds:
        test_db.add(fund)
    test_db.commit()

    # 刷新所有基金
    for fund in funds:
        test_db.refresh(fund)

    return funds


@pytest.fixture
def sample_positions() -> list[FundStockPositionCreate]:
    """
    创建测试持仓数据

    Returns:
        list[FundStockPositionCreate]: 测试持仓数据列表
    """
    return [
        FundStockPositionCreate(
            stock_code="000001.SZ",
            stock_name="平安银行",
            shares=Decimal("1000000"),
            market_value=Decimal("50000000"),
            weight=Decimal("0.05"),
            report_date=date(2024, 3, 31)
        ),
        FundStockPositionCreate(
            stock_code="600000.SH",
            stock_name="浦发银行",
            shares=Decimal("1500000"),
            market_value=Decimal("55000000"),
            weight=Decimal("0.055"),
            report_date=date(2024, 3, 31)
        ),
        FundStockPositionCreate(
            stock_code="000002.SZ",
            stock_name="万科A",
            shares=Decimal("2000000"),
            market_value=Decimal("40000000"),
            weight=Decimal("0.04"),
            report_date=date(2024, 3, 31)
        ),
    ]


@pytest.fixture
def sample_positions_with_invalid() -> list[FundStockPositionCreate]:
    """
    创建包含无效股票代码的测试数据（用于验证过滤逻辑）

    Returns:
        list[FundStockPositionCreate]: 包含有效和无效数据的列表
    """
    return [
        FundStockPositionCreate(
            stock_code="000001.OF",  # 无效：基金代码
            stock_name="伪装成股票的基金",
            shares=Decimal("1000000"),
            weight=Decimal("0.05"),
            report_date=date(2024, 3, 31)
        ),
        FundStockPositionCreate(
            stock_code="INVALID",  # 无效：缺少后缀
            stock_name="无效代码",
            shares=Decimal("1000000"),
            weight=Decimal("0.05"),
            report_date=date(2024, 3, 31)
        ),
        FundStockPositionCreate(
            stock_code="000001.SZ",  # 有效
            stock_name="平安银行",
            shares=Decimal("1000000"),
            weight=Decimal("0.05"),
            report_date=date(2024, 3, 31)
        ),
        FundStockPositionCreate(
            stock_code="600000.SH",  # 有效
            stock_name="浦发银行",
            shares=Decimal("1500000"),
            weight=Decimal("0.055"),
            report_date=date(2024, 3, 31)
        ),
    ]


@pytest.fixture
def sample_fund_with_positions(test_db: Session, sample_fund: Fund, sample_positions: list[FundStockPositionCreate]) -> Fund:
    """
    创建带有持仓的测试基金

    Args:
        test_db: 测试数据库会话
        sample_fund: 测试基金
        sample_positions: 测试持仓数据

    Returns:
        Fund: 带有持仓的基金
    """
    for position_data in sample_positions:
        position = FundStockPosition(
            fund_id=sample_fund.id,
            **position_data.model_dump()
        )
        test_db.add(position)
    test_db.commit()
    return sample_fund


# 环境变量设置
@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """
    自动设置测试环境变量

    autouse=True 表示自动应用于所有测试
    """
    monkeypatch.setenv("TUSHARE_TOKEN", "test_token_12345")
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)


# pytest 配置
def pytest_configure(config):
    """Pytest 初始化配置"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
