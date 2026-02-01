<template>
  <div class="fund-detail" v-loading="loading">
    <el-row :gutter="20" v-if="fund">
      <el-col :span="8">
        <el-card>
          <template #header>基金信息</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="基金代码">{{ fund.fund_code }}</el-descriptions-item>
            <el-descriptions-item label="基金名称">{{ fund.fund_name }}</el-descriptions-item>
            <el-descriptions-item label="基金类型">{{ fund.fund_type }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(fund.created_at) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>持仓信息</template>
          <el-descriptions :column="1" border v-if="holding">
            <el-descriptions-item label="持有金额">¥{{ formatNumber(holding.amount) }}</el-descriptions-item>
            <el-descriptions-item label="持有份额">{{ formatNumber(holding.shares, 4) }}</el-descriptions-item>
            <el-descriptions-item label="成本单价">¥{{ formatNumber(holding.cost_price, 4) }}</el-descriptions-item>
            <el-descriptions-item label="总成本">¥{{ formatNumber(holding.cost) }}</el-descriptions-item>
          </el-descriptions>
          <el-empty v-else description="暂无持仓数据" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>最新净值</template>
          <el-descriptions :column="1" border v-if="latestNav">
            <el-descriptions-item label="净值日期">{{ formatDate(latestNav.date) }}</el-descriptions-item>
            <el-descriptions-item label="单位净值">¥{{ formatNumber(latestNav.unit_nav, 4) }}</el-descriptions-item>
            <el-descriptions-item label="累计净值">¥{{ formatNumber(latestNav.accumulated_nav, 4) }}</el-descriptions-item>
            <el-descriptions-item label="日增长率">
              <span :class="latestNav.daily_growth >= 0 ? 'text-red' : 'text-green'">
                {{ latestNav.daily_growth >= 0 ? '+' : '' }}{{ formatNumber(latestNav.daily_growth * 100, 2) }}%
              </span>
            </el-descriptions-item>
          </el-descriptions>
          <el-empty v-else description="暂无净值数据" />
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>收益趋势</span>
          <el-button type="primary" @click="handleSync" :loading="syncing">
            <el-icon><Refresh /></el-icon> 同步数据
          </el-button>
        </div>
      </template>
      <div ref="chartRef" style="height: 400px;"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { getFund, getHolding, getLatestNav, getPnLChartData, syncFund } from '@/api/fund'
import dayjs from 'dayjs'
import { Refresh } from '@element-plus/icons-vue'

const route = useRoute()
const fundId = ref(route.params.id)

const fund = ref(null)
const holding = ref(null)
const latestNav = ref(null)
const loading = ref(false)
const syncing = ref(false)
const chartRef = ref(null)

const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined) return '0.00'
  return Number(num).toFixed(decimals)
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

const fetchData = async () => {
  loading.value = true
  try {
    fund.value = await getFund(fundId.value)
    holding.value = await getHolding(fundId.value).catch(() => null)
    latestNav.value = await getLatestNav(fund.value.fund_code).catch(() => null)

    await initChart()
  } finally {
    loading.value = false
  }
}

const initChart = async () => {
  if (!chartRef.value) return

  const chartData = await getPnLChartData(fundId.value).catch(() => null)
  if (!chartData) return

  const chart = echarts.init(chartRef.value)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['市值', '收益', '收益率']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.dates
    },
    yAxis: [
      {
        type: 'value',
        name: '金额(元)',
        position: 'left'
      },
      {
        type: 'value',
        name: '收益率(%)',
        position: 'right'
      }
    ],
    series: [
      {
        name: '市值',
        type: 'line',
        data: chartData.market_values,
        smooth: true
      },
      {
        name: '收益',
        type: 'line',
        data: chartData.profits,
        smooth: true
      },
      {
        name: '收益率',
        type: 'line',
        yAxisIndex: 1,
        data: chartData.profit_rates,
        smooth: true
      }
    ]
  }

  chart.setOption(option)
}

const handleSync = async () => {
  syncing.value = true
  try {
    await syncFund(fundId.value)
    await fetchData()
  } finally {
    syncing.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.fund-detail {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-red {
  color: #f56c6c;
}

.text-green {
  color: #67c23a;
}
</style>
