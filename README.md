# 基金收益追踪系统

因为自2026年2月2日之后，养基宝等多个可以实时监控基金收益的软件或小程序对应功能被下架，所以我选择完成此项目来供自身和网友学习，目前仍在优化中...

figures/image.png

这是一个基于 **FastAPI + Vue.js + PostgreSQL** 的中国基金实时净收益查询系统，使用 **efinance** 作为数据源。

## 为什么选择 efinance？

- **稳定可靠**：基于东方财富官方数据源，数据准确及时
- **免费使用**：无需付费，无调用次数限制
- **易于使用**：简洁的 API 设计，返回 pandas DataFrame 格式
- **数据全面**：支持基金、股票、债券等多种金融产品
- **持续维护**：活跃的社区和持续的更新维护

## 技术亮点

## 功能特性

- 📊 **基金管理**: 添加、编辑、删除基金代码
- 💰 **持仓跟踪**: 管理基金持仓金额和份额
- 📈 **实时净值**: 自动获取基金最新净值数据
- 📉 **收益计算**: 自动计算每日收益和收益率
- ⏰ **定时更新**: 每个交易日自动更新净值数据
- 📱 **可视化展示**: 直观的图表展示收益趋势

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
- Vue 3 - 渐进式 JavaScript 框架
- Vite - 快速构建工具
- Element Plus - UI 组件库
- ECharts - 数据可视化
- Pinia - 状态管理
- Axios - HTTP 客户端

## 项目结构

```
project/
├── backend/                      # 后端项目（FastAPI）
│   ├── app/
│   │   ├── api/                  # API 路由层
│   │   │   ├── funds.py         # 基金管理 API
│   │   │   ├── holdings.py      # 持仓管理 API
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

SCHEDULER_ENABLED=true
SCHEDULER_HOUR=16
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

### 2. 设置持仓

进入"持仓管理"页面，编辑基金持仓金额、份额和成本单价。

### 3. 同步数据

- 手动同步：点击"同步数据"按钮
- 自动同步：每个交易日 16:00 自动执行

### 4. 查看收益

在首页查看总收益和各基金收益详情。

## API 接口

### 基金管理
- `POST /api/funds` - 添加基金
- `GET /api/funds` - 获取基金列表
- `GET /api/funds/{id}` - 获取基金详情
- `PUT /api/funds/{id}` - 更新基金信息
- `DELETE /api/funds/{id}` - 删除基金
- `POST /api/funds/{id}/sync` - 同步基金数据

### 持仓管理
- `POST /api/holdings` - 添加持仓
- `GET /api/holdings` - 获取持仓列表
- `GET /api/holdings/{fund_id}` - 获取基金持仓
- `PUT /api/holdings/{fund_id}` - 更新持仓
- `DELETE /api/holdings/{fund_id}` - 删除持仓

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
   - 数据包括：基金基本信息、 **实时净值** 、历史净值、涨跌幅等
   - 如遇到数据获取失败，请检查网络连接或稍后重试

2. **交易日判断**：
   - 系统会自动判断是否为交易日（排除周末）
   - 定时任务仅在交易日执行
   - 建议设置定时任务在交易日 16:00 之后执行（此时净值已更新）

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

## Docker 部署（可选）

### 使用 Docker Compose

项目包含 `docker-compose.yml` 文件，可以一键启动所有服务：

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 单独构建

```bash
# 构建后端镜像
cd backend
docker build -t fund-tracker-backend .

# 构建前端镜像
cd frontend
docker build -t fund-tracker-frontend .

# 运行容器
docker run -p 8000:8000 --env-file .env fund-tracker-backend
docker run -p 5173:5173 fund-tracker-frontend
```

## 系统架构

### 数据流程

```
用户请求 → Vue.js 前端 → FastAPI 后端 → PostgreSQL 数据库
                ↓
        efinance API（获取基金数据）
                ↓
        数据处理和计算
                ↓
        返回结果并存储
```

### 核心模块说明

- **[fund_fetcher.py](backend/app/services/fund_fetcher.py)** - 基金数据获取服务
  - `get_fund_info()` - 获取基金基本信息
  - `get_fund_nav()` - 获取最新净值
  - `get_fund_history()` - 获取历史净值数据
  - `search_fund()` - 搜索基金

- **[scheduler.py](backend/app/scheduler.py)** - 定时任务调度
  - 每个交易日自动更新净值
  - 可配置执行时间

- **[models.py](backend/app/models.py)** - 数据库模型
  - Fund（基金信息）
  - Holding（持仓信息）
  - NetAssetValue（净值历史）
  - DailyPnL（每日收益）

### API 响应格式

所有 API 返回统一格式：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

错误响应：

```json
{
  "code": 400,
  "message": "错误信息",
  "data": null
}
```

## 开发指南

### 后端开发

```bash
cd backend

# 安装开发依赖
pip install -r requirements.txt

# 运行测试
pytest

# 代码格式化
black app/
isort app/

# 类型检查
mypy app/
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 开发模式（热重载）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 数据库迁移

```bash
cd backend

# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 提交 PR 前请确保：

1. 代码符合项目风格规范
2. 添加必要的测试
3. 更新相关文档
4. 确保所有测试通过

### 提交信息规范

```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 重构代码
test: 添加测试
chore: 构建/工具变动
```

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

## 参考资源

### 技术文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Vue 3 官方文档](https://cn.vuejs.org/)
- [efinance 文档](https://efinance.readthedocs.io/)
- [Element Plus 文档](https://element-plus.org/)
- [ECharts 文档](https://echarts.apache.org/)

### 数据源说明

本项目使用 **efinance** 库获取基金数据，该库基于东方财富网公开数据接口，仅供学习和个人使用。

### 基金信息查询

- 天天基金网：https://fund.eastmoney.com/
- 东方财富网：https://www.eastmoney.com/

## 致谢

感谢以下开源项目：

- [FastAPI](https://github.com/tiangolo/fastapi) - 现代化的 Python Web 框架
- [Vue.js](https://github.com/vuejs/core) - 渐进式 JavaScript 框架
- [efinance](https://github.com/infintetime/efinance) - 财经数据接口库
- [Element Plus](https://github.com/element-plus/element-plus) - Vue 3 UI 组件库
- [ECharts](https://github.com/apache/echarts) - 数据可视化图表库

## 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

## 版本记录

### v1.1.0 (2025-02-01)

**新增功能**：
- ✨ 基金名称自动获取（可手动修改）- 输入基金代码后自动从 efinance 获取基金名称和类型
- ✨ 基金列表页快速设置持仓 - 在基金列表页直接点击"设置持仓"按钮快速设置持仓信息
- ✨ 灵活输入，自动计算第三个字段 - 支持三种自动计算模式：
  - 输入金额和成本价 → 自动计算份额
  - 输入金额和份额 → 自动计算成本价
  - 输入份额和成本价 → 自动计算金额
- ✨ 基金列表显示持有金额和持有份额列

**优化**：
- 🔧 优化持仓计算逻辑，支持灵活输入
- 🔧 改进用户交互体验，添加加载状态提示

**Bug 修复**：
- 🐛 修复同步功能返回 500 错误的问题（移除错误的 pz 参数）
- 🐛 修复基金信息不显示的问题（正确处理 pandas Series 和 dict 类型）
- 🔧 配置 Pydantic 忽略 .env 中的额外字段（extra = "ignore"）
- 🔧 增强同步端点的错误处理，提供更详细的错误信息

**修改文件**：
- `backend/app/api/funds.py` - 新增基金信息查询 API，增强错误处理
- `backend/app/schemas.py` - 新增 FundInfoResponse 模型
- `backend/app/api/holdings.py` - 优化持仓计算逻辑
- `backend/app/config.py` - 添加 extra = "ignore" 配置
- `backend/app/services/fund_fetcher.py` - 修复 API 调用参数和返回值处理
- `frontend/src/api/fund.js` - 新增 API 调用方法
- `frontend/src/views/FundList.vue` - 实现新功能

### v1.0.0 (2026-01-31)

**初始版本**：
- 🎉 基础基金管理功能（添加、编辑、删除基金）
- 💰 持仓管理功能
- 📈 净值查询和同步
- 📊 收益统计和展示
- ⏰ 定时任务自动更新净值
- 🎨 Dashboard 可视化展示
