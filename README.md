# 基金收益追踪系统

因为自2026年2月2日之后，养基宝等多个可以实时监控基金收益的软件或小程序被下架，所以我选择完成此项目来供自身和网友学习，目前仍在优化中...
一个基于 FastAPI + Vue.js + PostgreSQL 的中国基金实时净收益查询系统。

## 功能特性

- 📊 **基金管理**: 添加、编辑、删除基金代码
- 💰 **持仓跟踪**: 管理基金持仓金额和份额
- 📈 **实时净值**: 自动获取基金最新净值数据
- 📉 **收益计算**: 自动计算每日收益和收益率
- ⏰ **定时更新**: 每个交易日自动更新净值数据
- 📱 **可视化展示**: 直观的图表展示收益趋势

## 技术栈

### 后端
- FastAPI - 高性能异步 Web 框架
- SQLAlchemy - ORM 数据库操作
- PostgreSQL - 关系型数据库
- AKShare - 财经数据接口
- APScheduler - 定时任务调度

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
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── services/       # 业务服务
│   │   ├── models.py       # 数据模型
│   │   ├── schemas.py      # 数据验证
│   │   ├── crud.py         # 数据库操作
│   │   ├── database.py     # 数据库配置
│   │   ├── scheduler.py    # 定时任务
│   │   └── main.py         # 应用入口
│   ├── requirements.txt
│   └── .env                # 配置文件
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 公共组件
│   │   ├── api/            # API 调用
│   │   ├── stores/         # 状态管理
│   │   └── router/         # 路由配置
│   ├── package.json
│   └── vite.config.js
└── README.md
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

1. **AKShare 数据源**：某些基金可能查询不到，需要做错误处理
2. **交易日判断**：避免非交易日执行定时任务
3. **数据备份**：定期备份 PostgreSQL 数据库
4. **网络异常**：内置重试机制和超时设置

## 常见问题

### Q: 找不到基金数据？

A: AKShare 主要支持场内基金，部分基金可能无法查询。可以尝试使用天天基金代码。

### Q: 数据库连接失败？

A: 请检查 `.env` 文件中的数据库配置是否正确。

### Q: 定时任务不执行？

A: 确认 `SCHEDULER_ENABLED=true` 且服务器在 16:00 后运行。

## 开发计划

- [ ] 支持多账户管理
- [ ] 添加收益目标功能
- [ ] 支持导出数据到 Excel
- [ ] 添加更多图表分析
- [ ] 支持移动端适配

## 许可证

MIT License

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

### v1.0.0 (2025-01-XX)

**初始版本**：
- 🎉 基础基金管理功能（添加、编辑、删除基金）
- 💰 持仓管理功能
- 📈 净值查询和同步
- 📊 收益统计和展示
- ⏰ 定时任务自动更新净值
- 🎨 Dashboard 可视化展示
