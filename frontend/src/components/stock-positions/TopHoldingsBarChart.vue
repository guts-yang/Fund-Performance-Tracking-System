<template>
  <div ref="chartRef" style="height: 350px;"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  positions: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value || !props.positions || props.positions.length === 0) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const top10 = props.positions.slice(0, 10)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(6, 182, 212, 0.3)',
      borderWidth: 1,
      textStyle: { color: '#e2e8f0' },
      formatter: (params) => {
        const data = params[0]
        const pos = top10[data.dataIndex]
        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 4px;">${data.name}</div>
            <div>占净值比例: ${data.value}%</div>
            <div>持仓市值: ¥${pos.market_value ? (pos.market_value / 10000).toFixed(2) : '-'}万</div>
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '占净值比例(%)',
      nameTextStyle: { color: '#94a3b8' },
      axisLine: { lineStyle: { color: 'rgba(6, 182, 212, 0.3)' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: 'rgba(6, 182, 212, 0.1)' } }
    },
    yAxis: {
      type: 'category',
      data: top10.map(p => p.stock_name || p.stock_code).reverse(),
      axisLine: { lineStyle: { color: 'rgba(6, 182, 212, 0.3)' } },
      axisLabel: {
        color: '#94a3b8',
        interval: 0
      }
    },
    series: [{
      type: 'bar',
      data: top10.map(p => (p.weight * 100).toFixed(2)).reverse(),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#06b6d4' },
          { offset: 1, color: '#22d3ee' }
        ]),
        borderRadius: [0, 4, 4, 0]
      },
      barWidth: '60%',
      label: {
        show: true,
        position: 'right',
        color: '#e2e8f0',
        formatter: '{c}%'
      }
    }]
  }

  chart.setOption(option)
}

// Watch for data changes
watch(() => props.positions, () => {
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
