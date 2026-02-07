<template>
  <div class="holding-list-page" v-loading="loading">
    <!-- Page Header -->
    <div class="page-header flex items-center justify-between mb-6">
      <div class="flex items-center space-x-3">
        <span class="text-sci-cyan text-3xl">💼</span>
        <div>
          <h1 class="page-title text-2xl font-bold text-white">用户持仓</h1>
          <p class="text-gray-400 text-sm">查看和管理您的基金持仓</p>
        </div>
      </div>
      <el-button
        type="primary"
        @click="handleSyncAll"
        :loading="syncing"
        class="sync-button"
      >
        <span v-if="!syncing">⟳ 同步数据</span>
        <span v-else>同步中...</span>
      </el-button>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && holdings.length === 0" class="glass-card p-12 text-center">
      <div class="text-6xl mb-4">📊</div>
      <h3 class="text-xl font-semibold text-white mb-2">暂无持仓数据</h3>
      <p class="text-gray-400 mb-6">您还没有添加任何基金持仓</p>
      <router-link to="/funds" class="btn-tech-primary inline-block">
        前往基金列表 →
      </router-link>
    </div>

    <!-- Content -->
    <div v-else>
      <!-- Statistics Cards -->
      <holdings-stats :holdings="holdings" />

      <!-- Filters -->
      <holdings-filters
        v-model:search="searchKeyword"
        v-model:profitFilter="profitFilter"
        v-model:amountRange="amountRange"
        v-model:sortBy="sortBy"
        v-model:sortOrder="sortOrder"
      />

      <!-- Charts -->
      <holdings-charts
        v-if="filteredHoldings.length > 0"
        :holdings="filteredHoldings"
      />

      <!-- Table -->
      <holdings-table
        :holdings="paginatedHoldings"
        :loading="loading"
        :current-page="pagination.currentPage"
        :page-size="pagination.pageSize"
        :total="filteredHoldings.length"
        @edit="handleEdit"
        @delete="handleDelete"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        @sort-change="handleSortChange"
      />
    </div>

    <!-- Edit Dialog -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑持仓"
      width="650px"
      :close-on-click-modal="false"
      class="edit-dialog"
    >
      <el-form :model="holdingForm" label-width="140px" class="edit-form">
        <el-form-item label="基金代码">
          <el-input v-model="currentFund.fund_code" disabled size="large" />
        </el-form-item>
        <el-form-item label="基金名称">
          <el-input v-model="currentFund.fund_name" disabled size="large" />
        </el-form-item>
        <el-form-item label="持有金额">
          <el-input-number
            v-model="holdingForm.amount"
            :precision="2"
            :min="0"
            controls-position="right"
            class="w-full"
            size="large"
          />
        </el-form-item>
        <el-form-item label="总成本">
          <span class="text-2xl font-bold text-sci-cyan font-mono-number">
            ¥{{ formatNumber(holdingForm.amount) }}
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="submitting">
          <span v-if="!submitting">保存</span>
          <span v-else>保存中...</span>
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getHoldings, updateHolding, deleteHolding, syncAllNav } from '@/api/fund'
import { formatNumber, sortArray } from '@/utils/helpers'
import HoldingsStats from '@/components/holdings/HoldingsStats.vue'
import HoldingsFilters from '@/components/holdings/HoldingsFilters.vue'
import HoldingsCharts from '@/components/holdings/HoldingsCharts.vue'
import HoldingsTable from '@/components/holdings/HoldingsTable.vue'

// State
const holdings = ref([])
const loading = ref(false)
const syncing = ref(false)
const editDialogVisible = ref(false)
const submitting = ref(false)

// Filter state
const searchKeyword = ref('')
const profitFilter = ref('')
const amountRange = ref('')
const sortBy = ref('amount')
const sortOrder = ref('desc')
const tableSort = ref({ prop: null, order: null })

// Pagination state
const pagination = ref({
  currentPage: 1,
  pageSize: 20
})

// Form state
const holdingForm = reactive({
  amount: 0,
  shares: 0,
  cost_price: 0
})

const currentFund = ref({
  fund_code: '',
  fund_name: ''
})

const currentFundId = ref(null)

// Filtered and sorted holdings
const filteredHoldings = computed(() => {
  let data = [...holdings.value]

  // Search filter
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter(h =>
      h.fund.fund_code.toLowerCase().includes(keyword) ||
      h.fund.fund_name.toLowerCase().includes(keyword)
    )
  }

  // Profit filter
  if (profitFilter.value === 'profit') {
    data = data.filter(h => (h.profit || 0) > 0)
  } else if (profitFilter.value === 'loss') {
    data = data.filter(h => (h.profit || 0) < 0)
  }

  // Amount range filter
  if (amountRange.value === 'small') {
    data = data.filter(h => (h.amount || 0) < 10000)
  } else if (amountRange.value === 'medium') {
    data = data.filter(h => (h.amount || 0) >= 10000 && (h.amount || 0) <= 100000)
  } else if (amountRange.value === 'large') {
    data = data.filter(h => (h.amount || 0) > 100000)
  }

  // Sort by filter selection
  if (sortBy.value) {
    data = sortArray(data, sortBy.value, sortOrder.value, 'number')
  }

  // Apply table sort if set
  if (tableSort.value.prop) {
    data = sortArray(data, tableSort.value.prop, tableSort.value.order, 'number')
  }

  return data
})

// Paginated holdings
const paginatedHoldings = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  const end = start + pagination.value.pageSize
  return filteredHoldings.value.slice(start, end)
})

// Fetch holdings with error handling
const fetchHoldings = async () => {
  loading.value = true
  try {
    const response = await getHoldings()

    // Validate response
    if (!Array.isArray(response)) {
      console.error('API返回数据格式错误:', response)
      ElMessage.error('数据格式错误，请检查API')
      holdings.value = []
      return
    }

    holdings.value = response

    if (response.length === 0) {
      console.log('暂无持仓数据')
    } else {
      console.log(`成功加载 ${response.length} 条持仓记录`)
    }
  } catch (error) {
    console.error('获取持仓数据失败:', error)
    ElMessage.error(`加载失败: ${error.message || '未知错误'}`)
    holdings.value = []
  } finally {
    loading.value = false
  }
}

// Sync all funds
const handleSyncAll = async () => {
  syncing.value = true
  try {
    await syncAllNav()
    ElMessage.success('同步成功')
    await fetchHoldings()
  } catch (error) {
    console.error('同步失败:', error)
    ElMessage.error('同步失败')
  } finally {
    syncing.value = false
  }
}

// Edit holding
const handleEdit = (holding) => {
  currentFundId.value = holding.fund_id
  currentFund.value = {
    fund_code: holding.fund.fund_code,
    fund_name: holding.fund.fund_name
  }
  holdingForm.amount = Number(holding.amount)
  holdingForm.shares = Number(holding.shares)
  holdingForm.cost_price = Number(holding.cost_price)
  editDialogVisible.value = true
}

// Update holding
const handleUpdate = async () => {
  submitting.value = true
  try {
    await updateHolding(currentFundId.value, holdingForm)
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    await fetchHoldings()
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error('更新失败')
  } finally {
    submitting.value = false
  }
}

// Delete holding
const handleDelete = async (holding) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${holding.fund.fund_name} 的持仓吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteHolding(holding.fund_id)
    ElMessage.success('删除成功')
    await fetchHoldings()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// Page change handler
const handlePageChange = (page) => {
  pagination.value.currentPage = page
}

// Page size change handler
const handlePageSizeChange = (size) => {
  pagination.value.pageSize = size
  pagination.value.currentPage = 1
}

// Sort change handler
const handleSortChange = ({ prop, order }) => {
  tableSort.value = { prop, order }
}

// Lifecycle
onMounted(() => {
  fetchHoldings()
})
</script>

<style scoped>
.holding-list-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  color: white;
}

.sync-button {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(0, 212, 255, 0.1) 100%);
  border: 1px solid rgba(0, 212, 255, 0.5);
  color: #00d4ff;
  font-weight: 500;
}

.sync-button:hover {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.3) 0%, rgba(0, 212, 255, 0.2) 100%);
  border-color: #00d4ff;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
}

.glass-card {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 12px;
}

.edit-dialog :deep(.el-dialog) {
  background-color: rgba(15, 23, 42, 0.98);
  border: 1px solid rgba(0, 212, 255, 0.3);
  backdrop-filter: blur(25px);
}

.edit-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
}

.edit-dialog :deep(.el-dialog__title) {
  color: rgb(243 244 246);
  font-size: 1.25rem;
}

.edit-dialog :deep(.el-dialog__body) {
  color: rgb(209 213 219);
}

.edit-form :deep(.el-form-item__label) {
  color: rgb(209 213 219);
}

.font-mono-number {
  font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
  font-feature-settings: 'tnum';
  font-variant-numeric: tabular-nums;
}

.text-sci-cyan {
  color: #00d4ff;
}
</style>
