from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from . import models
from .schemas import (
    FundCreate, FundUpdate, HoldingCreate, HoldingUpdate,
    NavHistoryCreate, DailyPnLCreate, FundStockPositionCreate
)
from .services.fund_fetcher import FundDataFetcher


# ==================== Fund CRUD ====================
def get_fund(db: Session, fund_id: int) -> Optional[models.Fund]:
    """获取单个基金"""
    return db.query(models.Fund).filter(models.Fund.id == fund_id).first()


def get_fund_by_code(db: Session, fund_code: str) -> Optional[models.Fund]:
    """根据基金代码获取基金"""
    return db.query(models.Fund).filter(models.Fund.fund_code == fund_code).first()


def get_funds_by_codes(db: Session, fund_codes: List[str]) -> List[models.Fund]:
    """根据基金代码列表批量获取基金"""
    return db.query(models.Fund).filter(models.Fund.fund_code.in_(fund_codes)).all()


def get_funds(db: Session, skip: int = 0, limit: int = 100) -> List[models.Fund]:
    """获取基金列表（包含持仓）"""
    from sqlalchemy.orm import joinedload
    return db.query(models.Fund)\
        .options(joinedload(models.Fund.holdings))\
        .offset(skip)\
        .limit(limit)\
        .all()


def create_fund(db: Session, fund: FundCreate) -> models.Fund:
    """创建基金"""
    db_fund = models.Fund(
        fund_code=fund.fund_code,
        fund_name=fund.fund_name,
        fund_type=fund.fund_type
    )
    db.add(db_fund)
    db.commit()
    db.refresh(db_fund)
    return db_fund


def update_fund(db: Session, fund_id: int, fund: FundUpdate) -> Optional[models.Fund]:
    """更新基金"""
    db_fund = get_fund(db, fund_id)
    if db_fund:
        if fund.fund_name is not None:
            db_fund.fund_name = fund.fund_name
        if fund.fund_type is not None:
            db_fund.fund_type = fund.fund_type
        db.commit()
        db.refresh(db_fund)
    return db_fund


def delete_fund(db: Session, fund_id: int) -> bool:
    """删除基金"""
    db_fund = get_fund(db, fund_id)
    if db_fund:
        db.delete(db_fund)
        db.commit()
        return True
    return False


# ==================== Holding CRUD ====================
def get_holding(db: Session, fund_id: int) -> Optional[models.Holding]:
    """获取基金持仓"""
    return db.query(models.Holding).filter(models.Holding.fund_id == fund_id).first()


def get_holdings(db: Session, skip: int = 0, limit: int = 100) -> List[models.Holding]:
    """获取所有持仓"""
    return db.query(models.Holding).offset(skip).limit(limit).all()


def create_or_update_holding(db: Session, holding: HoldingCreate) -> models.Holding:
    """创建或更新持仓"""
    db_holding = get_holding(db, holding.fund_id)

    if db_holding:
        # Update existing
        db_holding.amount = holding.amount
        if holding.shares is not None:
            db_holding.shares = holding.shares
        if holding.cost_price is not None:
            db_holding.cost_price = holding.cost_price
    else:
        # Create new
        db_holding = models.Holding(
            fund_id=holding.fund_id,
            amount=holding.amount,
            shares=holding.shares or Decimal("0"),
            cost_price=holding.cost_price or Decimal("0")
        )
        db.add(db_holding)

    db.commit()
    db.refresh(db_holding)
    return db_holding


def update_holding(db: Session, fund_id: int, holding: HoldingUpdate) -> Optional[models.Holding]:
    """更新持仓"""
    db_holding = get_holding(db, fund_id)
    if db_holding:
        db_holding.amount = holding.amount
        if holding.shares is not None:
            db_holding.shares = holding.shares
        if holding.cost_price is not None:
            db_holding.cost_price = holding.cost_price
        db.commit()
        db.refresh(db_holding)
    return db_holding


def delete_holding(db: Session, fund_id: int) -> bool:
    """删除持仓"""
    db_holding = get_holding(db, fund_id)
    if db_holding:
        db.delete(db_holding)
        db.commit()
        return True
    return False


# ==================== NavHistory CRUD ====================
def get_latest_nav(db: Session, fund_id: int) -> Optional[models.NavHistory]:
    """获取最新净值"""
    return db.query(models.NavHistory).filter(
        models.NavHistory.fund_id == fund_id
    ).order_by(desc(models.NavHistory.date)).first()


def get_nav_history(db: Session, fund_id: int, start_date: Optional[date] = None,
                    end_date: Optional[date] = None, limit: int = 100) -> List[models.NavHistory]:
    """获取净值历史"""
    query = db.query(models.NavHistory).filter(models.NavHistory.fund_id == fund_id)

    if start_date:
        query = query.filter(models.NavHistory.date >= start_date)
    if end_date:
        query = query.filter(models.NavHistory.date <= end_date)

    return query.order_by(desc(models.NavHistory.date)).limit(limit).all()


def create_nav_history(db: Session, nav: NavHistoryCreate) -> models.NavHistory:
    """创建净值记录"""
    db_nav = models.NavHistory(
        fund_id=nav.fund_id,
        date=nav.date,
        unit_nav=nav.unit_nav,
        accumulated_nav=nav.accumulated_nav,
        daily_growth=nav.daily_growth
    )
    db.add(db_nav)
    db.commit()
    db.refresh(db_nav)
    return db_nav


def upsert_nav_history(db: Session, fund_id: int, date: date, unit_nav: Decimal,
                       accumulated_nav: Optional[Decimal] = None,
                       daily_growth: Optional[Decimal] = None) -> models.NavHistory:
    """创建或更新净值记录"""
    db_nav = db.query(models.NavHistory).filter(
        and_(models.NavHistory.fund_id == fund_id, models.NavHistory.date == date)
    ).first()

    if db_nav:
        db_nav.unit_nav = unit_nav
        if accumulated_nav is not None:
            db_nav.accumulated_nav = accumulated_nav
        if daily_growth is not None:
            db_nav.daily_growth = daily_growth
    else:
        db_nav = models.NavHistory(
            fund_id=fund_id,
            date=date,
            unit_nav=unit_nav,
            accumulated_nav=accumulated_nav or Decimal("0"),
            daily_growth=daily_growth or Decimal("0")
        )
        db.add(db_nav)

    db.commit()
    db.refresh(db_nav)
    return db_nav


# ==================== DailyPnL CRUD ====================
def get_daily_pnl(db: Session, fund_id: int, pnl_date: date) -> Optional[models.DailyPnL]:
    """获取指定日期收益"""
    return db.query(models.DailyPnL).filter(
        and_(models.DailyPnL.fund_id == fund_id, models.DailyPnL.date == pnl_date)
    ).first()


def get_daily_pnl_history(db: Session, fund_id: int, limit: int = 30) -> List[models.DailyPnL]:
    """获取收益历史"""
    return db.query(models.DailyPnL).filter(
        models.DailyPnL.fund_id == fund_id
    ).order_by(desc(models.DailyPnL.date)).limit(limit).all()


def create_or_update_daily_pnl(db: Session, pnl: DailyPnLCreate) -> models.DailyPnL:
    """创建或更新每日收益"""
    db_pnl = db.query(models.DailyPnL).filter(
        and_(models.DailyPnL.fund_id == pnl.fund_id, models.DailyPnL.date == pnl.date)
    ).first()

    if db_pnl:
        db_pnl.shares = pnl.shares
        db_pnl.unit_nav = pnl.unit_nav
        db_pnl.market_value = pnl.market_value
        db_pnl.cost = pnl.cost
        db_pnl.profit = pnl.profit
        db_pnl.profit_rate = pnl.profit_rate
    else:
        db_pnl = models.DailyPnL(
            fund_id=pnl.fund_id,
            date=pnl.date,
            shares=pnl.shares,
            unit_nav=pnl.unit_nav,
            market_value=pnl.market_value,
            cost=pnl.cost,
            profit=pnl.profit,
            profit_rate=pnl.profit_rate
        )
        db.add(db_pnl)

    db.commit()
    db.refresh(db_pnl)
    return db_pnl


# ==================== Sync Functions ====================
def sync_fund_data(db: Session, fund_id: int) -> Optional[models.NavHistory]:
    """同步基金数据"""
    fund = get_fund(db, fund_id)
    if not fund:
        return None

    fetcher = FundDataFetcher()
    nav_data = fetcher.get_fund_nav(fund.fund_code)

    if nav_data:
        # Update fund info if needed
        if not fund.fund_name:
            fund.fund_name = f"基金{fund.fund_code}"

        # Save nav history
        nav_record = upsert_nav_history(
            db=db,
            fund_id=fund_id,
            date=nav_data["date"],
            unit_nav=nav_data["unit_nav"],
            accumulated_nav=nav_data.get("accumulated_nav"),
            daily_growth=nav_data.get("daily_growth")
        )

        # Calculate daily PnL if holding exists
        holding = get_holding(db, fund_id)
        if holding and holding.shares > 0:
            calculate_daily_pnl(db, fund_id, holding)

        return nav_record

    return None


def calculate_daily_pnl(db: Session, fund_id: int, holding: models.Holding) -> Optional[models.DailyPnL]:
    """计算每日收益"""
    latest_nav = get_latest_nav(db, fund_id)
    if not latest_nav:
        return None

    market_value = holding.shares * latest_nav.unit_nav
    cost = holding.cost
    profit = market_value - cost
    profit_rate = (profit / cost * 100) if cost > 0 else Decimal("0")

    pnl = create_or_update_daily_pnl(
        db=db,
        pnl=DailyPnLCreate(
            fund_id=fund_id,
            date=latest_nav.date,
            shares=holding.shares,
            unit_nav=latest_nav.unit_nav,
            market_value=market_value,
            cost=cost,
            profit=profit,
            profit_rate=profit_rate
        )
    )

    return pnl


def get_portfolio_summary(db: Session) -> dict:
    """获取投资组合汇总（包含当日收益）"""
    holdings = get_holdings(db)

    total_cost = Decimal("0")
    total_market_value = Decimal("0")
    total_daily_profit = Decimal("0")  # 新增：当日收益
    fund_summaries = []

    for holding in holdings:
        cost = holding.cost
        total_cost += cost

        latest_nav = get_latest_nav(db, holding.fund_id)
        if latest_nav and holding.shares > 0:
            market_value = holding.shares * latest_nav.unit_nav
        else:
            market_value = holding.amount

        total_market_value += market_value

        profit = market_value - cost
        profit_rate = (profit / cost * 100) if cost > 0 else Decimal("0")

        # 计算当日收益
        daily_pnl = get_daily_pnl(db, holding.fund_id, latest_nav.date) if latest_nav else None
        daily_profit = daily_pnl.profit if daily_pnl else Decimal("0")
        total_daily_profit += daily_profit

        fund_summaries.append({
            "fund_id": holding.fund_id,
            "fund_code": holding.fund.fund_code,
            "fund_name": holding.fund.fund_name,
            "amount": holding.amount,
            "shares": holding.shares,
            "cost_price": holding.cost_price,
            "cost": cost,
            "latest_nav": latest_nav.unit_nav if latest_nav else None,
            "market_value": market_value,
            "profit": profit,
            "profit_rate": profit_rate,
            "daily_profit": daily_profit  # 新增：当日收益
        })

    total_profit = total_market_value - total_cost
    total_profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else Decimal("0")

    return {
        "total_cost": total_cost,
        "total_market_value": total_market_value,
        "total_profit": total_profit,
        "total_profit_rate": total_profit_rate,
        "total_daily_profit": total_daily_profit,  # 新增：当日总收益
        "fund_count": len(holdings),
        "funds": fund_summaries
    }


def sync_all_funds(db: Session) -> dict:
    """同步所有基金数据"""
    funds = get_funds(db)
    updated_count = 0
    errors = []

    for fund in funds:
        try:
            result = sync_fund_data(db, fund.id)
            if result:
                updated_count += 1
        except Exception as e:
            errors.append(f"基金 {fund.fund_code}: {str(e)}")

    return {
        "updated_count": updated_count,
        "total_count": len(funds),
        "errors": errors
    }


# ==================== Transaction CRUD ====================
def get_transactions(db: Session, fund_id: int, skip: int = 0, limit: int = 100) -> List[models.Transaction]:
    """获取基金交易历史"""
    return db.query(models.Transaction)\
        .filter(models.Transaction.fund_id == fund_id)\
        .order_by(desc(models.Transaction.transaction_date))\
        .offset(skip)\
        .limit(limit)\
        .all()


def execute_buy_transaction(db: Session, fund_id: int, amount: Decimal) -> models.Transaction:
    """执行买入交易"""
    from .services.fund_fetcher import FundDataFetcher

    # 获取基金信息
    fund = get_fund(db, fund_id)
    if not fund:
        raise ValueError(f"基金 ID {fund_id} 不存在")

    # 获取当日净值
    fetcher = FundDataFetcher()
    nav_data = fetcher.get_fund_nav(fund.fund_code)

    if not nav_data or not nav_data.get("unit_nav"):
        raise ValueError("无法获取基金净值")

    nav = nav_data["unit_nav"]
    transaction_date = nav_data["date"]

    # 计算买入份额
    shares = (amount / nav).quantize(Decimal("0.0001"))

    # 创建交易记录
    transaction = models.Transaction(
        fund_id=fund_id,
        transaction_type="buy",
        amount=amount,
        shares=shares,
        nav=nav,
        transaction_date=transaction_date
    )
    db.add(transaction)

    # 更新持仓
    holding = get_holding(db, fund_id)
    if holding:
        # 更新现有持仓
        holding.amount += amount
        holding.shares += shares
        holding.cost_price = nav  # 覆盖为当日净值
    else:
        # 创建新持仓
        holding = models.Holding(
            fund_id=fund_id,
            amount=amount,
            shares=shares,
            cost_price=nav
        )
        db.add(holding)

    db.commit()
    db.refresh(transaction)
    return transaction


def execute_sell_transaction(db: Session, fund_id: int, amount: Optional[Decimal] = None, shares: Optional[Decimal] = None) -> models.Transaction:
    """执行卖出交易"""
    from .services.fund_fetcher import FundDataFetcher

    # 获取持仓
    holding = get_holding(db, fund_id)
    if not holding:
        raise ValueError(f"基金 ID {fund_id} 没有持仓")

    # 获取当日净值
    fund = get_fund(db, fund_id)
    fetcher = FundDataFetcher()
    nav_data = fetcher.get_fund_nav(fund.fund_code)

    if not nav_data or not nav_data.get("unit_nav"):
        raise ValueError("无法获取基金净值")

    nav = nav_data["unit_nav"]
    transaction_date = nav_data["date"]

    # 根据输入计算卖出金额和份额
    if shares and not amount:
        # 输入了份额，计算金额
        amount = (shares * nav).quantize(Decimal("0.01"))
    elif amount and not shares:
        # 输入了金额，计算份额
        shares = (amount / nav).quantize(Decimal("0.0001"))
    else:
        raise ValueError("必须且只能输入卖出金额或卖出份额之一")

    # 验证份额是否足够
    if shares > holding.shares:
        raise ValueError(f"持仓份额不足，当前持有 {holding.shares} 份，尝试卖出 {shares} 份")

    # 创建交易记录
    transaction = models.Transaction(
        fund_id=fund_id,
        transaction_type="sell",
        amount=amount,
        shares=shares,
        nav=nav,
        transaction_date=transaction_date
    )
    db.add(transaction)

    # 更新持仓（成本价保持不变）
    holding.amount -= amount
    holding.shares -= shares
    # cost_price 保持不变

    db.commit()
    db.refresh(transaction)
    return transaction


# ==================== Fund Stock Position CRUD ====================

def get_fund_stock_positions(
    db: Session,
    fund_id: int,
    report_date: Optional[date] = None
) -> List[models.FundStockPosition]:
    """获取基金股票持仓列表"""
    query = db.query(models.FundStockPosition).filter(
        models.FundStockPosition.fund_id == fund_id
    )

    if report_date:
        query = query.filter(models.FundStockPosition.report_date == report_date)

    return query.order_by(models.FundStockPosition.weight.desc()).all()


def create_fund_stock_position(
    db: Session,
    position: FundStockPositionCreate,
    fund_id: int
) -> models.FundStockPosition:
    """创建单个基金股票持仓记录"""
    db_position = models.FundStockPosition(
        fund_id=fund_id,
        **position.model_dump()
    )
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position


def update_fund_stock_positions(
    db: Session,
    fund_id: int,
    positions: List[FundStockPositionCreate]
) -> int:
    """
    批量更新基金股票持仓

    先删除该基金的所有持仓记录，然后插入新数据
    """
    # 删除旧数据
    db.query(models.FundStockPosition).filter(
        models.FundStockPosition.fund_id == fund_id
    ).delete()

    # 插入新数据
    count = 0
    for position in positions:
        db_position = models.FundStockPosition(
            fund_id=fund_id,
            **position.model_dump()
        )
        db.add(db_position)
        count += 1

    db.commit()
    return count
