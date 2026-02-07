<template>
  <div class="profit-comparison-bar glass-card p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-white">收益对比</h3>
      <el-select v-model="sortBy" size="small" style="width: 140px">
        <el-option label="按收益金额" value="profit" />
        <el-option label="按收益率" value="profit_rate" />
      </el-select>
    </div>
    <div ref="chartRef" style="height: 320px;"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  holdings: {
    type: Array,
    default: () => []
  }
})

const sortBy = ref('profit')
const chartRef = ref(null)
let chart = null

const sortedHoldings = computed(() => {
  if (!props.holdings || props.holdings.length === 0) return []

  const data = [...props.holdings].map(h => ({
    fundCode: h.fund.fund_code,
    fundName: h.fund.fund_name,
    profit: h.profit || 0,
    profitRate: h.profit_rate || 0
  }))

  // Sort by selected field
  data.sort((a, b) => {
    const aValue = sortBy.value === 'profit' ? a.profit : a.profitRate
    const bValue = sortBy.value === 'profit' ? b.profit : b.profitRate
    return Math.abs(bValue) - Math.abs(aValue)
  })

  // Take top 10
  return data.slice(0, 10)
})

const initChart = () => {
  if (!chartRef.value || sortedHoldings.value.length === 0) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const fundNames = sortedHoldings.value.map(h => `${h.fundCode} ${h.fundName}`)
  const profits = sortedHoldings.value.map(h => h.profit)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(6, 182, 212, 0.3)',
      borderWidth: 1,
      textStyle: { color: '#e2e8f0' },
      formatter: (params) => {
        const data = params[0]
        const holding = sortedHoldings.value[data.dataIndex]
        return `
          <div style="padding: 4px;">
            <div style="font-weight: bold; margin-bottom: 4px;">${data.name}</div>
            <div>收益金额: <span style="color: ${holding.profit >= 0 ? '#22c55e' : '#ef4444'}">${holding.profit >= 0 ? '+' : ''}¥${(holding.profit / 10000).toFixed(2)}万</span></div>
            <div>收益率: <span style="color: ${holding.profitRate >= 0 ? '#22c55e' : '#ef4444'}">${holding.profitRate >= 0 ? '+' : ''}${holding.profitRate.toFixed(2)}%</span></div>
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '8%',
      bottom: '3%',
      top: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '收益金额 (¥)',
      nameTextStyle: { color: '#94a3b8' },
      axisLine: { lineStyle: { color: 'rgba(6, 182, 212, 0.3)' } },
      axisLabel: {
        color: '#94a3b8',
        formatter: (value) => {
          if (value >= 10000) return (value / 10000).toFixed(0) + '万'
          return value
        }
      },
      splitLine: { lineStyle: { color: 'rgba(6, 182, 212, 0.1)' } }
    },
    yAxis: {
      type: 'category',
      data: fundNames,
      axisLine: { lineStyle: { color: 'rgba(6, 182, 212, 0.3)' } },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 11,
        width: 120,
        overflow: 'truncate',
        ellipsis: '...'
      }
    },
    series: [{
      type: 'bar',
      data: profits.map(p => ({
        value: p,
        itemStyle: {
          color: p >= 0 ? '#22c55e' : '#ef4444',
          borderRadius: p >= 0 ? [0, 4, 4, 0] : [0, 4, 4, 0]
        }
      })),
      barWidth: '60%',
      label: {
        show: true,
        position: 'right',
        color: '#e2e8f0',
        fontSize: 11,
        formatter: (params) => {
          const value = params.value
          if (Math.abs(value) >= 10000) {
            return (value >= 0 ? '+' : '') + (value / 10000).toFixed(2) + '万'
          }
          return (value >= 0 ? '+' : '') + value.toFixed(0)
        }
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }

  chart.setOption(option)
}

// Watch for data changes
watch(() => props.holdings, () => {
  initChart()
}, { deep: true })

watch(sortBy, () => {
  initChart()
})

// Handle resize
const handleResize = () => {
  if (chart && !chart.isDisposed()) {
    chart.resize()
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chart && !chart.isDisposed()) {
    chart.dispose()
  }
})
</script>

<style scoped>
.profit-comparison-bar {
  border-radius: 12px;
  height: 100%;
}

.glass-card {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(6, 182, 212, 0.2);
}
</style>
