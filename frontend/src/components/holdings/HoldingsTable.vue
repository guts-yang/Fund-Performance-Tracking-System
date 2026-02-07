<template>
  <div class="holdings-table-container">
    <div class="glass-card p-6">
      <!-- Table Header -->
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-white">基金列表</h3>
        <div class="text-sm text-gray-400">
          共 {{ holdings.length }} 只基金
        </div>
      </div>

      <!-- Table -->
      <div v-loading="loading" class="table-wrapper">
        <el-table
          :data="holdings"
          @sort-change="handleSortChange"
          :default-sort="{ prop: 'amount', order: 'descending' }"
          class="holdings-table"
          stripe
        >
          <el-table-column prop="fund.fund_code" label="基金代码" width="120" sortable>
            <template #default="{ row }">
              <span class="font-mono-number text-sci-cyan">{{ row.fund.fund_code }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="fund.fund_name" label="基金名称" min-width="200" sortable>
            <template #default="{ row }">
              <router-link
                :to="`/funds/${row.fund_id}`"
                class="fund-name-link"
              >
                {{ row.fund.fund_name }}
              </router-link>
            </template>
          </el-table-column>

          <el-table-column prop="amount" label="持有金额" width="140" sortable align="right">
            <template #default="{ row }">
              <span class="font-mono-number text-gray-200">¥{{ formatNumber(row.amount) }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="cost" label="总成本" width="140" sortable align="right">
            <template #default="{ row }">
              <span class="font-mono-number text-sci-cyan">¥{{ formatNumber(row.cost) }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="profit" label="收益" width="150" sortable align="right">
            <template #default="{ row }">
              <span
                class="font-mono-number"
                :class="getProfitClass(row.profit)"
              >
                {{ row.profit >= 0 ? '+' : '' }}¥{{ formatNumber(row.profit) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column prop="profit_rate" label="收益率" width="120" sortable align="right">
            <template #default="{ row }">
              <span
                class="font-mono-number font-bold"
                :class="getProfitClass(row.profit_rate)"
              >
                {{ row.profit_rate >= 0 ? '+' : '' }}{{ formatNumber(row.profit_rate, 2) }}%
              </span>
            </template>
          </el-table-column>

          <el-table-column prop="daily_profit_rate" label="今日收益" width="120" sortable align="right">
            <template #default="{ row }">
              <span
                v-if="row.daily_profit_rate !== null && row.daily_profit_rate !== undefined"
                class="font-mono-number"
                :class="getProfitClass(row.daily_profit_rate)"
              >
                {{ row.daily_profit_rate >= 0 ? '+' : '' }}{{ formatNumber(row.daily_profit_rate, 2) }}%
              </span>
              <span v-else class="text-gray-500">-</span>
            </template>
          </el-table-column>

          <el-table-column prop="updated_at" label="更新时间" width="180">
            <template #default="{ row }">
              <span class="text-gray-400 text-sm">{{ formatDate(row.updated_at) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="150" fixed="right" align="center">
            <template #default="{ row }">
              <el-button
                link
                type="primary"
                @click="$emit('edit', row)"
                class="action-btn"
              >
                编辑
              </el-button>
              <el-button
                link
                type="danger"
                @click="$emit('delete', row)"
                class="action-btn"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-wrapper mt-4">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="$emit('page-change', $event)"
        @size-change="$emit('page-size-change', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { formatNumber, formatDate } from '@/utils/helpers'

defineProps({
  holdings: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 20
  },
  total: {
    type: Number,
    default: 0
  }
})

defineEmits(['edit', 'delete', 'page-change', 'page-size-change', 'sort-change'])

const handleSortChange = ({ prop, order }) => {
  // Map prop to backend field names if needed
  const fieldMap = {
    'fund.fund_code': 'fund_code',
    'fund.fund_name': 'fund_name',
    'amount': 'amount',
    'cost': 'cost',
    'profit': 'profit',
    'profit_rate': 'profit_rate',
    'daily_profit_rate': 'daily_profit_rate'
  }
  emit('sort-change', { prop: fieldMap[prop] || prop, order })
}

const getProfitClass = (value) => {
  if (value > 0) return 'profit-positive'
  if (value < 0) return 'profit-negative'
  return 'profit-neutral'
}
</script>

<style scoped>
.holdings-table-container {
  margin-bottom: 24px;
}

.glass-card {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 12px;
}

.table-wrapper {
  min-height: 200px;
}

.holdings-table {
  background: transparent;
}

.holdings-table :deep(.el-table__header-wrapper) {
  background: rgba(15, 23, 42, 0.6);
}

.holdings-table :deep(.el-table__header th) {
  background: transparent;
  color: #94a3b8;
  font-weight: 600;
  border-bottom: 1px solid rgba(6, 182, 212, 0.2);
}

.holdings-table :deep(.el-table__body tr) {
  background: transparent;
  transition: all 0.2s ease;
}

.holdings-table :deep(.el-table__body tr:hover > td) {
  background: rgba(6, 182, 212, 0.05) !important;
}

.holdings-table :deep(.el-table__body td) {
  border-bottom: 1px solid rgba(6, 182, 212, 0.1);
  color: #e2e8f0;
}

.holdings-table :deep(.el-table__empty-block) {
  background: transparent;
}

.holdings-table :deep(.el-table__empty-text) {
  color: #94a3b8;
}

/* Sort icon styles */
.holdings-table :deep(.caret-wrapper) {
  color: rgba(6, 182, 212, 0.5);
}

.holdings-table :deep(.ascending .sort-caret.ascending) {
  border-bottom-color: #00d4ff;
}

.holdings-table :deep(.descending .sort-caret.descending) {
  border-top-color: #00d4ff;
}

.fund-name-link {
  color: #e2e8f0;
  text-decoration: none;
  transition: color 0.2s;
}

.fund-name-link:hover {
  color: #00d4ff;
}

.action-btn {
  font-weight: 500;
}

.profit-positive {
  color: #22c55e;
}

.profit-negative {
  color: #ef4444;
}

.profit-neutral {
  color: #9ca3af;
}

.font-mono-number {
  font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
  font-feature-settings: 'tnum';
  font-variant-numeric: tabular-nums;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

.pagination-wrapper :deep(.el-pagination) {
  color: #94a3b8;
}

.pagination-wrapper :deep(.el-pagination .el-pager li) {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(6, 182, 212, 0.2);
  color: #94a3b8;
}

.pagination-wrapper :deep(.el-pagination .el-pager li:hover) {
  border-color: rgba(0, 212, 255, 0.5);
  color: #00d4ff;
}

.pagination-wrapper :deep(.el-pagination .el-pager li.is-active) {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  color: #00d4ff;
}

.pagination-wrapper :deep(.btn-prev),
.pagination-wrapper :deep(.btn-next) {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(6, 182, 212, 0.2);
  color: #94a3b8;
}

.pagination-wrapper :deep(.btn-prev:hover),
.pagination-wrapper :deep(.btn-next:hover) {
  border-color: rgba(0, 212, 255, 0.5);
  color: #00d4ff;
}
</style>
