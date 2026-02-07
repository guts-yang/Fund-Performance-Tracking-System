<template>
  <div class="stock-positions-page" v-loading="loading">
    <!-- Page Header -->
    <div class="page-header mb-6">
      <h1 class="page-title text-2xl font-bold text-white mb-2">股票持仓管理</h1>
      <p class="text-gray-400">查看和分析基金的股票持仓情况</p>
    </div>

    <!-- Filters -->
    <stock-positions-filters
      v-model:fundId="selectedFundId"
      v-model:reportDate="selectedReportDate"
      v-model:market="selectedMarket"
      v-model:searchKeyword="searchKeyword"
      :funds="fundsList"
      :reportDates="availableReportDates"
      :loading="loading"
      @sync="handleSync"
      @checkQuality="handleCheckQuality"
    />

    <!-- Stats Cards -->
    <stock-positions-stats
      :positions="filteredPositions"
      :loading="loading"
    />

    <!-- Charts -->
    <stock-positions-charts
      v-if="filteredPositions.length > 0"
      :positions="filteredPositions"
    />

    <!-- Table -->
    <stock-positions-table
      :positions="paginatedPositions"
      :loading="loading"
      :pagination="pagination"
      @page-change="handlePageChange"
      @sort-change="handleSortChange"
    />

    <!-- Empty State -->
    <div v-if="!loading && filteredPositions.length === 0"
         class="glass-card p-12 text-center">
      <div class="text-6xl mb-4">📊</div>
      <h3 class="text-xl font-semibold text-white mb-2">暂无持仓数据</h3>
      <p class="text-gray-400 mb-6">请点击"同步持仓"按钮从 Tushare 获取最新持仓数据</p>
      <button @click="handleSync" class="btn-tech-primary">
        ⟳ 同步持仓
      </button>
    </div>

    <!-- Quality Check Dialog -->
    <el-dialog
      v-model="qualityDialogVisible"
      title="数据质量检查"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="qualityData" class="quality-check">
        <el-row :gutter="20" class="mb-6">
          <el-col :span="12">
            <div class="quality-card p-4 bg-navy-900/30 rounded-lg">
              <div class="text-gray-400 text-sm mb-2">总记录数</div>
              <div class="text-2xl font-bold text-white">{{ qualityData.total }}</div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="quality-card p-4 bg-navy-900/30 rounded-lg">
              <div class="text-gray-400 text-sm mb-2">完整度</div>
              <div class="text-2xl font-bold" :class="qualityData.with_name === qualityData.total ? 'text-sci-success' : 'text-sci-gold'">
                {{ ((qualityData.with_name / qualityData.total) * 100).toFixed(1) }}%
              </div>
            </div>
          </el-col>
        </el-row>

        <div v-if="qualityData.name_issues > 0" class="mb-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-gray-300">发现问题记录</span>
            <span class="text-sci-gold font-bold">{{ qualityData.name_issues }} 条</span>
          </div>
          <el-progress
            :percentage="((qualityData.total - qualityData.name_issues) / qualityData.total * 100)"
            :color="'#00d4ff'"
          />
        </div>

        <div class="info-box p-4 bg-navy-900/30 rounded-lg mb-6">
          <div class="text-sm text-gray-400 mb-1">最新报告期</div>
          <div class="text-lg text-white">{{ qualityData.report_date || '-' }}</div>
          <div class="text-sm text-gray-400 mt-2 mb-1">最后更新</div>
          <div class="text-sm text-gray-300">{{ qualityData.last_update || '-' }}</div>
        </div>
      </div>

      <template #footer>
        <el-button @click="qualityDialogVisible = false">关闭</el-button>
        <el-button
          v-if="qualityData && qualityData.name_issues > 0"
          type="primary"
          @click="handleFixNames"
          :loading="fixingNames"
        >
          一键修复
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getFunds, getFundStockPositions, syncFundStockPositions } from '@/api/fund'
import { useStockPositions } from '@/composables/useStockPositions'
import StockPositionsFilters from '@/components/stock-positions/StockPositionsFilters.vue'
import StockPositionsStats from '@/components/stock-positions/StockPositionsStats.vue'
import StockPositionsTable from '@/components/stock-positions/StockPositionsTable.vue'
import StockPositionsCharts from '@/components/stock-positions/StockPositionsCharts.vue'

// State
const selectedFundId = ref(null)  // null表示所有基金
const selectedReportDate = ref(null)
const selectedMarket = ref('all')
const searchKeyword = ref('')

const qualityDialogVisible = ref(false)
const qualityData = ref(null)
const fixingNames = ref(false)

// Use composable
const {
  fundsList,
  stockPositions,
  loading,
  availableReportDates,
  pagination,
  filteredPositions,
  paginatedPositions,
  fetchAllPositions,
  syncPositions,
  checkQuality,
  fixNames
} = useStockPositions(selectedFundId, selectedReportDate, selectedMarket, searchKeyword)

// Lifecycle
onMounted(() => {
  fetchAllPositions()
})

// Event Handlers
const handleSync = async (fundId) => {
  const targetFundId = fundId || selectedFundId.value
  if (!targetFundId) {
    ElMessage.warning('请先选择基金')
    return
  }

  const success = await syncPositions(targetFundId)
  if (success) {
    await fetchAllPositions()
  }
}

const handleCheckQuality = async () => {
  const fundId = selectedFundId.value
  if (!fundId) {
    ElMessage.warning('请先选择单个基金')
    return
  }

  const data = await checkQuality(fundId)
  if (data) {
    qualityData.value = data
    qualityDialogVisible.value = true
  }
}

const handleFixNames = async () => {
  const fundId = selectedFundId.value
  if (!fundId) return

  fixingNames.value = true
  try {
    const success = await fixNames(fundId)
    if (success) {
      ElMessage.success('修复成功')
      qualityDialogVisible.value = false
      await fetchAllPositions()
    }
  } finally {
    fixingNames.value = false
  }
}

const handlePageChange = (page) => {
  pagination.value.currentPage = page
}

const handleSortChange = ({ prop, order }) => {
  // Handle sort change
  console.log('Sort changed:', prop, order)
}
</script>

<style scoped>
.stock-positions-page {
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

.quality-check {
  padding: 10px 0;
}

.quality-card {
  background: rgba(15, 23, 42, 0.3);
  border-radius: 8px;
  padding: 16px;
}

.glass-card {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 12px;
}
</style>
