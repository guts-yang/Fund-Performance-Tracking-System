<template>
  <el-row :gutter="20" v-if="positions.length > 0">
    <el-col :span="6" v-for="(metric, key) in metrics" :key="key">
      <div class="concentration-metric p-4 bg-navy-900/30 rounded-lg">
        <div class="text-gray-400 text-sm mb-2">{{ metric.label }}</div>
        <div class="text-2xl font-bold font-mono-number" :class="metric.colorClass">
          {{ metric.value }}
        </div>
        <div class="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all"
               :class="metric.barClass"
               :style="{ width: metric.percentage + '%' }">
          </div>
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  positions: {
    type: Array,
    default: () => []
  }
})

const metrics = computed(() => {
  if (!props.positions || props.positions.length === 0) {
    return {}
  }

  const total = props.positions.reduce((sum, p) => sum + (p.weight || 0), 0)
  const top5 = props.positions.slice(0, 5).reduce((sum, p) => sum + (p.weight || 0), 0)
  const top10 = props.positions.slice(0, 10).reduce((sum, p) => sum + (p.weight || 0), 0)
  const top20 = props.positions.slice(0, 20).reduce((sum, p) => sum + (p.weight || 0), 0)

  // 计算HHI指数（赫芬达尔-赫希曼指数）
  const hhi = props.positions.reduce((sum, p) => {
    const weight = p.weight || 0
    return sum + (weight * weight * 10000)
  }, 0)

  return {
    top5: {
      label: 'Top5 占比',
      value: total > 0 ? ((top5 / total) * 100).toFixed(2) + '%' : '0%',
      percentage: total > 0 ? (top5 / total) * 100 : 0,
      colorClass: 'text-sci-cyan',
      barClass: 'bg-sci-cyan'
    },
    top10: {
      label: 'Top10 占比',
      value: total > 0 ? ((top10 / total) * 100).toFixed(2) + '%' : '0%',
      percentage: total > 0 ? (top10 / total) * 100 : 0,
      colorClass: 'text-sci-gold',
      barClass: 'bg-sci-gold'
    },
    top20: {
      label: 'Top20 占比',
      value: total > 0 ? ((top20 / total) * 100).toFixed(2) + '%' : '0%',
      percentage: total > 0 ? (top20 / total) * 100 : 0,
      colorClass: 'text-sci-success',
      barClass: 'bg-sci-success'
    },
    hhi: {
      label: 'HHI指数',
      value: hhi.toFixed(0),
      percentage: Math.min(hhi / 100, 100),
      colorClass: 'text-white',
      barClass: 'bg-gray-500'
    }
  }
})
</script>

<style scoped>
.concentration-metric {
  background: rgba(15, 23, 42, 0.3);
  border-radius: 8px;
  padding: 16px;
}

.font-mono-number {
  font-family: 'Courier New', Courier, monospace;
  font-variant-numeric: tabular-nums;
}

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

.bg-sci-cyan {
  background-color: #00d4ff;
}

.bg-sci-gold {
  background-color: #ffd700;
}

.bg-sci-success {
  background-color: #ef4444;
}

.bg-gray-500 {
  background-color: #6b7280;
}

.bg-gray-700 {
  background-color: #374151;
}
</style>
