"""Redis缓存性能测试"""
import time
from app.services.tushare_service import tushare_service
from app.services.fund_fetcher import FundDataFetcher

def test_stock_realtime_cache():
    """测试股票实时行情缓存性能"""
    stock_codes = ['000001.SZ', '600519.SH', '600036.SH']

    print("\n" + "=" * 60)
    print("测试1: 股票实时行情缓存性能")
    print("=" * 60)

    # 第一次（冷启动）
    print("\n[测试] 第一次调用（缓存未命中）...")
    start = time.time()
    result1 = tushare_service.get_stock_realtime(stock_codes)
    time1 = time.time() - start
    print(f"[结果] 冷启动耗时: {time1:.3f}秒")
    print(f"[结果] 获取股票数: {len(result1)}")

    # 第二次（缓存命中）
    print("\n[测试] 第二次调用（应该缓存命中）...")
    start = time.time()
    result2 = tushare_service.get_stock_realtime(stock_codes)
    time2 = time.time() - start
    print(f"[结果] 缓存命中耗时: {time2:.3f}秒")
    print(f"[结果] 获取股票数: {len(result2)}")

    # 计算性能提升
    if time2 > 0:
        speedup = time1 / time2
        improvement = ((time1 - time2) / time1) * 100
        print(f"\n[统计] 性能提升: {speedup:.1f}x")
        print(f"[统计] 时间节省: {time1 - time2:.3f}秒")
        print(f"[统计] 改进幅度: {improvement:.1f}%")

    return time1, time2

def test_fund_info_cache():
    """测试基金信息缓存性能"""
    fund_code = "000001"

    print("\n" + "=" * 60)
    print("测试2: 基金信息缓存性能")
    print("=" * 60)

    # 第一次
    print(f"\n[测试] 第一次调用基金{fund_code}信息（缓存未命中）...")
    start = time.time()
    info1 = FundDataFetcher.get_fund_info(fund_code)
    time1 = time.time() - start
    print(f"[结果] 冷启动耗时: {time1:.3f}秒")
    print(f"[结果] 基金名称: {info1.get('fund_name', 'N/A')}")

    # 第二次
    print(f"\n[测试] 第二次调用基金{fund_code}信息（应该缓存命中）...")
    start = time.time()
    info2 = FundDataFetcher.get_fund_info(fund_code)
    time2 = time.time() - start
    print(f"[结果] 缓存命中耗时: {time2:.3f}秒")
    print(f"[结果] 基金名称: {info2.get('fund_name', 'N/A')}")

    # 计算性能提升
    if time2 > 0:
        speedup = time1 / time2
        improvement = ((time1 - time2) / time1) * 100
        print(f"\n[统计] 性能提升: {speedup:.1f}x")
        print(f"[统计] 时间节省: {time1 - time2:.3f}秒")
        print(f"[统计] 改进幅度: {improvement:.1f}%")

    return time1, time2

def test_fund_nav_cache():
    """测试基金净值缓存性能"""
    fund_code = "000001"

    print("\n" + "=" * 60)
    print("测试3: 基金最新净值缓存性能")
    print("=" * 60)

    # 第一次
    print(f"\n[测试] 第一次调用基金{fund_code}最新净值（缓存未命中）...")
    start = time.time()
    nav1 = FundDataFetcher.get_fund_nav(fund_code)
    time1 = time.time() - start
    print(f"[结果] 冷启动耗时: {time1:.3f}秒")
    if nav1:
        print(f"[结果] 净值日期: {nav1.get('date', 'N/A')}")
        print(f"[结果] 单位净值: {nav1.get('unit_nav', 'N/A')}")
    else:
        print("[结果] 未获取到净值数据")

    # 第二次
    print(f"\n[测试] 第二次调用基金{fund_code}最新净值（应该缓存命中）...")
    start = time.time()
    nav2 = FundDataFetcher.get_fund_nav(fund_code)
    time2 = time.time() - start
    print(f"[结果] 缓存命中耗时: {time2:.3f}秒")
    if nav2:
        print(f"[结果] 净值日期: {nav2.get('date', 'N/A')}")
        print(f"[结果] 单位净值: {nav2.get('unit_nav', 'N/A')}")

    # 计算性能提升
    if time2 > 0:
        speedup = time1 / time2
        improvement = ((time1 - time2) / time1) * 100
        print(f"\n[统计] 性能提升: {speedup:.1f}x")
        print(f"[统计] 时间节省: {time1 - time2:.3f}秒")
        print(f"[统计] 改进幅度: {improvement:.1f}%")

    return time1, time2

def print_summary(test_results):
    """打印测试总结"""
    print("\n" + "=" * 60)
    print("性能测试总结")
    print("=" * 60)

    total_tests = len(test_results)
    total_speedup = 0
    valid_speedup_count = 0

    for test_name, (time1, time2) in test_results.items():
        if time2 > 0:
            speedup = time1 / time2
            total_speedup += speedup
            valid_speedup_count += 1
            print(f"{test_name}:")
            print(f"  冷启动: {time1:.3f}秒 -> 缓存命中: {time2:.3f}秒")
            print(f"  性能提升: {speedup:.1f}x")

    if valid_speedup_count > 0:
        avg_speedup = total_speedup / valid_speedup_count
        print(f"\n平均性能提升: {avg_speedup:.1f}x")

    print("\n" + "=" * 60)
    print("[完成] 所有测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    print("=" * 60)
    print("Redis缓存性能测试")
    print("=" * 60)
    print("\n说明：此脚本测试Redis缓存对性能的提升")
    print("      每个测试会调用两次API，第一次为冷启动，第二次应命中缓存")
    print("      非交易时间可能看不到显著的缓存效果")

    test_results = {}

    try:
        # 测试1: 股票实时行情
        t1_1, t1_2 = test_stock_realtime_cache()
        test_results["股票实时行情"] = (t1_1, t1_2)

        # 测试2: 基金信息
        t2_1, t2_2 = test_fund_info_cache()
        test_results["基金信息"] = (t2_1, t2_2)

        # 测试3: 基金净值
        t3_1, t3_2 = test_fund_nav_cache()
        test_results["基金最新净值"] = (t3_1, t3_2)

        # 打印总结
        print_summary(test_results)

    except Exception as e:
        print(f"\n[错误] 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
