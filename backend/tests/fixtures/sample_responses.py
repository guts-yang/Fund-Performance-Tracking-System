"""
测试数据生成器和示例响应

提供标准化的测试数据用于各个测试模块
"""
import pandas as pd
from datetime import date
from decimal import Decimal

from app.schemas import FundStockPositionCreate


# ==================== API 响应示例 ====================

class SampleAPIResponses:
    """示例 API 响应数据"""

    @staticmethod
    def tushare_success_response() -> dict:
        """Tushare 成功响应"""
        return {
            "success": True,
            "message": "成功同步 3 条持仓记录",
            "funds_updated": 3,
            "errors": []
        }

    @staticmethod
    def tushare_empty_response() -> dict:
        """Tushare 空数据响应"""
        return {
            "success": False,
            "message": "无法获取基金的持仓数据",
            "funds_updated": 0,
            "errors": ["Tushare API 返回空数据"]
        }

    @staticmethod
    def tushare_error_response() -> dict:
        """Tushare 错误响应"""
        return {
            "success": False,
            "message": "同步失败: API error",
            "funds_updated": 0,
            "errors": ["API error"]
        }


# ==================== DataFrame 示例 ====================

class SampleDataFrames:
    """示例 DataFrame 数据"""

    @staticmethod
    def standard_positions() -> pd.DataFrame:
        """标准持仓数据"""
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
    def positions_with_fund_code() -> pd.DataFrame:
        """包含基金代码的数据（用于测试过滤）"""
        return pd.DataFrame({
            'ts_code': ['000001.OF', '000001.OF', '000001.OF'],
            'symbol': ['000001.OF', '000001.SZ', '600000.SH'],
            'name': ['伪装成股票', '平安银行', '浦发银行'],
            'amount': [1000000, 1000000, 1500000],
            'mkv': [50000000, 50000000, 55000000],
            'stk_mkv_ratio': [5.0, 5.0, 5.5],
            'end_date': ['20240331', '20240331', '20240331']
        })

    @staticmethod
    def positions_with_null_values() -> pd.DataFrame:
        """包含空值的数据"""
        return pd.DataFrame({
            'ts_code': ['000001.OF', '000001.OF', '000001.OF'],
            'symbol': ['000001.SZ', None, '600000.SH'],
            'name': ['平安银行', None, '浦发银行'],
            'amount': [1000000, None, 1500000],
            'mkv': [50000000, None, 55000000],
            'stk_mkv_ratio': [5.0, None, 5.5],
            'end_date': ['20240331', None, '20240331']
        })

    @staticmethod
    def empty_positions() -> pd.DataFrame:
        """空数据"""
        return pd.DataFrame()

    @staticmethod
    def large_positions(count: int = 50) -> pd.DataFrame:
        """生成大量持仓数据"""
        symbols = [f"{str(i).zfill(6)}.SZ" for i in range(1, count + 1)]
        names = [f"股票{i}" for i in range(1, count + 1)]
        amounts = [1000000 * i for i in range(1, count + 1)]
        mkvs = [50000000 * i for i in range(1, count + 1)]
        ratios = [5.0 + i * 0.1 for i in range(count)]

        return pd.DataFrame({
            'ts_code': ['000001.OF'] * count,
            'symbol': symbols,
            'name': names,
            'amount': amounts,
            'mkv': mkvs,
            'stk_mkv_ratio': ratios,
            'end_date': ['20240331'] * count
        })


# ==================== 测试数据生成器 ====================

class TestDataGenerator:
    """测试数据生成器"""

    @staticmethod
    def create_position(
        stock_code: str = "000001.SZ",
        stock_name: str = "平安银行",
        shares: str = "1000000",
        market_value: str = "50000000",
        weight: str = "0.05",
        report_date: date = None
    ) -> FundStockPositionCreate:
        """创建单个持仓数据"""
        if report_date is None:
            report_date = date(2024, 3, 31)

        return FundStockPositionCreate(
            stock_code=stock_code,
            stock_name=stock_name,
            shares=Decimal(shares),
            market_value=Decimal(market_value),
            weight=Decimal(weight),
            report_date=report_date
        )

    @staticmethod
    def create_standard_positions() -> list[FundStockPositionCreate]:
        """创建标准持仓列表"""
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
                stock_code="000002.SZ",
                stock_name="万科A",
                shares=Decimal("2000000"),
                market_value=Decimal("60000000"),
                weight=Decimal("0.06"),
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
        ]

    @staticmethod
    def create_positions_with_invalid_codes() -> list[FundStockPositionCreate]:
        """创建包含无效代码的持仓列表"""
        return [
            FundStockPositionCreate(
                stock_code="000001.OF",
                stock_name="伪装成股票",
                shares=Decimal("1000000"),
                weight=Decimal("0.05"),
                report_date=date(2024, 3, 31)
            ),
            FundStockPositionCreate(
                stock_code="INVALID",
                stock_name="无效代码",
                shares=Decimal("1000000"),
                weight=Decimal("0.05"),
                report_date=date(2024, 3, 31)
            ),
            FundStockPositionCreate(
                stock_code="000001.SZ",
                stock_name="平安银行",
                shares=Decimal("1000000"),
                weight=Decimal("0.05"),
                report_date=date(2024, 3, 31)
            ),
        ]

    @staticmethod
    def create_boundary_positions() -> list[FundStockPositionCreate]:
        """创建边界值测试数据"""
        return [
            # 零权重
            FundStockPositionCreate(
                stock_code="000001.SZ",
                stock_name="平安银行",
                weight=Decimal("0"),
                report_date=date(2024, 3, 31)
            ),
            # 最大权重
            FundStockPositionCreate(
                stock_code="600000.SH",
                stock_name="浦发银行",
                weight=Decimal("1"),
                report_date=date(2024, 3, 31)
            ),
            # 零份额
            FundStockPositionCreate(
                stock_code="000002.SZ",
                stock_name="万科A",
                shares=Decimal("0"),
                report_date=date(2024, 3, 31)
            ),
            # 零市值
            FundStockPositionCreate(
                stock_code="000003.SZ",
                stock_name="测试股票",
                market_value=Decimal("0"),
                report_date=date(2024, 3, 31)
            ),
        ]


# ==================== 常用测试数据 ====================

# 常用股票代码
VALID_STOCK_CODES = [
    "000001.SZ",  # 平安银行
    "000002.SZ",  # 万科A
    "600000.SH",  # 浦发银行
    "600036.SH",  # 招商银行
    "601318.SH",  # 中国平安
]

# 无效股票代码（用于测试过滤）
INVALID_STOCK_CODES = [
    "000001.OF",  # 基金代码
    "INVALID",    # 无格式
    "",           # 空字符串
]

# 常用报告期
REPORT_DATES = [
    date(2024, 3, 31),  # 一季度
    date(2024, 6, 30),  # 二季度
    date(2024, 9, 30),  # 三季度
    date(2024, 12, 31), # 四季度
]
