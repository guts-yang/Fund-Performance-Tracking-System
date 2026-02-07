<template>
  <div class="profit-loss-distribution glass-card p-6">
    <h3 class="text-lg font-semibold text-white mb-4">盈亏分布</h3>
    <div ref="chartRef" style="height: 260px;"></div>
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

const chartRef = ref(null)
let chart = null

const totalProfitRate = computed(() => {
  const totalCost = props.holdings?.reduce((sum, h) => sum + (h.cost || 0), 0) || 0
  const totalProfit = props.holdings?.reduce((sum, h) => sum + (h.profit || 0), 0) || 0
  if (totalCost === 0) return 0
  return (totalProfit / totalCost) * 100
})

const distribution = computed(() => {
  if (!props.holdings || props.holdings.length === 0) {
    return [
      { name: '高盈利(>10%)', value: 0, color: '#15803d' },
      { name: '低盈利(0-10%)', value: 0, color: '#22c55e' },
      { name: '低亏损(0~-10%)', value: 0, color: '#f87171' },
      { name: '高亏损(<-10%)', value: 0, color: '#dc2626' }
    ]
  }

  const profit = props.holdings.filter(h => (h.profit || 0) > 0)
  const loss = props.holdings.filter(h => (h.profit || 0) < 0)

  const highProfit = profit.filter(h => (h.profit_rate || 0) > 10).length
  const lowProfit = profit.length - highProfit
  const highLoss = loss.filter(h => (h.profit_rate || 0) < -10).length
  const lowLoss = loss.length - highLoss

  return [
    { name: '高盈利(>10%)', value: highProfit, color: '#15803d' },
    { name: '低盈利(0-10%)', value: lowProfit, color: '#22c55e' },
    { name: '低亏损(0~-10%)', value: lowLoss, color: '#f87171' },
    { name: '高亏损(<-10%)', value: highLoss, color: '#dc2626' }
  ]
})

const initChart = () => {
  if (!chartRef.value || props.holdings.length === 0) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const hasData = distribution.value.some(d => d.value > 0)
  const centerText = hasData
    ? (totalProfitRate.value >= 0 ? '+' : '') + totalProfitRate.value.toFixed(2) + '%'
    : 'N/A'

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(6, 182, 212, 0.3)',
      borderWidth: 1,
      textStyle: { color: '#e2e8f0' },
      formatter: '{b}: {c} 只 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 20,
      top: 'center',
      textStyle: { color: '#94a3b8', fontSize: 12 },
      data: distribution.value.map(d => d.name)
    },
    series: [{
      type: 'pie',
      radius: ['50%', '75%'],
      center: ['35%', '50%'],
      data: distribution.value.map(d => ({
        name: d.name,
        value: d.value,
        itemStyle: {
          color: d.value > 0 ? d.color : '#374151',
          borderRadius: 8,
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
          color: '#fff'
        }
      },
      // Custom center text
      markArea: {
        silent: true,
        label: {
          show: true,
          position: 'inside',
          formatter: () => {
            return [
              '{b|总收益率}',
              `{c|${centerText}}`
            ].join('\n')
          },
          rich: {
            b: {
              fontSize: 12,
              color: '#9ca3af',
              padding: [0, 0, 8, 0]
            },
            c: {
              fontSize: 20,
              fontWeight: 'bold',
              color: totalProfitRate.value >= 0 ? '#22c55e' : '#ef4444',
              fontFamily: 'JetBrains Mono, monospace'
            }
          }
        }
      }
    }]
  }

  // For center text in pie chart, we use graphic component
  option.graphic = {
    type: 'text',
    left: '35%',
    top: '50%',
    style: {
      text: [
        '{b|总收益率}',
        `{c|${centerText}}`
      ].join('\n'),
      textAlign: 'center',
      rich: {
        b: {
          fontSize: 12,
          color: '#9ca3af',
          padding: [0, 0, 8, 0]
        },
        c: {
          fontSize: 20,
          fontWeight: 'bold',
          color: totalProfitRate.value >= 0 ? '#22c55e' : '#ef4444',
          fontFamily: 'JetBrains Mono, monospace'
        }
      }
    }
  }

  chart.setOption(option)
}

// Watch for data changes
watch(() => props.holdings, () => {
  initChart()
}, { deep: true })

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
.profit-loss-distribution {
  border-radius: 12px;
  height: 100%;
}

.glass-card {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(6, 182, 212, 0.2);
}
</style>
