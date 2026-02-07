<template>
  <div class="table-container glass-card p-6">
    <div class="card-header flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-white">持仓明细</h3>
      <span class="text-sm text-gray-400">
        共 {{ pagination.total }} 条记录
      </span>
    </div>

    <el-table
      :data="positions"
      v-loading="loading"
      class="table-sci-fi"
      stripe
      :default-sort="{ prop: 'weight', order: 'descending' }"
      @sort-change="handleSortChange"
    >
      <!-- 基金名称 -->
      <el-table-column prop="fund_name" label="基金名称" width="200">
        <template #default="{ row }">
          <div class="flex items-center space-x-2">
            <span class="text-white">{{ row.fund_name }}</span>
            <el-tag size="small" type="info" class="text-xs">
              {{ row.fund_code }}
            </el-tag>
          </div>
        </template>
      </el-table-column>

      <!-- 股票代码 -->
      <el-table-column prop="stock_code" label="股票代码" width="140">
        <template #default="{ row }">
          <div class="flex items-center space-x-2">
            <span class="font-mono-number text-sci-cyan">{{ row.stock_code }}</span>
            <el-tag v-if="isOverseasStock(row.stock_code)"
                    type="warning"
                    size="small"
                    effect="plain"
                    class="text-xs">
              境外
            </el-tag>
          </div>
        </template>
      </el-table-column>

      <!-- 股票名称 -->
      <el-table-column prop="stock_name" label="股票名称" width="150" />

      <!-- 持仓股数 -->
      <el-table-column prop="shares" label="持仓股数" align="right" sortable>
        <template #default="{ row }">
          <span class="font-mono-number">
            {{ row.shares ? formatNumber(row.shares, 0) : '-' }}
          </span>
        </template>
      </el-table-column>

      <!-- 持仓市值 -->
      <el-table-column prop="market_value" label="持仓市值(元)" align="right" sortable>
        <template #default="{ row }">
          <span class="font-mono-number text-sci-gold">
            ¥{{ row.market_value ? formatNumber(row.market_value) : '-' }}
          </span>
        </template>
      </el-table-column>

      <!-- 占净值比例 -->
      <el-table-column prop="weight" label="占净值比例" align="right" width="130" sortable>
        <template #default="{ row }">
          <div class="flex items-center justify-end space-x-2">
            <span v-if="row.weight" class="font-mono-number font-bold">
              {{ (row.weight * 100).toFixed(2) }}%
            </span>
            <span v-else class="text-gray-500 text-xs">-</span>
            <div v-if="row.weight" class="w-12 h-1.5 bg-gray-700 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full"
                :class="getWeightBarColor(row.weight)"
                :style="{ width: Math.min(row.weight * 100, 100) + '%' }"
              ></div>
            </div>
          </div>
        </template>
      </el-table-column>

      <!-- 报告期 -->
      <el-table-column prop="report_date" label="报告期" width="120" sortable>
        <template #default="{ row }">
          <span class="text-gray-300">
            {{ row.report_date || '-' }}
          </span>
        </template>
      </el-table-column>

      <!-- 操作 -->
      <el-table-column label="操作" width="100" align="center" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            link
            size="small"
            @click="goToFundDetail(row.fund_id)"
          >
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="flex justify-center mt-6" v-if="pagination.total > pagination.pageSize">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        :page-size="pagination.pageSize"
        :total="pagination.total"
        layout="total, prev, pager, next, jumper"
        @current-change="handlePageChange"
        background
      />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { formatNumber } from '@/utils/helpers'

const props = defineProps({
  positions: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  pagination: {
    type: Object,
    default: () => ({
      currentPage: 1,
      pageSize: 20,
      total: 0
    })
  }
})

const emit = defineEmits(['pageChange', 'sortChange'])

const router = useRouter()

// 判断是否为海外股票
const isOverseasStock = (stockCode) => {
  if (!stockCode) return false
  return !stockCode.endsWith('.SZ') && !stockCode.endsWith('.SH')
}

// 根据权重返回进度条颜色
const getWeightBarColor = (weight) => {
  const percentage = weight * 100
  if (percentage >= 5) return 'bg-sci-gold'
  if (percentage >= 2) return 'bg-sci-cyan'
  return 'bg-gray-500'
}

// 跳转到基金详情
const goToFundDetail = (fundId) => {
  router.push({ name: 'FundDetail', params: { id: fundId } })
}

// 处理分页变化
const handlePageChange = (page) => {
  emit('pageChange', page)
}

// 处理排序变化
const handleSortChange = ({ prop, order }) => {
  emit('sortChange', { prop, order })
}
</script>

<style scoped>
.table-container {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 12px;
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.font-mono-number {
  font-family: 'Courier New', Courier, monospace;
  font-variant-numeric: tabular-nums;
}

/* Color classes */
.text-sci-cyan {
  color: #00d4ff;
}

.text-sci-gold {
  color: #ffd700;
}

.text-white {
  color: white;
}

.text-gray-300 {
  color: #d1d5db;
}

.text-gray-500 {
  color: #6b7280;
}

.text-gray-400 {
  color: #9ca3af;
}

/* Progress bar colors */
.bg-sci-gold {
  background-color: #ffd700;
}

.bg-sci-cyan {
  background-color: #00d4ff;
}

.bg-gray-500 {
  background-color: #6b7280;
}

.bg-gray-700 {
  background-color: #374151;
}

/* Table styles */
:deep(.el-table) {
  background: transparent;
  color: #e2e8f0;
}

:deep(.el-table tr) {
  background: transparent;
}

:deep(.el-table th.el-table__cell) {
  background: rgba(30, 41, 59, 0.5);
  color: #94a3b8;
  border-color: rgba(6, 182, 212, 0.1);
}

:deep(.el-table td.el-table__cell) {
  border-color: rgba(6, 182, 212, 0.1);
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(30, 41, 59, 0.3);
}

:deep(.el-table__body tr:hover > td) {
  background: rgba(6, 182, 212, 0.1) !important;
}

:deep(.el-table__empty-block) {
  background: transparent;
}

:deep(.el-pagination) {
  --el-pagination-text-color: #9ca3af;
  --el-pagination-bg-color: transparent;
  --el-pagination-button-bg-color: rgba(30, 41, 59, 0.5);
  --el-pagination-button-color: #e2e8f0;
  --el-pagination-hover-color: #00d4ff;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: #00d4ff;
}
</style>
