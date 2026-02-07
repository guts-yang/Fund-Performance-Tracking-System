<template>
  <div class="asset-allocation-pie glass-card p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-white">资产配置分布</h3>
      <el-radio-group v-model="mode" size="small" class="mode-selector">
        <el-radio-button label="top10">Top 10</el-radio-button>
        <el-radio-button label="top20">Top 20</el-radio-button>
        <el-radio-button label="all">全部</el-radio-button>
      </el-radio-group>
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

const mode = ref('top10')
const chartRef = ref(null)
let chart = null

const chartData = computed(() => {
  if (!props.holdings || props.holdings.length === 0) return []

  return props.holdings.map(h => ({
    name: `${h.fund.fund_code} - ${h.fund.fund_name}`,
    value: h.market_value || h.amount || 0,
    fundCode: h.fund.fund_code,
    profit: h.profit || 0,
    profitRate: h.profit_rate || 0
  })).sort((a, b) => b.value - a.value)
})

const displayData = computed(() => {
  const data = chartData.value
  if (mode.value === 'top10') return data.slice(0, 10)
  if (mode.value === 'top20') return data.slice(0, 20)
  return data
})

const initChart = () => {
  if (!chartRef.value || displayData.value.length === 0) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const colors = [
    '#00d4ff', '#ffd700', '#22c55e', '#ef4444', '#a855f7',
    '#f97316', '#06b6d4', '#8b5cf6', '#ec4899', '#14b8a6',
    '#f59e0b', '#3b82f6', '#10b981', '#ef4444', '#8b5cf6'
  ]

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(6, 182, 212, 0.3)',
      borderWidth: 1,
      textStyle: { color: '#e2e8f0' },
      formatter: (params) => {
        const data = params.data
        return `
          <div style="padding: 4px;">
            <div style="font-weight: bold; margin-bottom: 4px;">${data.name}</div>
            <div>市值: ¥${(data.value / 10000).toFixed(2)}万</div>
            <div>占比: ${params.percent}%</div>
            <div style="color: ${data.profit >= 0 ? '#22c55e' : '#ef4444'}">
              收益: ${data.profit >= 0 ? '+' : ''}¥${(data.profit / 10000).toFixed(2)}万
            </div>
          </div>
        `
      }
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#94a3b8', fontSize: 11 },
      type: 'scroll',
      pageTextStyle: { color: '#94a3b8' }
    },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['38%', '50%'],
      data: displayData.value.map((item, index) => ({
        ...item,
        itemStyle: {
          color: colors[index % colors.length],
          borderRadius: 10,
          borderColor: '#0f172a',
          borderWidth: 2
        }
      })),
      label: {
        show: false
      },
      labelLine: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
          color: '#fff',
          formatter: '{b}\n{d}%'
        },
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

watch(mode, () => {
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
.asset-allocation-pie {
  border-radius: 12px;
  height: 100%;
}

.glass-card {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(6, 182, 212, 0.2);
}

.mode-selector :deep(.el-radio-button__inner) {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(6, 182, 212, 0.3);
  color: #94a3b8;
}

.mode-selector :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  color: #00d4ff;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}
</style>
