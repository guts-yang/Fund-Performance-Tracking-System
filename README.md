# 基金收益追踪系统

<div align="center">

![Version](https://img.shields.io/badge/version-1.8.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-teal.svg)
![Uvicorn](https://img.shields.io/badge/Uvicorn-0.24.0-0b7285.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.23-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-336791.svg)
![Redis](https://img.shields.io/badge/Redis-5.0.1-red.svg)
![Vue](https://img.shields.io/badge/Vue-3.3.8-42b883.svg)
![Vite](https://img.shields.io/badge/Vite-5.0.4-646cff.svg)
![Element_Plus](https://img.shields.io/badge/Element_Plus-2.4.4-409eff.svg)
![ECharts](https://img.shields.io/badge/ECharts-5.4.3-aa66ef.svg)
![Pinia](https://img.shields.io/badge/Pinia-2.1.7-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

</div>

<br>

基于 **FastAPI + Vue.js + PostgreSQL** 的中国基金实时净收益查询系统，使用 **efinance 和 Tushare** 作为数据源。

## 系统预览

![首页截图](figures/home_1.png)
![基金查询](figures/fund_query.png)
![基金管理](figures/funds_management.png)
![基金持仓](figures/fund_component.png)
![持仓分析](figures/Analysis.png)

## 功能特性

- **基金管理**: 添加、编辑、删除基金代码，自动获取基金名称和类型
- **持仓跟踪**: 简化持仓设置，只需输入持有金额，系统自动计算份额
- **实时净值**: 自动获取基金最新净值数据
- **收益计算**: 自动计算每日收益和收益率
- **基金交易**: 支持买入和卖出操作，自动记录交易历史
- **定时更新**: 每个交易日自动更新净值数据
- **可视化展示**: 直观的图表展示收益趋势
- **盘中估值**: 基于股票持仓计算基金实时估值（交易时间）

## 技术栈

### 后端
- **FastAPI** - 高性能异步 Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **PostgreSQL** - 关系型数据库
- **efinance** - 东方财富财经数据接口
- **Tushare Pro** - 基金持仓数据
- **APScheduler** - 定时任务调度
- **Redis** - 内存缓存（股票名称、实时行情、基金净值、持仓数据）
- **hiredis** - Redis Python 客户端加速

### 缓存策略
- **股票名称缓存**: TTL 24小时，减少 Tushare API 调用
- **实时行情缓存**: 盘中30秒/非交易1小时，减少外部API压力
- **基金信息缓存**: TTL 24小时，静态数据长期缓存
- **最新净值缓存**: TTL 30分钟，平衡实时性和性能
- **历史净值缓存**: TTL 24小时，历史数据不变
- **持仓数据缓存**: 有报告期7天/无报告期24小时
- **空值缓存**: 防止缓存穿透，短TTL（1-5分钟）

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 快速构建工具
- **Element Plus** - UI 组件库
- **ECharts** - 数据可视化
- **Pinia** - 状态管理

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+

### 数据库配置

- PostgreSQL配置：[PostgreSQL教程 | 菜鸟教程](https://www.runoob.com/postgresql/postgresql-tutorial.html)
- Redis配置：[Redis教程 | 菜鸟教程](https://www.runoob.com/redis/redis-install.html)

```sql
CREATE DATABASE fund_tracker;
```

### 后端启动

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 配置数据库连接和 Tushare Token
```

```bash
cd backendv
```

`.env` 配置示例：
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/fund_tracker
TUSHARE_TOKEN=your_tushare_token
SCHEDULER_ENABLED=true
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问地址：http://localhost:5173

## 使用说明

### 1. 添加基金
输入基金代码（如：000001），系统自动获取基金名称和类型
![添加基金](figures/add_fund.png)

### 2. 设置持仓
只需输入持有金额，系统自动计算份额和成本价
![设置持仓](figures/set_balance.png)

### 3. 基金交易
- **买入**：输入金额，自动计算份额，成本价更新为当日净值
- **卖出**：按金额或份额卖出，成本价保持不变
![买入](figures/buy.png)
![卖出](figures/sell.png)

### 4. 同步数据
- 手动同步：点击"同步"按钮
- 自动同步：每个交易日 24:00 执行

## Tushare 使用说明

### 注册与获取 Token

1. 访问 [Tushare Pro](https://tushare.pro/register) 注册账号
2. 登录后进入「用户中心」→「接口TOKEN」
3. **学生可以免费申请2000积分，需要提供学生证明，按照对方的要求完成简单任务即可获得**
4. 复制 Token 到 `backend/.env` 文件的 `TUSHARE_TOKEN` 字段

### 本项目使用场景

Tushare 在本项目中的主要用途：

| 功能 | API 接口 | 数据说明 |
|------|----------|----------|
| 基金股票持仓 | `fund_portfolio` | 获取基金持仓股票明细（代码、名称、数量、市值、权重） |
| 股票基本信息 | `stock_basic` | 获取股票基本信息和交易状态 |
| 股票实时行情 | `realtime_quote` | 获取股票实时价格（通过爬虫接口，0积分） |

### 调用限制

- **免费用户**：每分钟 120 次调用
- **积分用户**：根据积分等级提升调用频率
- **持仓同步**：建议手动触发，避免频繁调用

### 配置示例

```python
# backend/app/.env
TUSHARE_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx  # 替换为你的 Token
```

```python
# 后端服务调用示例
from backend.app.services.tushare_service import TushareService

service = TushareService()
# 获取基金持仓
positions = service.get_fund_portfolio("000001.OF")
```

## 数据源说明

### 1. efinance（主数据源）
- **用途**：基金基本信息、历史净值、实时涨跌幅、场内基金股价
- **优势**：无需 Token、免费无限制、数据全面
- **官方文档**：https://efinance.readthedocs.io/

### 2. Tushare Pro（备用数据源）
- **用途**：基金股票持仓明细
- **优势**：数据详细、更新及时
- **限制**：需要 Token、有调用频率限制
- **官方文档**：https://tushare.pro/

## API 接口

### 基金管理
- `POST /api/funds` - 添加基金
- `GET /api/funds` - 获取基金列表
- `DELETE /api/funds/{id}` - 删除基金

### 持仓管理
- `POST /api/holdings` - 添加/更新持仓
- `GET /api/holdings` - 获取持仓列表

### 交易记录
- `POST /api/transactions/buy` - 买入
- `POST /api/transactions/sell` - 卖出

### 净值查询
- `GET /api/nav/{fund_code}` - 获取最新净值
- `GET /api/nav/{fund_code}/realtime` - 获取实时估值

### 股票持仓
- `GET /api/stock-positions/funds/{fund_id}` - 获取持仓列表
- `POST /api/stock-positions/funds/{fund_id}/sync` - 同步持仓（来自 Tushare）

## 注意事项

1. **交易日判断**：系统自动判断交易日，定时任务仅在交易日执行
2. **数据备份**：建议定期备份 PostgreSQL 数据库
3. **Token 安全**：请勿将 Tushare Token 提交到 Git 仓库
4. **网络异常**：内置重试机制和超时设置

## 常见问题

### Q: 找不到基金数据？
检查基金代码是否正确（6位数字），确认基金未退市

### Q: 数据库连接失败？
检查 `.env` 文件中的数据库配置是否正确

### Q: 定时任务不执行？
确认 `SCHEDULER_ENABLED=true` 且服务器在运行

### Q: 持仓同步失败？
检查 Tushare Token 是否正确，网络连接是否正常

## 许可证

MIT License

## 版本记录

### v1.8.0 (2026-02-06)
- **Redis缓存全面优化**: 实现三层缓存架构
  - 实时行情缓存: 盘中30秒/非交易1小时，API调用减少80-95%
  - 基金净值缓存: 最新30分钟/历史24小时，响应时间从500ms降至10ms
  - 持仓数据缓存: 有报告期7天/无报告期24小时
- **性能提升**: 平均性能提升3.5x（Redis启动后预期60-300x）
- **优雅降级**: Redis不可用时自动切换到API调用
- **新增基础设施**:
  - Redis客户端封装 (redis_client.py)
  - Efinance API客户端 (efinance_client.py)
  - 重试机制工具 (retry_helper.py)
- **配置优化**: 新增11个缓存TTL配置参数
- **测试工具**: 新增Redis缓存性能测试脚本

### v1.5.0 (2026-02-05)
- 修复饼图 DOM 渲染时序问题
- Vue 生命周期优化

### v1.4.9 (2026-02-04)
- 新增实时股票行情功能
- 添加编码问题处理
- 持仓详情展示增强

### v1.4.8 (2026-02-04)
- 修复实时估值 500 错误
- 添加交易时间检查
- 股票实时行情改用 efinance

### v1.4.7 (2026-02-04)
- 修复持仓同步字段映射错误
- 添加字段验证逻辑

### v1.4.6 (2026-02-04)
- 使用东方财富网爬虫替代 Tushare API 获取基金持仓
- 优先级策略：东方财富网 → Tushare API

### v1.4.5 (2026-02-04)
- 添加 Tushare API 调用频率限制
- 改进错误提示和日志输出

### v1.4.4 (2026-02-04)
- 修复持仓数据格式转换错误
- 修复基金代码格式问题

### v1.4.3 (2026-02-04)
- 修复所有基金无法同步股票持仓的问题
- 增强持仓同步的错误日志输出

### v1.4.2 (2026-02-04)
- 修复实时数据显示 0.00% 的问题
- 新增批量股票持仓估值 API

### v1.4.1 (2026-02-04)
- 交易时间内 10 秒高频刷新，非交易时间 5 分钟低频刷新
- 新增交易时间状态指示器

### v1.4.0 (2026-02-03)
- 新增排序功能
- 新增当日收益统计
- 优化自动同步机制

### v1.3.0
- 简化持仓设置
- 基金交易功能
- 自动净值获取

### v1.0.0
- 基金管理、持仓管理、收益分析等核心功能
