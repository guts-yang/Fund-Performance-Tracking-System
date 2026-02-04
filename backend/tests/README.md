# 持仓数据获取模块 - 测试套件

完整的测试覆盖，包括单元测试、集成测试和端到端测试。

## 目录结构

```
tests/
├── __init__.py
├── conftest.py                      # Pytest 配置和共享 fixtures
├── unit/                            # 单元测试
│   ├── test_models.py               # 数据库模型测试
│   ├── test_schemas.py              # Pydantic Schema 验证测试
│   └── test_crud.py                 # CRUD 操作测试
├── integration/                     # 集成测试
│   ├── test_stock_positions_api.py  # API 端点测试
│   ├── test_tushare_service.py      # Tushare 服务测试
│   └── test_sina_finance_service.py # 东方财富服务测试
├── e2e/                             # 端到端测试
│   └── test_sync_workflow.py        # 完整同步流程测试
├── mocks/                           # Mock 数据
│   ├── mock_tushare_api.py          # Tushare API Mock
│   └── mock_sina_api.py             # 东方财富 API Mock
└── fixtures/                        # 测试数据
    └── sample_responses.py          # 示例响应和数据生成器
```

## 快速开始

### 安装测试依赖

```bash
cd backend
pip install pytest pytest-asyncio pytest-mock
```

### 运行所有测试

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 显示测试覆盖率（需要安装 pytest-cov）
pip install pytest-cov
pytest --cov=app --cov-report=html
```

### 运行特定测试

```bash
# 只运行单元测试
pytest tests/unit/

# 只运行集成测试
pytest tests/integration/

# 只运行 E2E 测试
pytest tests/e2e/

# 运行特定测试文件
pytest tests/unit/test_models.py

# 运行特定测试用例
pytest tests/unit/test_models.py::TestFundStockPositionModel::test_position_creation

# 运行标记的测试
pytest -m unit          # 只运行单元测试
pytest -m integration   # 只运行集成测试
pytest -m "not slow"    # 跳过慢速测试
```

### 调试失败的测试

```bash
# 打印详细输出
pytest -vv -s

# 在第一个失败时停止
pytest -x

# 只运行上次失败的测试
pytest --lf

# 进入 Python 调试器
pytest --pdb
```

## 测试用例说明

### 单元测试 (Unit Tests)

#### `test_models.py` - 数据库模型测试

- ✅ 基金创建和唯一约束
- ✅ 持仓创建和字段验证
- ✅ 唯一约束（fund_id + stock_code + report_date）
- ✅ 级联删除（基金删除时持仓也删除）
- ✅ 关联关系验证

#### `test_schemas.py` - Schema 验证测试

- ✅ 有效持仓数据验证
- ✅ 权重范围验证（0-1）
- ✅ 可选字段处理
- ✅ 数据类型验证
- ✅ 最大长度验证

#### `test_crud.py` - CRUD 操作测试

- ✅ 基金 CRUD 操作
- ✅ 持仓 CRUD 操作
- ✅ 批量更新和替换
- ✅ 日期过滤
- ✅ 排序功能
- ✅ 数据隔离

### 集成测试 (Integration Tests)

#### `test_stock_positions_api.py` - API 端点测试

- ✅ GET `/api/stock-positions/funds/{fund_id}` - 获取持仓
- ✅ POST `/api/stock-positions/funds/{fund_id}/sync` - 同步持仓
- ✅ 日期过滤参数
- ✅ 错误处理（404, 400）
- ✅ 数据验证和过滤
- ✅ 降级逻辑（东方财富 → Tushare）

#### `test_tushare_service.py` - Tushare 服务测试

- ✅ 基金持仓获取
- ✅ 频率限制机制
- ✅ 自动添加 .OF 后缀
- ✅ 异常处理
- ✅ 实时行情获取

#### `test_sina_finance_service.py` - 东方财富服务测试

- ✅ 基金持仓获取
- ✅ 市场代码转换
- ✅ 频率限制机制
- ✅ 备用方案
- ✅ 网络错误处理

### 端到端测试 (E2E Tests)

#### `test_sync_workflow.py` - 完整同步流程

- ✅ 完整同步工作流
- ✅ 降级流程测试
- ✅ 数据验证流程
- ✅ 数据替换流程
- ✅ 多基金同步
- ✅ 错误恢复流程

## Fixtures 说明

### 共享 Fixtures (conftest.py)

| Fixture | 说明 | 返回类型 |
|---------|------|----------|
| `test_db` | 内存 SQLite 数据库 | `Session` |
| `client` | FastAPI 测试客户端 | `TestClient` |
| `sample_fund` | 单个测试基金 | `Fund` |
| `sample_funds` | 多个测试基金 | `list[Fund]` |
| `sample_positions` | 测试持仓数据 | `list[FundStockPositionCreate]` |
| `sample_positions_with_invalid` | 包含无效代码的数据 | `list[FundStockPositionCreate]` |

## 测试数据

### Mock 数据

所有外部 API 调用都被 Mock，避免真实请求：

- **Tushare API**: `mock_tushare_api.py`
- **东方财富 API**: `mock_sina_api.py`

### 测试数据生成器

`fixtures/sample_responses.py` 提供标准化的测试数据：

```python
from tests.fixtures.sample_responses import SampleDataFrames, TestDataGenerator

# 获取标准 DataFrame
df = SampleDataFrames.standard_positions()

# 创建测试数据
position = TestDataGenerator.create_position()
positions = TestDataGenerator.create_standard_positions()
```

## 测试覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|---------|
| 模型 (models) | 90%+ | ✅ |
| Schema (schemas) | 95%+ | ✅ |
| CRUD (crud) | 85%+ | ✅ |
| API 端点 | 80%+ | ✅ |
| 服务层 | 75%+ | ✅ |

## 持续集成

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 常见问题

### Q: 如何跳过网络请求？

A: 所有外部 API 调用都已被 Mock，无需配置。

### Q: 如何测试真实 API？

A: 暂时移除 `@patch` 装饰器，并确保 `TUSHARE_TOKEN` 环境变量已设置。

### Q: 测试数据库在哪里？

A: 使用 SQLite 内存数据库 (`:memory:`)，每个测试独立运行，测试后自动清理。

### Q: 如何添加新的测试用例？

A: 参考 `tests/unit/test_crud.py` 或 `tests/integration/test_stock_positions_api.py` 中的示例。

## 贡献指南

1. 保持测试独立：每个测试应该独立运行，不依赖其他测试
2. 使用 Mock：外部 API 调用必须使用 Mock
3. 清理数据：测试后清理数据库（使用 test_db fixture 自动处理）
4. 添加标记：为慢速测试添加 `@pytest.mark.slow`
5. 编写文档：复杂测试应添加注释说明

## 更新日志

- **v1.0.0** (2024-01-XX): 初始版本
  - 完整的单元测试覆盖
  - API 集成测试
  - 端到端工作流测试
  - Mock 数据和 fixtures

## 联系方式

如有问题，请提交 Issue 或 Pull Request。
