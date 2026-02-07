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
  },
  mode: {
    type: String,
    default: 'top10'
  }
})

const chartRef = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value || !props.positions || props.positions.length === 0) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  // 根据mode获取数据
  let data = [...props.positions]
  if (props.mode === 'top10') {
    data = data.slice(0, 10)
  } else if (props.mode === 'top20') {
    data = data.slice(0, 20)
  }

  const chartData = data.map(p => ({
    name: p.stock_name || p.stock_code,
    value: p.weight ? (p.weight * 100).toFixed(2) : 0
  }))

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(6, 182, 212, 0.3)',
      borderWidth: 1,
      textStyle: { color: '#e2e8f0' },
      formatter: '{b}: {c}%'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#94a3b8' },
      type: 'scroll'
    },
    series: [{
      name: '持仓占比',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      data: chartData,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#0f172a',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
          color: '#fff'
        }
      }
    }]
  }

  chart.setOption(option)
}

// Watch for data changes
watch(() => props.positions, () => {
  initChart()
}, { deep: true })

watch(() => props.mode, () => {
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
