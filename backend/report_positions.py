"""
生成持仓数据报告
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import FundStockPosition, Fund
from sqlalchemy import func

db = SessionLocal()

print("\n" + "="*80)
print(" "*20 + "基金持仓数据统计报告")
print("="*80)

# 总体统计
total_positions = db.query(FundStockPosition).count()
total_funds = db.query(Fund).count()
funds_with_positions = db.query(Fund).join(FundStockPosition).distinct().count()

print(f"\n[总体统计]")
print(f"  总基金数: {total_funds}")
print(f"  有持仓的基金: {funds_with_positions}")
print(f"  总持仓记录: {total_positions}")
print(f"  平均每只基金持仓: {total_positions // funds_with_positions if funds_with_positions > 0 else 0} 条")

# 按基金统计持仓数量
print(f"\n[按基金统计持仓数量 (Top 15)]")
funds = db.query(
    Fund.fund_code,
    Fund.fund_name,
    func.count(FundStockPosition.id).label('count')
).outerjoin(FundStockPosition)\
 .group_by(Fund.id)\
 .order_by(func.count(FundStockPosition.id).desc())\
 .limit(15)\
 .all()

print(f"  {'基金代码':<10} {'基金名称':<40} {'持仓数量':>10}")
print("  " + "-"*70)
for fund in funds:
    print(f"  {fund[0]:<10} {fund[1]:<40} {fund[2]:>10}")

# 各基金的前5大持仓
print(f"\n[各基金前5大持仓]")
funds_with_data = db.query(Fund).join(FundStockPosition).distinct().limit(10).all()

for fund in funds_with_data:
    top_positions = db.query(FundStockPosition)\
        .filter(FundStockPosition.fund_id == fund.id)\
        .order_by(FundStockPosition.weight.desc())\
        .limit(5)\
        .all()

    if top_positions:
        print(f"\n  {fund.fund_code} - {fund.fund_name}")
        for idx, pos in enumerate(top_positions, 1):
            weight_str = f"{pos.weight*100:.2f}%" if pos.weight else "N/A"
            print(f"    {idx}. {pos.stock_code:<10} {pos.stock_name:<15} 权重:{weight_str:<8} 份额:{int(pos.shares) if pos.shares else 0:>12,}")

# 持仓最多的股票
print(f"\n[持仓最多的股票 (Top 10)]")
stocks = db.query(
    FundStockPosition.stock_code,
    FundStockPosition.stock_name,
    func.count(FundStockPosition.id).label('fund_count'),
    func.sum(FundStockPosition.weight).label('total_weight')
).group_by(
    FundStockPosition.stock_code,
    FundStockPosition.stock_name
).order_by(
    func.count(FundStockPosition.id).desc()
).limit(10).all()

print(f"  {'股票代码':<10} {'股票名称':<15} {'出现次数':>10} {'总权重':>10}")
print("  " + "-"*50)
for stock in stocks:
    total_weight_str = f"{stock[3]*100:.2f}%" if stock[3] else "N/A"
    print(f"  {stock[0]:<10} {stock[1]:<15} {stock[2]:>10} {total_weight_str:>10}")

print("\n" + "="*80)

db.close()
