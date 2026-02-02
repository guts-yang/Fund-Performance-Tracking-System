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
          <div>
            <el-tag v-if="autoRefresh" type="success" style="margin-right: 10px;">
              自动刷新中 ({{ lastUpdateTime ? lastUpdateTime : '--:--:--' }})
            </el-tag>
            <el-button @click="toggleAutoRefresh" style="margin-right: 10px;">
              {{ autoRefresh ? '关闭自动刷新' : '开启自动刷新' }}
            </el-button>
            <el-button type="primary" @click="handleSyncAll" :loading="syncing">
              <el-icon><Refresh /></el-icon> 同步数据
            </el-button>
          </div>
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
        <el-table-column prop="latest_nav" label="最新净值" align="right" width="120">
          <template #default="{ row }">
            <span v-if="row.latest_nav" style="color: #909399; font-size: 12px;">正式</span>
            <div>¥{{ formatNumber(row.latest_nav, 4) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="实时估值" align="right" width="140">
          <template #default="{ row }">
            <div v-if="row.realtime_nav">
              <div :class="row.increase_rate >= 0 ? 'text-red' : 'text-green'" style="font-weight: bold;">
                ¥{{ formatNumber(row.realtime_nav, 4) }}
              </div>
              <div style="font-size: 12px;" :class="row.increase_rate >= 0 ? 'text-red' : 'text-green'">
                {{ row.increase_rate >= 0 ? '+' : '' }}{{ formatNumber(row.increase_rate, 2) }}%
              </div>
            </div>
            <div v-else style="color: #ccc; font-size: 12px;">-</div>
          </template>
        </el-table-column>
        <el-table-column label="市值(实时)" align="right" width="140">
          <template #default="{ row }">
            <span style="font-weight: bold;">
              ¥{{ formatNumber(row.realtime_market_value || row.market_value) }}
            </span>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useFundStore } from '@/stores/fund'
import { syncAllNav, getBatchRealtimeValuation } from '@/api/fund'
import { Refresh } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const fundStore = useFundStore()
const syncing = ref(false)
const summary = ref(null)

// 自动刷新相关
const autoRefresh = ref(true)
const refreshInterval = ref(null)
const lastUpdateTime = ref('')

const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined) return '0.00'
  return Number(num).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const getProfitClass = (value) => {
  if (value > 0) return 'profit-positive'
  if (value < 0) return 'profit-negative'
  return ''
}

const fetchSummaryWithRealtime = async () => {
  await fundStore.fetchSummary()
  summary.value = fundStore.summary

  // 获取实时估值
  if (summary.value?.funds?.length > 0) {
    try {
      const fundCodes = summary.value.funds.map(f => f.fund_code)
      const result = await getBatchRealtimeValuation(fundCodes)

      // 合并实时估值数据并更新市值
      const valuationMap = {}
      result.valuations.forEach(v => {
        valuationMap[v.fund_code] = v
      })

      summary.value.funds.forEach(fund => {
        const valuation = valuationMap[fund.fund_code]
        if (valuation && valuation.realtime_nav) {
          fund.realtime_nav = valuation.realtime_nav
          fund.increase_rate = valuation.increase_rate
          // 使用实时估值计算市值
          fund.realtime_market_value = fund.shares * valuation.realtime_nav
        }
      })

      // 更新总市值（使用实时市值）
      const totalRealtimeMarketValue = summary.value.funds.reduce((sum, fund) => {
        return sum + (fund.realtime_market_value || fund.market_value || 0)
      }, 0)
      summary.value.total_market_value = totalRealtimeMarketValue

      // 更新总收益和收益率
      summary.value.total_profit = totalRealtimeMarketValue - summary.value.total_cost
      summary.value.total_profit_rate = (summary.value.total_profit / summary.value.total_cost) * 100

      lastUpdateTime.value = dayjs().format('HH:mm:ss')
    } catch (error) {
      console.error('获取实时估值失败:', error)
    }
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  refreshInterval.value = setInterval(() => {
    fetchSummaryWithRealtime()
  }, 60000)
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

onMounted(async () => {
  await fetchSummaryWithRealtime()
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})

const handleSyncAll = async () => {
  syncing.value = true
  try {
    await syncAllNav()
    await fetchSummaryWithRealtime()
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

.text-red {
  color: #f56c6c;
}

.text-green {
  color: #67c23a;
}
</style>
