"""测试 efinance 基金数据获取"""
import efinance as ef

print("=" * 50)
print("测试 efinance 基金数据获取")
print("=" * 50)

# 测试基金代码
fund_codes = ["023754", "000001", "110022"]

for fund_code in fund_codes:
    print(f"\n--- 测试基金代码: {fund_code} ---")

    # 1. 获取基金基本信息
    try:
        fund_info = ef.fund.get_fund_base_info(market=0, fund_code=fund_code)
        print(f"基金基本信息: {fund_info.shape if fund_info is not None else 'None'}")
        if fund_info is not None and not fund_info.empty:
            print(fund_info.head())
    except Exception as e:
        print(f"获取基金信息失败: {e}")

    # 2. 获取基金实时行情
    try:
        quote = ef.fund.get_fund_quote(fund_code)
        print(f"基金行情: {quote.shape if quote is not None else 'None'}")
        if quote is not None and not quote.empty:
            print(quote.head())
            print(f"列名: {list(quote.columns)}")
    except Exception as e:
        print(f"获取基金行情失败: {e}")

    # 3. 获取历史净值
    try:
        history = ef.fund.get_fund_history(
            fund_code=fund_code,
            begin_date="20240101",
            end_date="20250101"
        )
        print(f"历史净值: {history.shape if history is not None else 'None'}")
        if history is not None and not history.empty:
            print(history.head())
            print(f"列名: {list(history.columns)}")
    except Exception as e:
        print(f"获取历史净值失败: {e}")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)
