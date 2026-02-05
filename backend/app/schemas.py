from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal


# ==================== Holding Schemas (Moved before Fund Schemas) ====================
class HoldingBase(BaseModel):
    """持仓基础模型"""
    amount: Decimal = Field(..., ge=0, description="持有金额")
    shares: Optional[Decimal] = Field(None, ge=0, description="持有份额（可选，自动计算）")
    cost_price: Optional[Decimal] = Field(None, ge=0, description="成本单价（可选）")


class HoldingCreate(HoldingBase):
    """创建持仓请求"""
    fund_id: int = Field(..., description="基金ID")
    auto_fetch_nav: bool = Field(
        default=False,
        description="是否自动获取净值来计算份额"
    )


class HoldingUpdate(BaseModel):
    """更新持仓请求"""
    amount: Decimal
    shares: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    auto_fetch_nav: bool = Field(default=False)


class HoldingResponse(HoldingBase):
    """持仓响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    fund_id: int
    created_at: datetime
    updated_at: datetime
    cost: Decimal = Field(description="总成本")
    daily_profit_rate: Optional[Decimal] = Field(None, description="今日收益率")
    total_profit_rate: Optional[Decimal] = Field(None, description="整体收益率")


# ==================== Fund Schemas ====================
class FundBase(BaseModel):
    """基金基础模型"""
    fund_code: str = Field(..., max_length=10, description="基金代码")
    fund_name: Optional[str] = Field(None, max_length=100, description="基金名称")
    fund_type: Optional[str] = Field(None, max_length=20, description="基金类型")


class FundCreate(FundBase):
    """创建基金请求"""
    pass


class FundUpdate(BaseModel):
    """更新基金请求"""
    fund_name: Optional[str] = None
    fund_type: Optional[str] = None


class FundInfoResponse(BaseModel):
    """基金信息响应（用于前端自动填充）"""
    fund_code: str
    fund_name: Optional[str] = None
    fund_type: Optional[str] = "开放式基金"
    latest_nav: Optional[float] = 0


class FundResponse(FundBase):
    """基金响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    holdings: Optional[HoldingResponse] = None

    # 股票持仓统计
    stock_positions_count: int = Field(default=0, description="股票持仓数量")
    stock_positions_updated_at: Optional[datetime] = Field(None, description="持仓最后更新时间")


# ==================== NavHistory Schemas ====================
class NavHistoryBase(BaseModel):
    """净值历史基础模型"""
    date: date
    unit_nav: Decimal = Field(..., description="单位净值")
    accumulated_nav: Optional[Decimal] = Field(None, description="累计净值")
    daily_growth: Optional[Decimal] = Field(None, description="日增长率")


class NavHistoryCreate(NavHistoryBase):
    """创建净值历史请求"""
    fund_id: int


class NavHistoryResponse(NavHistoryBase):
    """净值历史响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    fund_id: int
    created_at: datetime


# ==================== DailyPnL Schemas ====================
class DailyPnLBase(BaseModel):
    """每日收益基础模型"""
    date: date
    shares: Decimal
    unit_nav: Decimal
    market_value: Decimal
    cost: Decimal
    profit: Decimal
    profit_rate: Decimal


class DailyPnLCreate(DailyPnLBase):
    """创建每日收益请求"""
    fund_id: int


class DailyPnLResponse(DailyPnLBase):
    """每日收益响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    fund_id: int
    created_at: datetime


# ==================== Summary Schemas ====================
class FundSummary(BaseModel):
    """基金汇总信息"""
    fund_id: int
    fund_code: str
    fund_name: Optional[str]
    amount: Decimal
    shares: Decimal
    cost_price: Decimal
    cost: Decimal
    latest_nav: Optional[Decimal]
    market_value: Optional[Decimal]
    profit: Optional[Decimal]
    profit_rate: Optional[Decimal]


class PortfolioSummary(BaseModel):
    """投资组合汇总"""
    total_cost: Decimal = Field(description="总成本")
    total_market_value: Decimal = Field(description="总市值")
    total_profit: Decimal = Field(description="总收益（实时计算）")
    total_profit_rate: Decimal = Field(description="总收益率（实时计算）")
    cumulative_profit: Optional[Decimal] = Field(None, description="累计总收益（每日收益叠加）")
    daily_profits_history: Optional[list[dict]] = Field(None, description="每日收益历史")
    fund_count: int = Field(description="基金数量")
    funds: list[FundSummary] = Field(description="基金列表")


# ==================== Sync Schemas ====================
class SyncResponse(BaseModel):
    """同步响应"""
    success: bool
    message: str
    funds_updated: int = 0
    errors: list[str] = Field(default_factory=list)


# ==================== Transaction Schemas ====================
class TransactionBase(BaseModel):
    """交易基础模型"""
    transaction_type: str = Field(..., description="交易类型：buy/sell")
    amount: Optional[Decimal] = Field(None, ge=0, description="交易金额（买入必填）")
    shares: Optional[Decimal] = Field(None, ge=0, description="交易份额（卖出可选）")


class TransactionCreate(TransactionBase):
    """创建交易请求"""
    fund_id: int = Field(..., description="基金ID")


class TransactionResponse(TransactionBase):
    """交易响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    fund_id: int
    nav: Decimal
    transaction_date: date
    created_at: datetime


# ==================== Realtime Nav Schemas ====================
class RealtimeNavResponse(BaseModel):
    """实时估值响应（支持场内基金实时股价和场外基金估算涨跌幅）"""
    fund_code: str = Field(..., description="基金代码")

    # 数据源标识
    data_source: Optional[str] = Field(
        None,
        description="数据源: 'stock'表示实时股价, 'estimate'表示估算涨跌幅, 'nav'表示正式净值"
    )
    is_listed_fund: Optional[bool] = Field(
        False,
        description="是否为场内基金（ETF/LOF）"
    )

    # 价格信息（场内基金用）
    current_price: Optional[float] = Field(
        None,
        description="实时股价（场内基金）"
    )

    # 涨跌幅信息（通用）
    increase_rate: Optional[float] = Field(None, description="涨跌幅(%)，场内基金为实际涨跌，场外基金为估算涨跌")

    # 时间信息
    estimate_time: Optional[datetime] = Field(None, description="数据获取时间")
    latest_nav_date: Optional[date] = Field(None, description="最新净值日期")
    latest_nav_unit_nav: Optional[float] = Field(None, description="最新正式单位净值")

    # 交易状态
    is_trading_time: bool = Field(True, description="是否是交易时间")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RealtimeNavItem(BaseModel):
    """单只基金的实时估值项（支持场内和场外基金）"""
    fund_code: str

    # 数据源标识
    data_source: Optional[str] = Field(None, description="数据源: 'stock', 'estimate', 'nav'")
    is_listed_fund: Optional[bool] = Field(False, description="是否为场内基金")

    # 价格信息（场内基金用）
    current_price: Optional[float] = Field(None, description="实时股价（场内基金）")

    # 涨跌幅信息
    increase_rate: Optional[float] = None
    estimate_time: Optional[datetime] = None
    latest_nav_date: Optional[date] = None
    latest_nav_unit_nav: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class BatchRealtimeNavResponse(BaseModel):
    """批量实时估值响应"""
    valuations: List[RealtimeNavItem] = Field(default_factory=list, description="实时估值列表")
    update_time: datetime = Field(description="更新时间")
    is_trading_time: bool = Field(True, description="是否是交易时间")

    model_config = ConfigDict(from_attributes=True)


# ==================== Fund Stock Position Schemas ====================
class FundStockPositionBase(BaseModel):
    """基金股票持仓基础模型"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: Optional[str] = Field(None, description="股票名称")
    shares: Optional[Decimal] = Field(None, description="持仓股数")
    market_value: Optional[Decimal] = Field(None, description="持仓市值(元)")
    weight: Optional[Decimal] = Field(None, ge=0, le=1, description="占基金净值比例(0-1)")
    cost_price: Optional[Decimal] = Field(None, description="成本单价")
    report_date: Optional[date] = Field(None, description="报告期")


class FundStockPositionCreate(FundStockPositionBase):
    """创建基金股票持仓请求"""
    pass


class FundStockPositionResponse(FundStockPositionBase):
    """基金股票持仓响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    fund_id: int
    created_at: datetime
    updated_at: datetime


class StockRealtimeNavResponse(BaseModel):
    """基于股票持仓的基金实时估值响应"""
    fund_code: str = Field(..., description="基金代码")
    realtime_nav: float = Field(..., description="实时估值净值")
    increase_rate: float = Field(..., description="涨跌幅(%)")
    latest_nav: float = Field(..., description="最新正式净值")
    stock_count: int = Field(..., description="持仓股票数")
    update_time: datetime = Field(..., description="更新时间")
    data_source: str = Field(default="tushare_sina", description="数据源标识")

    model_config = ConfigDict(from_attributes=True)
