<template>
  <div class="charts-container mb-6">
    <el-row :gutter="20">
      <!-- 饼图 -->
      <el-col :span="12">
        <div class="glass-card p-6 card-hover">
          <div class="card-header flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <span class="text-sci-cyan text-lg">🥧</span>
              <h3 class="text-lg font-semibold text-white">持仓占比分析</h3>
            </div>
            <el-radio-group v-model="chartMode" size="small">
              <el-radio-button label="top10">Top 10</el-radio-button>
              <el-radio-button label="top20">Top 20</el-radio-button>
            </el-radio-group>
          </div>
          <holdings-pie-chart :positions="positions" :mode="chartMode" />
        </div>
      </el-col>

      <!-- 柱状图 -->
      <el-col :span="12">
        <div class="glass-card p-6 card-hover">
          <div class="card-header flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <span class="text-sci-gold text-lg">📊</span>
              <h3 class="text-lg font-semibold text-white">Top 10 重仓股</h3>
            </div>
          </div>
          <top-holdings-bar-chart :positions="positions" />
        </div>
      </el-col>

      <!-- 集中度分析 -->
      <el-col :span="24">
        <div class="glass-card p-6 card-hover mt-6">
          <div class="card-header flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <span class="text-sci-success text-lg">🎯</span>
              <h3 class="text-lg font-semibold text-white">持仓集中度分析</h3>
            </div>
          </div>
          <concentration-chart :positions="positions" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import HoldingsPieChart from './HoldingsPieChart.vue'
import TopHoldingsBarChart from './TopHoldingsBarChart.vue'
import ConcentrationChart from './ConcentrationChart.vue'

defineProps({
  positions: {
    type: Array,
    default: () => []
  }
})

const chartMode = ref('top10')
</script>

<style scoped>
.charts-container {
  margin-bottom: 24px;
}

.glass-card {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(6, 182, 212, 0.15);
  border-color: rgba(6, 182, 212, 0.4);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
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
</style>
