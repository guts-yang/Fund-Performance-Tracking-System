<template>
  <div class="dashboard">
    <el-row :gutter="20" class="summary-row">
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="card-content">
            <div class="card-label">总成本</div>
            <div class="card-value">¥{{ formatNumber(summary?.total_cost || 0) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="card-content">
            <div class="card-label">总市值</div>
            <div class="card-value">¥{{ formatNumber(summary?.total_market_value || 0) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="summary-card" :class="getProfitClass(summary?.total_profit)">
          <div class="card-content">
            <div class="card-label">总收益</div>
            <div class="card-value">
              {{ summary?.total_profit >= 0 ? '+' : '' }}¥{{ formatNumber(summary?.total_profit || 0) }}
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="summary-card" :class="getProfitClass(summary?.total_profit_rate)">
          <div class="card-content">
            <div class="card-label">总收益率</div>
            <div class="card-value">
              {{ summary?.total_profit_rate >= 0 ? '+' : '' }}{{ formatNumber(summary?.total_profit_rate || 0, 2) }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="fund-list-card">
      <template #header>
        <div class="card-header">
          <span>我的基金 ({{ summary?.fund_count || 0 }})</span>
          <el-button type="primary" @click="handleSyncAll" :loading="syncing">
            <el-icon><Refresh /></el-icon> 同步数据
          </el-button>
        </div>
      </template>
      <el-table :data="summary?.funds || []" stripe>
        <el-table-column prop="fund_code" label="基金代码" width="120" />
        <el-table-column prop="fund_name" label="基金名称" />
        <el-table-column prop="amount" label="持有金额" align="right">
          <template #default="{ row }">
            ¥{{ formatNumber(row.amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="shares" label="持有份额" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.shares, 4) }}
          </template>
        </el-table-column>
        <el-table-column prop="cost_price" label="成本单价" align="right">
          <template #default="{ row }">
            ¥{{ formatNumber(row.cost_price, 4) }}
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="总成本" align="right">
          <template #default="{ row }">
            ¥{{ formatNumber(row.cost) }}
          </template>
        </el-table-column>
        <el-table-column prop="latest_nav" label="最新净值" align="right">
          <template #default="{ row }">
            ¥{{ formatNumber(row.latest_nav, 4) }}
          </template>
        </el-table-column>
        <el-table-column prop="market_value" label="市值" align="right">
          <template #default="{ row }">
            ¥{{ formatNumber(row.market_value) }}
          </template>
        </el-table-column>
        <el-table-column prop="profit" label="收益" align="right">
          <template #default="{ row }">
            <span :class="getProfitClass(row.profit)">
              {{ row.profit >= 0 ? '+' : '' }}¥{{ formatNumber(row.profit) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_rate" label="收益率" align="right">
          <template #default="{ row }">
            <span :class="getProfitClass(row.profit_rate)">
              {{ row.profit_rate >= 0 ? '+' : '' }}{{ formatNumber(row.profit_rate, 2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="$router.push(`/funds/${row.fund_id}`)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFundStore } from '@/stores/fund'
import { syncAllNav } from '@/api/fund'
import { Refresh } from '@element-plus/icons-vue'

const fundStore = useFundStore()
const syncing = ref(false)

const summary = ref(null)

const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined) return '0.00'
  return Number(num).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const getProfitClass = (value) => {
  if (value > 0) return 'profit-positive'
  if (value < 0) return 'profit-negative'
  return ''
}

onMounted(async () => {
  await fundStore.fetchSummary()
  summary.value = fundStore.summary
})

const handleSyncAll = async () => {
  syncing.value = true
  try {
    await syncAllNav()
    await fundStore.fetchSummary()
    summary.value = fundStore.summary
  } finally {
    syncing.value = false
  }
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.summary-row {
  margin-bottom: 20px;
}

.summary-card {
  border-radius: 8px;
  overflow: hidden;
}

.card-content {
  text-align: center;
}

.card-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.profit-positive .card-value {
  color: #f56c6c;
}

.profit-negative .card-value {
  color: #67c23a;
}

.fund-list-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profit-positive {
  color: #f56c6c;
}

.profit-negative {
  color: #67c23a;
}
</style>
