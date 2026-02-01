"""探索 efinance 的正确 API"""
import efinance as ef

print("=" * 60)
print("探索 efinance.fund 模块的所有函数")
print("=" * 60)

# 获取 fund 模块的所有属性
fund_attrs = [attr for attr in dir(ef.fund) if not attr.startswith('_')]
print(f"\nefinance.fund 可用函数 ({len(fund_attrs)} 个):")
for i, attr in enumerate(fund_attrs, 1):
    print(f"{i:3d}. {attr}")

# 尝试获取基金代码 023754 的数据
fund_code = "023754"
print(f"\n{'='*60}")
print(f"测试获取基金 {fund_code} 的数据")
print(f"{'='*60}")

# 尝试不同的函数
test_funcs = [
    'get_fund_info',
    'get_fund_hist',
    'get_fund_hist_em',
    'get_base_info',
    'get_all_base_info',
    'get_quote',
    'get_quote_history',
]

for func_name in test_funcs:
    if func_name in fund_attrs:
        print(f"\n--- 尝试: ef.fund.{func_name} ---")
        try:
            func = getattr(ef.fund, func_name)
            # 尝试调用
            result = func(fund_code)
            print(f"成功! 返回类型: {type(result)}")
            if result is not None:
                import pandas as pd
                if isinstance(result, pd.DataFrame):
                    print(f"形状: {result.shape}")
                    if not result.empty:
                        print(f"列名: {list(result.columns)}")
                        print(result.head())
                else:
                    print(f"结果: {result}")
        except Exception as e:
            print(f"调用失败: {e}")

print("\n" + "=" * 60)
