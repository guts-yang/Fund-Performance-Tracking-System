from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from decimal import Decimal
from .database import Base


class Fund(Base):
    """基金信息表"""
    __tablename__ = "funds"

    id = Column(Integer, primary_key=True, index=True)
    fund_code = Column(String(10), unique=True, nullable=False, index=True, comment="基金代码")
    fund_name = Column(String(100), comment="基金名称")
    fund_type = Column(String(20), comment="基金类型")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # Relationships
    holdings = relationship("Holding", back_populates="fund", uselist=False, cascade="all, delete-orphan")
    nav_history = relationship("NavHistory", back_populates="fund", cascade="all, delete-orphan")
    daily_pnl = relationship("DailyPnL", back_populates="fund", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Fund(id={self.id}, code={self.fund_code}, name={self.fund_name})>"


class Holding(Base):
    """持仓信息表"""
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, unique=True, comment="基金ID")
    amount = Column(Numeric(15, 2), nullable=False, default=0, comment="持有金额")
    shares = Column(Numeric(15, 4), nullable=False, default=0, comment="持有份额")
    cost_price = Column(Numeric(10, 4), nullable=False, default=0, comment="成本单价")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # Relationships
    fund = relationship("Fund", back_populates="holdings")

    @property
    def cost(self) -> Decimal:
        """总成本 = 份额 * 成本单价"""
        if self.shares and self.cost_price:
            return self.shares * self.cost_price
        return Decimal("0")

    def __repr__(self):
        return f"<Holding(id={self.id}, fund_id={self.fund_id}, amount={self.amount})>"


class NavHistory(Base):
    """净值历史表"""
    __tablename__ = "nav_history"

    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, comment="基金ID")
    date = Column(Date, nullable=False, comment="净值日期")
    unit_nav = Column(Numeric(10, 4), nullable=False, comment="单位净值")
    accumulated_nav = Column(Numeric(10, 4), comment="累计净值")
    daily_growth = Column(Numeric(8, 4), comment="日增长率")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # Relationships
    fund = relationship("Fund", back_populates="nav_history")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('fund_id', 'date', name='unique_fund_date'),
    )

    def __repr__(self):
        return f"<NavHistory(id={self.id}, fund_id={self.fund_id}, date={self.date}, nav={self.unit_nav})>"


class DailyPnL(Base):
    """每日收益表"""
    __tablename__ = "daily_pnl"

    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, comment="基金ID")
    date = Column(Date, nullable=False, comment="日期")
    shares = Column(Numeric(15, 4), nullable=False, default=0, comment="当日份额")
    unit_nav = Column(Numeric(10, 4), nullable=False, comment="当日净值")
    market_value = Column(Numeric(15, 2), nullable=False, default=0, comment="市值")
    cost = Column(Numeric(15, 2), nullable=False, default=0, comment="成本")
    profit = Column(Numeric(15, 2), nullable=False, default=0, comment="收益")
    profit_rate = Column(Numeric(8, 4), nullable=False, default=0, comment="收益率")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # Relationships
    fund = relationship("Fund", back_populates="daily_pnl")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('fund_id', 'date', name='unique_fund_pnl_date'),
    )

    def __repr__(self):
        return f"<DailyPnL(id={self.id}, fund_id={self.fund_id}, date={self.date}, profit={self.profit})>"
