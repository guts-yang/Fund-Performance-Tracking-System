<template>
  <div class="stats-container mb-6" v-if="!loading && positions.length > 0">
    <el-row :gutter="20">
      <!-- 持仓股票数 -->
      <el-col :span="4.8">
        <div class="stat-card glass-card p-5 card-hover">
          <div class="flex items-center space-x-2 mb-3">
            <span class="text-2xl">📊</span>
            <span class="text-gray-400 text-sm">持仓股票数</span>
          </div>
          <div class="stat-value text-3xl font-bold font-mono-number text-sci-cyan">
            {{ stats.totalStocks }}
          </div>
          <div class="text-sm text-gray-400 mt-1">只</div>
        </div>
      </el-col>

      <!-- 持仓总市值 -->
      <el-col :span="4.8">
        <div class="stat-card glass-card p-5 card-hover">
          <div class="flex items-center space-x-2 mb-3">
            <span class="text-2xl">💰</span>
            <span class="text-gray-400 text-sm">持仓总市值</span>
          </div>
          <div class="stat-value text-3xl font-bold font-mono-number text-sci-gold">
            ¥{{ formatNumber(stats.totalMarketValue) }}
          </div>
          <div class="text-sm text-gray-400 mt-1">万元</div>
        </div>
      </el-col>

      <!-- 平均持仓占比 -->
      <el-col :span="4.8">
        <div class="stat-card glass-card p-5 card-hover">
          <div class="flex items-center space-x-2 mb-3">
            <span class="text-2xl">📈</span>
            <span class="text-gray-400 text-sm">平均持仓占比</span>
          </div>
          <div class="stat-value text-3xl font-bold font-mono-number" :class="getAverageColor(stats.avgWeight)">
            {{ stats.avgWeight }}%
          </div>
          <div class="text-sm text-gray-400 mt-1">占净值</div>
        </div>
      </el-col>

      <!-- Top10占比 -->
      <el-col :span="4.8">
        <div class="stat-card glass-card p-5 card-hover">
          <div class="flex items-center space-x-2 mb-3">
            <span class="text-2xl">🏆</span>
            <span class="text-gray-400 text-sm">Top10占比</span>
          </div>
          <div class="stat-value text-3xl font-bold font-mono-number text-sci-success">
            {{ stats.top10Weight }}%
          </div>
          <div class="text-sm text-gray-400 mt-1">集中度</div>
        </div>
      </el-col>

      <!-- 最新报告期 -->
      <el-col :span="4.8">
        <div class="stat-card glass-card p-5 card-hover">
          <div class="flex items-center space-x-2 mb-3">
            <span class="text-2xl">📅</span>
            <span class="text-gray-400 text-sm">最新报告期</span>
          </div>
          <div class="stat-value text-xl font-bold font-mono-number text-white">
            {{ stats.latestReportDate }}
          </div>
          <div class="text-sm text-gray-400 mt-1">季度</div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatNumber } from '@/utils/helpers'

const props = defineProps({
  positions: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// 计算统计数据
const stats = computed(() => {
  if (!props.positions || props.positions.length === 0) {
    return {
      totalStocks: 0,
      totalMarketValue: 0,
      avgWeight: '0.00',
      top10Weight: '0.00',
      latestReportDate: '-'
    }
  }

  // 持仓股票总数（去重，按股票代码）
  const uniqueStocks = new Set(props.positions.map(p => p.stock_code))
  const totalStocks = uniqueStocks.size

  // 持仓总市值（单位：万元）
  const totalMarketValue = props.positions.reduce((sum, p) => {
    return sum + (p.market_value || 0)
  }, 0) / 10000

  // 平均持仓占比
  const positionsWithWeight = props.positions.filter(p => p.weight)
  const avgWeight = positionsWithWeight.length > 0
    ? (positionsWithWeight.reduce((sum, p) => sum + p.weight, 0) / positionsWithWeight.length * 100).toFixed(2)
    : '0.00'

  // Top10占比
  const top10 = props.positions.slice(0, 10)
  const top10Weight = top10.length > 0
    ? (top10.reduce((sum, p) => sum + (p.weight || 0), 0) * 100).toFixed(2)
    : '0.00'

  // 最新报告期
  const reportDates = props.positions
    .map(p => p.report_date)
    .filter(d => d)
    .sort((a, b) => new Date(b) - new Date(a))
  const latestReportDate = reportDates.length > 0
    ? reportDates[0].substring(0, 7) // 只显示 YYYY-MM
    : '-'

  return {
    totalStocks,
    totalMarketValue: totalMarketValue.toFixed(0),
    avgWeight,
    top10Weight,
    latestReportDate
  }
})

// 根据平均值返回颜色
const getAverageColor = (avg) => {
  const num = parseFloat(avg)
  if (num >= 3) return 'text-sci-success'
  if (num >= 1.5) return 'text-sci-gold'
  return 'text-white'
}
</script>

<style scoped>
.stats-container {
  margin-bottom: 24px;
}

.stat-card {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(6, 182, 212, 0.15);
  border-color: rgba(6, 182, 212, 0.4);
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  line-height: 1.2;
}

/* Color variables */
.text-sci-cyan {
  color: #00d4ff;
}

.text-sci-gold {
  color: #ffd700;
}

.text-sci-success {
  color: #ef4444;
}

.text-white {
  color: white;
}

.text-gray-400 {
  color: #9ca3af;
}

.font-mono-number {
  font-family: 'Courier New', Courier, monospace;
  font-variant-numeric: tabular-nums;
}
</style>
