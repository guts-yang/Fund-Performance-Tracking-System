<template>
  <el-row :gutter="20" class="stats-row mb-6">
    <!-- Total Assets Card -->
    <el-col :span="6">
      <div class="stat-card glass-card card-hover p-6">
        <div class="flex items-center justify-between mb-3">
          <div class="stat-label text-sm text-gray-400 flex items-center font-modern uppercase tracking-wider">
            <span class="w-2 h-2 bg-sci-gold rounded-full mr-2 animate-pulse"></span>
            总资产
          </div>
          <div class="stat-icon w-10 h-10 flex items-center justify-center
                      bg-sci-gold/10 border border-sci-gold/40 rounded-lg">
            <span class="text-sci-gold text-lg">💰</span>
          </div>
        </div>
        <div class="stat-value text-sci-gold font-data text-glow-gold-enhanced text-2xl font-bold">
          ¥{{ formatNumber(totalMarketValue) }}
        </div>
      </div>
    </el-col>

    <!-- Total Profit Card -->
    <el-col :span="6">
      <div class="stat-card glass-card card-hover p-6"
           :class="getProfitBgClass(totalProfit)">
        <div class="flex items-center justify-between mb-3">
          <div class="stat-label text-sm text-gray-400 flex items-center font-modern uppercase tracking-wider">
            <span class="w-2 h-2 rounded-full mr-2 animate-pulse"
                  :class="totalProfit >= 0 ? 'bg-sci-success' : 'bg-sci-danger'"></span>
            总收益
          </div>
          <div class="stat-icon w-10 h-10 flex items-center justify-center bg-navy-800/60 rounded-lg"
               :style="'border: 1px solid ' + (totalProfit >= 0 ? 'rgba(34, 197, 94, 0.4)' : 'rgba(239, 68, 68, 0.4)')">
            <span class="text-lg" :class="totalProfit >= 0 ? 'text-sci-success' : 'text-sci-danger'">
              {{ totalProfit >= 0 ? '📈' : '📉' }}
            </span>
          </div>
        </div>
        <div class="stat-value font-data text-2xl font-bold"
             :class="getProfitClass(totalProfit)">
          {{ totalProfit >= 0 ? '+' : '' }}¥{{ formatNumber(totalProfit) }}
        </div>
      </div>
    </el-col>

    <!-- Total Profit Rate Card -->
    <el-col :span="6">
      <div class="stat-card glass-card card-hover p-6"
           :class="getProfitBgClass(totalProfitRate)">
        <div class="flex items-center justify-between mb-3">
          <div class="stat-label text-sm text-gray-400 flex items-center font-modern uppercase tracking-wider">
            <span class="w-2 h-2 rounded-full mr-2 animate-pulse"
                  :class="totalProfitRate >= 0 ? 'bg-sci-success' : 'bg-sci-danger'"></span>
            总收益率
          </div>
          <div class="stat-icon w-10 h-10 flex items-center justify-center bg-navy-800/60 rounded-lg"
               :style="'border: 1px solid ' + (totalProfitRate >= 0 ? 'rgba(34, 197, 94, 0.4)' : 'rgba(239, 68, 68, 0.4)')">
            <span class="text-lg" :class="totalProfitRate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
              📊
            </span>
          </div>
        </div>
        <div class="stat-value font-data text-2xl font-bold"
             :class="getProfitClass(totalProfitRate)">
          {{ totalProfitRate >= 0 ? '+' : '' }}{{ formatNumber(totalProfitRate, 2) }}%
        </div>
      </div>
    </el-col>

    <!-- Profitable Funds Card -->
    <el-col :span="6">
      <div class="stat-card glass-card card-hover p-6">
        <div class="flex items-center justify-between mb-3">
          <div class="stat-label text-sm text-gray-400 flex items-center font-modern uppercase tracking-wider">
            <span class="w-2 h-2 bg-sci-success rounded-full mr-2 animate-pulse"></span>
            盈利基金
          </div>
          <div class="stat-icon w-10 h-10 flex items-center justify-center
                      bg-sci-success/10 border border-sci-success/40 rounded-lg">
            <span class="text-sci-success text-lg">✓</span>
          </div>
        </div>
        <div class="stat-value text-sci-success font-data text-2xl font-bold">
          {{ profitableFunds }} <span class="text-gray-500 text-lg">/ {{ totalFunds }}</span>
        </div>
        <div class="text-xs text-gray-400 mt-1">
          盈利率: {{ totalFunds > 0 ? ((profitableFunds / totalFunds) * 100).toFixed(1) : 0 }}%
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script setup>
import { computed } from 'vue'
import { formatNumber } from '@/utils/helpers'

const props = defineProps({
  holdings: {
    type: Array,
    default: () => []
  }
})

// Calculate total market value
const totalMarketValue = computed(() => {
  if (!props.holdings || props.holdings.length === 0) return 0
  return props.holdings.reduce((sum, h) => sum + (h.market_value || h.amount || 0), 0)
})

// Calculate total profit
const totalProfit = computed(() => {
  if (!props.holdings || props.holdings.length === 0) return 0
  return props.holdings.reduce((sum, h) => sum + (h.profit || 0), 0)
})

// Calculate total profit rate
const totalProfitRate = computed(() => {
  const totalCost = props.holdings?.reduce((sum, h) => sum + (h.cost || 0), 0) || 0
  if (totalCost === 0) return 0
  return (totalProfit.value / totalCost) * 100
})

// Count profitable funds
const profitableFunds = computed(() => {
  if (!props.holdings || props.holdings.length === 0) return 0
  return props.holdings.filter(h => (h.profit || 0) > 0).length
})

// Count total funds
const totalFunds = computed(() => {
  return props.holdings?.length || 0
})

// Get profit class for color
const getProfitClass = (value) => {
  if (value > 0) return 'profit-positive'
  if (value < 0) return 'profit-negative'
  return 'profit-neutral'
}

// Get profit background class
const getProfitBgClass = (value) => {
  if (value > 0) return 'profit-bg-positive'
  if (value < 0) return 'profit-bg-negative'
  return ''
}
</script>

<style scoped>
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-hover:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow:
    0 20px 50px rgba(0, 0, 0, 0.6),
    0 0 40px rgba(0, 212, 255, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.stat-label {
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.stat-value {
  font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
  font-feature-settings: 'tnum';
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

/* Enhanced profit/loss colors */
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

.profit-bg-positive {
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.profit-bg-negative {
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.glass-card {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 12px;
}

.text-glow-gold-enhanced {
  text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
}
</style>
