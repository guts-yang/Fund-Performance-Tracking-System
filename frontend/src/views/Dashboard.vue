<template>
  <div class="dashboard space-y-8">
    <!-- Summary Cards Row -->
    <el-row :gutter="24" class="summary-row">
      <!-- Total Cost Card -->
      <el-col :span="6" class="summary-col">
        <div class="glass-card-enhanced card-hover p-8 relative">
          <div class="flex items-center justify-between mb-4">
            <div class="card-label text-sm text-gray-400 flex items-center font-modern uppercase tracking-wider">
              <span class="w-2 h-2 bg-sci-cyan rounded-full mr-2 animate-pulse"></span>
              总成本
            </div>
            <div class="card-icon w-10 h-10 flex items-center justify-center
                        bg-sci-cyan/10 border border-sci-cyan/40 rounded-lg
                        shadow-glow-cyan-sm">
              <span class="text-sci-cyan">💰</span>
            </div>
          </div>
          <div class="card-value text-white font-data text-glow-cyan-enhanced">
            ¥{{ formatNumber(summary?.total_cost || 0) }}
          </div>
        </div>
      </el-col>

      <!-- Total Market Value Card -->
      <el-col :span="6" class="summary-col">
        <div class="glass-card-enhanced card-hover p-8 relative">
          <div class="flex items-center justify-between mb-4">
            <div class="card-label text-sm text-gray-400 flex items-center font-modern uppercase tracking-wider">
              <span class="w-2 h-2 bg-sci-gold rounded-full mr-2 animate-pulse"></span>
              总市值
            </div>
            <div class="card-icon w-10 h-10 flex items-center justify-center
                        bg-sci-gold/10 border border-sci-gold/40 rounded-lg
                        shadow-glow-gold-sm">
              <span class="text-sci-gold">📊</span>
            </div>
          </div>
          <div class="card-value text-sci-gold font-data text-glow-gold-enhanced">
            ¥{{ formatNumber(summary?.total_market_value || 0) }}
          </div>
        </div>
      </el-col>

      <!-- Total Profit Card -->
      <el-col :span="6" class="summary-col">
        <div class="glass-card-enhanced card-hover p-6 relative"
             :class="getProfitClass(summary?.total_profit)">
          <div class="flex items-center justify-between mb-4">
            <div class="card-label text-sm text-gray-400 flex items-center font-modern uppercase tracking-wider">
              <span class="w-2 h-2 rounded-full mr-2 animate-pulse"
                    :class="summary?.total_profit >= 0 ? 'bg-sci-success' : 'bg-sci-danger'"></span>
              总收益
            </div>
            <div class="card-icon w-10 h-10 flex items-center justify-center
                        bg-navy-800/60 rounded-lg"
                 :class="summary?.total_profit >= 0 ? 'border-sci-success/40' : 'border-sci-danger/40'"
                 :style="'border: 1px solid ' + (summary?.total_profit >= 0 ? 'rgba(34, 197, 94, 0.4)' : 'rgba(239, 68, 68, 0.4)')">
              <span class="text-lg" :class="summary?.total_profit >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                {{ summary?.total_profit >= 0 ? '📈' : '📉' }}
              </span>
            </div>
          </div>
          <div class="card-value font-data"
               :class="getProfitClass(summary?.total_profit)">
            {{ summary?.total_profit >= 0 ? '+' : '' }}¥{{ formatNumber(summary?.total_profit || 0) }}
          </div>
        </div>
      </el-col>

      <!-- Total Daily Profit Card -->
      <el-col :span="6" class="summary-col">
        <div class="glass-card-enhanced card-hover p-6 relative"
             :class="getProfitClass(totalDailyProfit)">
          <div class="flex items-center justify-between mb-4">
            <div class="card-label text-sm text-gray-400 flex items-center font-modern uppercase tracking-wider">
              <span class="w-2 h-2 rounded-full mr-2 animate-pulse"
                    :class="totalDailyProfit >= 0 ? 'bg-sci-success' : 'bg-sci-danger'"></span>
              当日收益
            </div>
            <div class="card-icon w-10 h-10 flex items-center justify-center
                        bg-navy-800/60 rounded-lg"
                 :style="'border: 1px solid ' + (totalDailyProfit >= 0 ? 'rgba(34, 197, 94, 0.4)' : 'rgba(239, 68, 68, 0.4)')">
              <span class="text-lg" :class="totalDailyProfit >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                📅
              </span>
            </div>
          </div>
          <div class="card-value font-data"
               :class="getProfitClass(totalDailyProfit)">
            {{ totalDailyProfit >= 0 ? '+' : '' }}¥{{ formatNumber(totalDailyProfit) }}
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Fund List Card -->
    <div class="glass-card-enhanced p-8">
      <!-- Card Header -->
      <div class="card-header flex items-center justify-between mb-6">
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-3">
            <span class="text-sci-cyan text-2xl">⚡</span>
            <h3 class="text-xl font-tech font-semibold text-white tracking-wide">我的基金</h3>
          </div>
          <span class="px-3 py-1.5 bg-sci-cyan/15 border border-sci-cyan/40 rounded-lg text-sci-cyan text-sm font-data tracking-wider">
            {{ summary?.fund_count || 0 }}
          </span>
        </div>
        <div class="flex items-center space-x-4">
          <div v-if="autoRefresh" class="flex items-center space-x-2 px-4 py-2
                        bg-sci-success/10 border border-sci-success/40 rounded-lg
                        backdrop-blur-sm">
            <span class="status-pulse w-2 h-2 bg-sci-success rounded-full"></span>
            <span class="text-xs text-sci-success font-data tracking-wider">
              自动刷新中 ({{ lastUpdateTime ? lastUpdateTime : '--:--:--' }})
            </span>
          </div>
          <button @click="toggleAutoRefresh"
                  class="btn-tech text-sm px-4 py-2 font-modern">
            {{ autoRefresh ? '关闭自动刷新' : '开启自动刷新' }}
          </button>
          <button @click="handleSyncAll"
                  :disabled="syncing"
                  class="btn-tech-primary text-sm px-4 py-2 flex items-center space-x-2 font-modern"
                  :class="syncing ? 'opacity-50 cursor-not-allowed' : ''">
            <span v-if="!syncing">⟳</span>
            <span v-else class="animate-spin">⟳</span>
            <span>同步数据</span>
          </button>
        </div>
      </div>

      <!-- Sci-Fi Table -->
      <div class="overflow-x-auto">
        <table class="table-sci-fi">
          <thead>
            <tr>
              <th>基金代码</th>
              <th>基金名称</th>
              <th class="text-right cursor-pointer hover:text-sci-cyan" @click="handleSort('amount', 'number')">
                持有金额
                <span v-if="sortState.key === 'amount'">
                  {{ sortState.order === 'desc' ? '↓' : '↑' }}
                </span>
              </th>
              <th class="text-right">持有份额</th>
              <th class="text-right">成本单价</th>
              <th class="text-right">总成本</th>
              <th class="text-right">最新净值</th>
              <th class="text-right cursor-pointer hover:text-sci-cyan" @click="handleSort('increase_rate', 'number')">
                实时数据
                <span v-if="sortState.key === 'increase_rate'">
                  {{ sortState.order === 'desc' ? '↓' : '↑' }}
                </span>
              </th>
              <th class="text-right">市值(实时)</th>
              <th class="text-right">收益</th>
              <th class="text-right">收益率</th>
              <th class="text-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in sortedFunds" :key="row.fund_id" class="table-row">
              <td class="font-mono-number text-sci-cyan">{{ row.fund_code }}</td>
              <td>{{ row.fund_name }}</td>
              <td class="text-right font-mono-number text-gray-300">¥{{ formatNumber(row.amount) }}</td>
              <td class="text-right font-mono-number text-gray-300">{{ formatNumber(row.shares, 4) }}</td>
              <td class="text-right font-mono-number text-gray-400">¥{{ formatNumber(row.cost_price, 4) }}</td>
              <td class="text-right font-mono-number text-gray-400">¥{{ formatNumber(row.cost) }}</td>
              <td class="text-right">
                <div v-if="row.latest_nav" class="space-y-1">
                  <span class="text-xs text-sci-cyan/60 block">正式</span>
                  <div class="font-mono-number">¥{{ formatNumber(row.latest_nav, 4) }}</div>
                </div>
                <span v-else class="text-gray-500">-</span>
              </td>
              <td class="text-right">
                <!-- 场内基金 -->
                <div v-if="row.is_listed_fund && row.current_price">
                  <span class="tag-tech-gold text-xs">场内</span>
                  <div class="mt-1 font-mono-number font-bold"
                       :class="row.increase_rate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                    ¥{{ formatNumber(row.current_price, 4) }}
                  </div>
                  <div class="text-xs font-mono-number"
                       :class="row.increase_rate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                    {{ row.increase_rate >= 0 ? '+' : '' }}{{ formatNumber(row.increase_rate, 2) }}%
                  </div>
                </div>
                <!-- 场外基金 -->
                <div v-else-if="row.increase_rate !== null">
                  <span class="tag-tech-cyan text-xs">场外</span>
                  <div class="mt-1 font-mono-number text-base font-bold"
                       :class="row.increase_rate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                    {{ row.increase_rate >= 0 ? '+' : '' }}{{ formatNumber(row.increase_rate, 2) }}%
                  </div>
                  <div class="text-xs text-gray-500">估算</div>
                </div>
                <div v-else class="text-gray-500 text-xs">-</div>
              </td>
              <td class="text-right">
                <span class="font-mono-number font-bold text-sci-gold">
                  ¥{{ formatNumber(row.realtime_market_value || row.market_value) }}
                </span>
              </td>
              <td class="text-right">
                <span class="font-mono-number"
                      :class="getProfitClass(row.profit)">
                  {{ row.profit >= 0 ? '+' : '' }}¥{{ formatNumber(row.profit) }}
                </span>
              </td>
              <td class="text-right">
                <span class="font-mono-number"
                      :class="getProfitClass(row.profit_rate)">
                  {{ row.profit_rate >= 0 ? '+' : '' }}{{ formatNumber(row.profit_rate, 2) }}%
                </span>
              </td>
              <td class="text-right">
                <router-link :to="`/funds/${row.fund_id}`"
                             class="text-sci-cyan hover:text-sci-cyan/80 transition-colors">
                  详情 →
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFundStore } from '@/stores/fund'
import { syncAllNav, getBatchRealtimeValuation } from '@/api/fund'
import { formatNumber, sortArray } from '@/utils/helpers'
import dayjs from 'dayjs'

const router = useRouter()
const fundStore = useFundStore()
const syncing = ref(false)
const summary = ref(null)

// 自动刷新相关
const autoRefresh = ref(true)
const refreshInterval = ref(null)
const lastUpdateTime = ref('')

// 排序状态
const sortState = ref({
  key: null,
  order: 'desc',
  type: 'number'
})

// 排序后的基金列表
const sortedFunds = computed(() => {
  if (!sortState.value.key || !summary.value?.funds) {
    return summary.value?.funds || []
  }
  return sortArray(
    summary.value.funds,
    sortState.value.key,
    sortState.value.order,
    sortState.value.type
  )
})

// 排序切换函数
const handleSort = (key, type = 'number') => {
  if (sortState.value.key === key) {
    sortState.value.order = sortState.value.order === 'desc' ? 'asc' : 'desc'
  } else {
    sortState.value.key = key
    sortState.value.order = 'desc'
    sortState.value.type = type
  }
}

// 计算总当日收益（基于实时估值）
const totalDailyProfit = computed(() => {
  if (!summary.value?.funds) return 0

  return summary.value.funds.reduce((total, fund) => {
    // 使用实时市值（如果有），否则使用正式市值
    const realtimeMarketValue = fund.realtime_market_value || fund.market_value || 0
    const cost = fund.cost || 0
    return total + (realtimeMarketValue - cost)
  }, 0)
})

const getProfitClass = (value) => {
  if (value > 0) return 'profit-positive'
  if (value < 0) return 'profit-negative'
  return 'profit-neutral'
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
        if (valuation) {
          fund.is_listed_fund = valuation.is_listed_fund
          fund.increase_rate = valuation.increase_rate
          fund.current_price = valuation.current_price

          // 场内基金使用实时股价计算市值
          if (valuation.is_listed_fund && valuation.current_price) {
            fund.realtime_nav = valuation.current_price
            fund.realtime_market_value = fund.shares * valuation.current_price
          }
          // 场外基金使用估算涨跌幅计算市值
          else if (valuation.increase_rate !== null) {
            fund.realtime_nav = fund.latest_nav * (1 + valuation.increase_rate / 100)
            fund.realtime_market_value = fund.shares * fund.realtime_nav
          }
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
  margin-bottom: 0;
}

.summary-col {
  /* No custom margin - let Element Plus gutter handle spacing */
}

.glass-card-enhanced {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-hover:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow:
    0 20px 50px rgba(0, 0, 0, 0.6),
    0 0 40px rgba(0, 212, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.card-label {
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.card-value {
  font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
  font-feature-settings: 'tnum';
  font-variant-numeric: tabular-nums;
  font-size: 1.75rem;
  line-height: 1.2;
}

/* Enhanced profit/loss colors with new neon palette */
.profit-positive {
  color: #22c55e;
  text-shadow: 0 0 25px rgba(34, 197, 94, 0.6);
}

.profit-negative {
  color: #ef4444;
  text-shadow: 0 0 25px rgba(239, 68, 68, 0.6);
}

.profit-neutral {
  color: #9ca3af;
}

/* Table Row Hover Animation */
.table-row {
  transition: all 0.2s ease;
}

.table-row:hover {
  background: rgba(6, 182, 212, 0.05);
}

/* Responsive */
@media (max-width: 1024px) {
  .summary-col {
    /* Let Element Plus handle spacing */
  }
}

@media (max-width: 768px) {
  .summary-col {
    /* Let Element Plus handle spacing */
  }

  .card-value {
    font-size: 1.25rem;
  }
}
</style>
