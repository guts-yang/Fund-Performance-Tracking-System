# 基金收益追踪系统

因为自2026年2月2日之后，养基宝等多个可以实时监控基金收益的软件或小程序对应功能被下架，所以我选择完成此项目来供自身和网友学习，目前仍在优化中...

## 系统预览

![首页截图](figures/home_1.png)
![基金查询](figures/fund_query.png)
![基金管理](figures/funds_management.png)

## 项目简介

这是一个基于 **FastAPI + Vue.js + PostgreSQL** 的中国基金实时净收益查询系统，使用 **efinance** 作为数据源。

### 为什么选择 efinance？

- **稳定可靠**：基于东方财富官方数据源，数据准确及时
- **免费使用**：无需付费，无调用次数限制
- **易于使用**：简洁的 API 设计，返回 pandas DataFrame 格式
- **数据全面**：支持基金、股票、债券等多种金融产品
- **持续维护**：活跃的社区和持续的更新维护

## 功能特性

### 核心功能

- 📊 **基金管理**: 添加、编辑、删除基金代码，自动获取基金名称和类型
- 💰 **持仓跟踪**: 简化持仓设置，只需输入持有金额，系统自动计算份额
- 📈 **实时净值**: 自动获取基金最新净值数据
- 📉 **收益计算**: 自动计算每日收益和收益率
- 💱 **基金交易**: 支持买入和卖出操作，自动记录交易历史
- ⏰ **定时更新**: 每个交易日自动更新净值数据
- 📱 **可视化展示**: 直观的图表展示收益趋势

### 最新功能 (v1.4.0)

- ✨ **排序功能**: 首页和基金列表支持按持有金额、实时数据等字段排序，支持正序/逆序切换
- ✨ **当日收益**: 首页新增当日收益统计卡片，实时显示当日盈亏情况
- ✨ **自动同步优化**:
  - 登录时自动同步（距离上次同步超过24小时）
  - 定时任务改为每天24:00执行
  - 自动更新持仓金额（基于最新净值）
- ✨ **安全性增强**: Tushare Token 使用环境变量配置，不再硬编码

### 最新功能 (v1.3.0)

- ✨ **简化持仓设置**: 只需输入持有金额，系统自动获取净值并计算份额和成本价
- ✨ **基金交易功能**: 支持买入/卖出操作
  - 买入：输入金额，自动获取当日净值计算份额，成本价更新为当日净值
  - 卖出：支持按金额或按份额卖出，成本价保持不变
  - 交易历史记录：完整记录每笔交易
- ✨ **基金名称显示**: 基金列表优先显示基金简称而非代码
- ✨ **自动净值获取**: 所有持仓相关操作都通过 efinance 自动获取最新净值

## 技术亮点

- 🚀 **前后端分离**：Vue 3 + FastAPI 现代化技术栈
- 🔄 **自动同步**：每个交易日自动更新净值数据
- 📊 **数据可视化**：ECharts 图表展示收益趋势
- 💾 **精确计算**：使用 Decimal 类型避免浮点数精度问题
- 🛡️ **类型安全**：Pydantic 数据验证和类型检查
- 📝 **RESTful API**：规范的 API 设计和文档
- ⚡ **高性能**：FastAPI 异步处理，支持高并发
- 🔐 **配置管理**：环境变量配置，支持多环境部署

## 技术栈

### 后端
- **FastAPI** - 高性能异步 Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **PostgreSQL** - 关系型数据库
- **efinance** - 东方财富财经数据接口（支持基金、股票等金融数据）
- **APScheduler** - 定时任务调度
- **Pydantic** - 数据验证和设置管理
- **Alembic** - 数据库迁移工具

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 快速构建工具
- **Element Plus** - UI 组件库
- **ECharts** - 数据可视化
- **Pinia** - 状态管理
- **Axios** - HTTP 客户端

## 项目结构

```
project/
├── backend/                      # 后端项目（FastAPI）
│   ├── app/
│   │   ├── api/                  # API 路由层
│   │   │   ├── funds.py         # 基金管理 API
│   │   │   ├── holdings.py      # 持仓管理 API
│   │   │   ├── transactions.py  # 交易记录 API
│   │   │   ├── nav.py           # 净值查询 API
│   │   │   └── pnl.py           # 收益统计 API
│   │   ├── services/             # 业务服务层
│   │   │   └── fund_fetcher.py  # efinance 数据获取服务
│   │   ├── models.py             # SQLAlchemy 数据模型
│   │   ├── schemas.py            # Pydantic 数据验证模式
│   │   ├── crud.py               # 数据库 CRUD 操作
│   │   ├── database.py           # 数据库连接配置
│   │   ├── config.py             # 应用配置（环境变量）
│   │   ├── scheduler.py          # APScheduler 定时任务
│   │   └── main.py               # FastAPI 应用入口
│   ├── requirements.txt          # Python 依赖列表
│   └── .env                      # 环境变量配置文件
├── frontend/                     # 前端项目（Vue 3）
│   ├── src/
│   │   ├── views/                # 页面组件
│   │   │   ├── Dashboard.vue    # 仪表盘（首页）
│   │   │   ├── FundList.vue     # 基金列表
│   │   │   ├── HoldingMgmt.vue  # 持仓管理
│   │   │   └── Analysis.vue     # 数据分析
│   │   ├── components/           # 可复用组件
│   │   ├── api/                  # API 调用封装
│   │   │   ├── fund.js          # 基金相关 API
│   │   │   ├── holding.js       # 持仓相关 API
│   │   │   └── nav.js           # 净值相关 API
│   │   ├── stores/               # Pinia 状态管理
│   │   └── router/               # Vue Router 路由配置
│   ├── package.json              # Node.js 依赖列表
│   └── vite.config.js            # Vite 构建配置
├── figures/                      # 图片资源
│   └── home.png                  # 首页截图
└── README.md                     # 项目说明文档
```

## 快速开始

### 1. 环境要求

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+

### 2. 数据库配置

```sql
-- 创建数据库
CREATE DATABASE fund_tracker;

-- 创建用户（可选）
CREATE USER fund_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fund_tracker TO fund_user;
```

### 3. 后端配置

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp .env.example .env

# 编辑 .env 文件，配置数据库连接
```

`.env` 配置示例：
```env
DATABASE_URL=postgresql://postgres:342802@localhost:5432/fund_tracker
DB_USER=root
DB_PASSWORD=342802
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fund_tracker

API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173

# Tushare Pro Token（获取方式：https://tushare.pro/register）
TUSHARE_TOKEN=your_tushare_token_here

SCHEDULER_ENABLED=true
SCHEDULER_HOUR=0    # 24:00 执行（0 表示午夜）
SCHEDULER_MINUTE=0
```

### 4. 启动后端

```bash
cd backend

# 启动开发服务器
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档：http://localhost:8000/docs

### 5. 前端配置

```bash
cd frontend

# 安装依赖
npm install
```

### 6. 启动前端

```bash
cd frontend

# 启动开发服务器
npm run dev
```

前端访问地址：http://localhost:5173

## 使用说明

### 1. 添加基金

进入"基金管理"页面，点击"添加基金"按钮，输入基金代码（如：000001）。

系统会自动获取基金名称和类型。

![添加基金](figures/add_fund.png)

### 2. 设置持仓

进入"基金管理"页面，点击"设置持仓"按钮，只需输入持有金额即可。

系统会自动获取最新净值并计算：
- 持有份额 = 持有金额 / 最新净值
- 成本单价 = 最新净值

![设置持仓](figures/set_balance.png)

### 3. 基金交易

进入"基金管理"页面，点击"交易"按钮进行买入或卖出操作：

**买入操作**：
- 输入买入金额
- 系统自动获取当日净值
- 自动计算买入份额
- 持仓增加，成本价更新为当日净值

![买入操作](figures/buy.png)

**卖出操作**：
- 选择按金额或按份额卖出
- 系统自动获取当日净值
- 验证持仓是否足够
- 持仓减少，成本价保持不变

![卖出操作](figures/sell.png)

### 4. 同步数据

- 手动同步：点击基金列表中的"同步"按钮
- 自动同步：每个交易日 16:00 自动执行

### 5. 查看收益

在首页查看总收益和各基金收益详情。

![首页截图](figures/home_1.png)

## API 接口

### 基金管理
- `POST /api/funds` - 添加基金
- `GET /api/funds` - 获取基金列表
- `GET /api/funds/{id}` - 获取基金详情
- `PUT /api/funds/{id}` - 更新基金信息
- `DELETE /api/funds/{id}` - 删除基金
- `POST /api/funds/{id}/sync` - 同步基金数据
- `GET /api/funds/info/{fund_code}` - 根据代码获取基金信息

### 持仓管理
- `POST /api/holdings` - 添加/更新持仓（支持自动获取净值）
- `GET /api/holdings` - 获取持仓列表
- `GET /api/holdings/{fund_id}` - 获取基金持仓
- `PUT /api/holdings/{fund_id}` - 更新持仓
- `DELETE /api/holdings/{fund_id}` - 删除持仓

### 交易记录
- `POST /api/transactions/buy` - 买入基金
- `POST /api/transactions/sell` - 卖出基金
- `GET /api/transactions/{fund_id}` - 获取交易历史

### 净值查询
- `GET /api/nav/{fund_code}` - 获取最新净值
- `GET /api/nav/{fund_code}/history` - 获取历史净值
- `POST /api/nav/sync-all` - 同步所有基金净值

### 收益统计
- `GET /api/pnl/summary` - 获取投资组合汇总
- `GET /api/pnl/daily/{fund_id}` - 获取每日收益
- `GET /api/pnl/chart/{fund_id}` - 获取图表数据

## 注意事项

1. **efinance 数据源**：
   - 使用东方财富提供的 efinance 接口获取基金数据
   - 支持各类场内基金（ETF、LOF）和场外基金
   - 数据包括：基金基本信息、**实时净值**、历史净值、涨跌幅等
   - 如遇到数据获取失败，请检查网络连接或稍后重试

2. **Tushare Pro 数据源**（股票持仓数据）：
   - 用于获取基金股票持仓明细和股票实时行情
   - 需要申请 Tushare Pro Token：https://tushare.pro/register
   - 配置方式：在 `backend/.env` 文件中设置 `TUSHARE_TOKEN`
   - 数据包括：基金持仓股票、股票实时价格、涨跌幅等
   - 免费版用户有积分限制，建议合理使用
   - 安全提示：请勿将 Token 提交到 Git 仓库

3. **交易日判断**：
   - 系统会自动判断是否为交易日（排除周末）
   - 定时任务仅在交易日执行
   - 定时任务在每日 24:00 执行，更新净值和持仓金额

3. **数据备份**：
   - 建议定期备份 PostgreSQL 数据库
   - 可使用 `pg_dump` 命令进行备份
   - 备份命令示例：`pg_dump -U postgres fund_tracker > backup_$(date +%Y%m%d).sql`

4. **网络异常**：
   - 内置重试机制和超时设置
   - 所有外部 API 调用都有异常处理
   - 错误日志会记录在 `backend/app/logs/` 目录（如果配置）

5. **数据类型说明**：
   - 持仓金额：Decimal 类型，精确到分
   - 净值数据：Decimal 类型，避免浮点数精度问题
   - 日期格式：统一使用 `YYYY-MM-DD` 格式

## 常见问题

### Q: 找不到基金数据？

A: efinance 支持场内基金和场外基金，大部分公募基金都可以查询。如果遇到查询不到的情况，可以：
- 检查基金代码是否正确（6位数字）
- 尝试使用天天基金的基金代码
- 确认该基金是否已退市或合并
- 查看后端日志获取详细错误信息

### Q: 数据库连接失败？

A: 请检查 `.env` 文件中的数据库配置是否正确。

### Q: 定时任务不执行？

A: 确认 `SCHEDULER_ENABLED=true` 且服务器在 16:00 后运行。

### Q: 如何查看日志？

A: 后端日志会输出到控制台，可以配置日志文件。前端使用浏览器开发者工具查看。

### Q: 支持哪些类型的基金？

A: efinance 支持大多数公募基金，包括：
- 开放式基金
- 封闭式基金
- ETF（交易所交易基金）
- LOF（上市开放式基金）
- QDII基金

## 数据源说明

### 1. efinance 数据源

**用途**：基金基础数据、历史净值、实时估值

**使用模块**：
- `backend/app/services/fund_fetcher.py` - `FundDataFetcher` 类

**调用 API**：
1. **基金基本信息**：
   - `ef.fund.get_base_info(fund_code)` - 获取基金名称、类型、最新净值
2. **历史净值数据**：
   - `ef.fund.get_quote_history(fund_code)` - 获取净值历史、涨跌幅
3. **基金搜索**：
   - `ef.fund.get_fund_codes()` - 搜索所有基金代码
4. **ETF/LOF 实时价格**：
   - `ef.stock.get_realtime_quotes('ETF')` - 获取 ETF 实时价格
   - `ef.stock.get_realtime_quotes('LOF')` - 获取 LOF 实时价格
5. **境外基金实时估值**：
   - `ef.fund.get_realtime_increase_rate(fund_code)` - 获取估算涨跌幅

**特点**：
- 无需 API Token
- 数据覆盖全面
- 实时性较好

### 2. Tushare Pro 数据源

**用途**：基金股票持仓明细、股票实时行情、估值计算

**使用模块**：
- `backend/app/services/tushare_service.py` - `TushareService` 类
- `backend/app/api/nav.py` - 实时估值计算
- `backend/app/api/stock_positions.py` - 持仓同步

**调用 API**：
1. **基金股票持仓**：
   - `pro.fund_portfolio(ts_code=fund_code, period=period)` - 获取基金持仓股票明细
2. **股票实时行情**：
   - `ts.realtime(ts_code=stock_codes, src='sina')` - 获取股票实时价格（来源：新浪财经）

**特点**：
- 需要 Tushare Pro Token（免费注册）
- 提供详细的持仓数据
- 免费版有积分限制

### 3. 基金估值计算逻辑

**计算原理**：基于基金持仓股票的实时涨跌幅，加权计算基金实时估值

**计算公式**：

```
步骤 1：获取基金最新持仓（来自 Tushare）
- 股票代码、持仓数量、市值、权重

步骤 2：获取持仓股票的实时价格（来自新浪财经 via Tushare）
- 当前价格、涨跌幅

步骤 3：计算加权平均涨跌幅
weighted_change_pct = Σ(weight[i] × change_pct[i])

步骤 4：计算实时净值
realtime_nav = latest_nav × (1 + weighted_change_pct)

步骤 5：计算实时市值
realtime_market_value = shares × realtime_nav
```

**代码实现**：`backend/app/services/tushare_service.py` (Lines 85-156)

**示例**：
```
基金 A 最新净值：1.5000
持仓股票 B：权重 30%，涨跌幅 +2.5%
持仓股票 C：权重 70%，涨跌幅 -1.0%

加权涨跌幅 = 0.3 × 2.5% + 0.7 × (-1.0%) = 0.75% - 0.7% = 0.05%
实时净值 = 1.5000 × (1 + 0.0005) = 1.50075
```

**注意事项**：
- 仅在交易时间内计算（周一至周五 09:30-15:00）
- 非交易时间返回最新官方净值
- 实时数据缓存 60 秒
- ETF/LOF 使用实际市场价格而非估算

## 开发计划

- [ ] 支持多账户管理
- [ ] 添加收益目标功能
- [ ] 支持导出数据到 Excel
- [ ] 添加更多图表分析（最大回撤、夏普比率等）
- [ ] 支持移动端适配
- [ ] 添加基金对比功能
- [ ] 支持股基混合投资组合
- [ ] 添加邮件/微信通知功能
- [ ] 支持自定义交易日历
- [ ] 添加数据导入导出功能

## 许可证

MIT License

---

## 版本记录

### v1.6.5 (2026-02-04)

**优化改进**：
- ⏱️ 添加 Tushare API 调用频率限制（两次调用间隔至少 1 秒）
- 📊 改进错误提示，区分不同类型的 API 错误（频率限制、权限不足等）
- 🔍 增强日志输出，记录 API 调用详情和空数据原因
- ✅ 解决 Tushare API 频率限制导致返回空数据的问题

### v1.6.4 (2026-02-04)

**Bug 修复**：
- 🐛 修复持仓数据格式转换错误
- 🔧 weight 字段：百分比转小数（4.82 → 0.0482）
- 🔧 report_date 字段：字符串转 date 对象（'20251231' → date(2025, 12, 31)）
- ✅ 验证持仓同步数据可正确保存到数据库

### v1.6.3 (2026-02-04)

**Bug 修复**：
- 🐛 修复基金代码格式问题导致 Tushare 返回空数据
- 🔧 自动为基金代码添加 .OF 后缀（016582 → 016582.OF）
- 📊 改进日志输出，记录代码格式转换过程

### v1.6.2 (2026-02-04)

**Bug 修复**：
- 🐛 修复所有基金无法同步股票持仓的问题
- 🔧 修正 Tushare API 字段映射错误（stk_name → symbol, stk_share → amount 等）
- 📊 增强持仓同步的错误日志输出，方便调试
- ✅ 验证持仓同步功能可正常工作

### v1.6.1 (2026-02-04)

**实时估值修复**：
- 🐛 修复实时数据显示 0.00% 的问题
- 📊 新增批量股票持仓估值 API (`/api/nav/realtime/batch-stock`)
- 🔄 多数据源策略：场内基金实时股价 → 场外基金持仓估值 → efinance 降级 → 正式净值
- 📝 完善数据源标识显示（场内/持仓估值/场外）

### v1.6.0 (2026-02-04)

**动态刷新优化**：
- ⚡ 交易时间内 10 秒高频刷新，非交易时间 5 分钟低频刷新
- 📊 新增交易时间状态指示器（🔴 交易中 / ⚫ 非交易）
- 🔧 重构自动刷新逻辑，支持动态间隔调整

### v1.5.0 (2026-02-03)

**颜色逻辑修正**：
- 🎨 符合中国股市惯例：正收益=红色、负收益=绿色、零收益=白色
- 📝 优化 README：添加数据源详细说明和基金估值计算逻辑

### v1.4.0 (2026-02-03)

**新增功能**：
- ✨ 排序功能：首页和基金列表支持多字段排序
- ✨ 当日收益：首页新增当日收益统计卡片

**优化改进**：
- 🔧 自动同步机制：登录后自动同步、定时任务改为24:00、每日更新持仓金额
- 🔧 安全性增强：移除硬编码的 TUSHARE_TOKEN

### v1.3.0 及更早

- 盘中实时估值、自动刷新机制、双净值对比
- 简化持仓设置、基金交易功能
- 量子指挥中心主题UI升级
- 基金管理、持仓管理、收益分析等核心功能
