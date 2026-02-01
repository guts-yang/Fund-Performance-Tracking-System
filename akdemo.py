import akshare as ak

# 获取贵州茅台日线数据（前复权）

df = ak.stock_zh_a_daily(symbol="sh600519", adjust="qfq")

print(df.tail())

# 获取沪深300指数

index_df = ak.index_zh_ah_daily(symbol="sh000300")

# 获取融资融券余额

margin_df = ak.stock_margin_szse_summary() # 深市两融汇总

# 获取期货主力合约行情

futures_df = ak.futures_main_sina(symbol="RB") # 螺纹钢

# 获取基金净值

etf_df = ak.fund_etf_hist_em(fund="510300") # 沪深300ETF