<template>
  <el-row :gutter="20" class="charts-section mb-6">
    <!-- Asset Allocation Pie Chart -->
    <el-col :span="12">
      <asset-allocation-pie :holdings="holdings" />
    </el-col>

    <!-- Profit Comparison Bar Chart -->
    <el-col :span="12">
      <profit-comparison-bar :holdings="holdings" />
    </el-col>

    <!-- Profit/Loss Distribution Chart -->
    <el-col :span="24" class="mt-5">
      <profit-loss-distribution :holdings="holdings" />
    </el-col>
  </el-row>
</template>

<script setup>
import AssetAllocationPie from './AssetAllocationPie.vue'
import ProfitComparisonBar from './ProfitComparisonBar.vue'
import ProfitLossDistribution from './ProfitLossDistribution.vue'

defineProps({
  holdings: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.charts-section {
  margin-bottom: 24px;
}
</style>
