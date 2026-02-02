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

    <!-- 新增：实时涨跌幅卡片 -->
    <el-row :gutter="20" style="margin-top: 20px;" v-if="fund">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>
                {{ realtimeData?.is_listed_fund ? '实时股价' : '实时估值' }}
              </span>
              <div>
                <el-tag v-if="realtimeData?.is_listed_fund" type="warning" style="margin-right: 10px;">
                  场内基金
                </el-tag>
                <el-tag v-else type="info" style="margin-right: 10px;">
                  场外基金
                </el-tag>
                <el-tag v-if="realtimeData?.is_trading_time" type="success" style="margin-right: 10px;">盘中实时</el-tag>
                <el-tag v-else type="info">非交易时间</el-tag>
                <el-button @click="toggleAutoRefresh" style="margin-left: 10px;">
                  {{ autoRefresh ? '关闭自动刷新' : '开启自动刷新' }}
                </el-button>
              </div>
            </div>
          </template>
          <div v-if="realtimeData && (realtimeData.increase_rate !== null || realtimeData.current_price)">
            <el-descriptions :column="2" border>

              <!-- 场内基金：显示实时股价 -->
              <el-descriptions-item v-if="realtimeData.is_listed_fund" label="实时股价">
                <span :class="realtimeData.increase_rate >= 0 ? 'text-red' : 'text-green'" style="font-size: 28px; font-weight: bold;">
                  ¥{{ formatNumber(realtimeData.current_price, 4) }}
                </span>
              </el-descriptions-item>

              <!-- 场外基金：显示估算涨跌幅 -->
              <el-descriptions-item v-else label="估算涨跌幅">
                <span :class="realtimeData.increase_rate >= 0 ? 'text-red' : 'text-green'" style="font-size: 28px; font-weight: bold;">
                  {{ realtimeData.increase_rate >= 0 ? '+' : '' }}{{ formatNumber(realtimeData.increase_rate, 2) }}%
                </span>
              </el-descriptions-item>

              <el-descriptions-item label="涨跌幅">
                <span :class="realtimeData.increase_rate >= 0 ? 'text-red' : 'text-green'" style="font-size: 20px; font-weight: bold;">
                  {{ realtimeData.increase_rate >= 0 ? '+' : '' }}{{ formatNumber(realtimeData.increase_rate, 2) }}%
                </span>
                <div style="font-size: 12px; color: #909399; margin-top: 5px;">
                  {{ realtimeData.is_listed_fund ? '实际涨跌' : '估算涨跌' }}
                </div>
              </el-descriptions-item>

              <el-descriptions-item label="数据更新时间">
                {{ formatDateTime(realtimeData.estimate_time) }}
              </el-descriptions-item>

              <el-descriptions-item label="最新正式净值">
                <span v-if="realtimeData.latest_nav_unit_nav">
                  ¥{{ formatNumber(realtimeData.latest_nav_unit_nav, 4) }}
                  <span style="color: #909399; font-size: 12px; margin-left: 5px;">
                    ({{ formatDate(realtimeData.latest_nav_date) }})
                  </span>
                </span>
                <span v-else>-</span>
              </el-descriptions-item>

              <el-descriptions-item label="自动刷新">
                <el-tag :type="autoRefresh ? 'success' : 'info'">
                  {{ autoRefresh ? '已开启 (每60秒)' : '已关闭' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
          <el-empty v-else description="当前非交易时间，暂无实时数据" />
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { getFund, getHolding, getLatestNav, getPnLChartData, syncFund, getRealtimeValuation } from '@/api/fund'
import dayjs from 'dayjs'
import { Refresh } from '@element-plus/icons-vue'

const route = useRoute()
const fundId = ref(route.params.id)

const fund = ref(null)
const holding = ref(null)
const latestNav = ref(null)
const realtimeData = ref(null)
const loading = ref(false)
const syncing = ref(false)
const chartRef = ref(null)

// 自动刷新相关
const autoRefresh = ref(true)
const refreshInterval = ref(null)

const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined || isNaN(num)) return '0.00'
  return Number(num).toFixed(decimals)
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

const formatDateTime = (datetime) => {
  return dayjs(datetime).format('YYYY-MM-DD HH:mm:ss')
}

const fetchData = async () => {
  loading.value = true
  try {
    fund.value = await getFund(fundId.value)
    holding.value = await getHolding(fundId.value).catch(() => null)
    latestNav.value = await getLatestNav(fund.value.fund_code).catch(() => null)
    await fetchRealtimeData()
    await initChart()
  } finally {
    loading.value = false
  }
}

const fetchRealtimeData = async () => {
  if (!fund.value) return
  try {
    const data = await getRealtimeValuation(fund.value.fund_code)
    realtimeData.value = data
  } catch (error) {
    // 非交易时间或获取失败时保持原有数据或设为null
    console.error('获取实时估值失败:', error)
  }
}

const getDiffClass = (data) => {
  if (!data.latest_nav_unit_nav || !data.realtime_nav) return ''
  const diff = data.realtime_nav - data.latest_nav_unit_nav
  return diff > 0 ? 'text-red' : diff < 0 ? 'text-green' : ''
}

const getDiffPercent = (data) => {
  if (!data.latest_nav_unit_nav || !data.realtime_nav) return '0.00'
  const diff = data.realtime_nav - data.latest_nav_unit_nav
  const percent = (diff / data.latest_nav_unit_nav) * 100
  return (percent >= 0 ? '+' : '') + percent.toFixed(2)
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  // 每60秒刷新一次
  refreshInterval.value = setInterval(() => {
    fetchRealtimeData()
  }, 60000)
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
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
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
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
