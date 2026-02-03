<template>
  <div class="fund-detail space-y-6" v-loading="loading">
    <!-- Info Cards Row -->
    <el-row :gutter="20" v-if="fund">
      <!-- Fund Info Card -->
      <el-col :span="8" class="info-col">
        <div class="glass-card card-hover p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <span class="text-sci-cyan text-lg">📁</span>
              <h4 class="text-white font-semibold">基金信息</h4>
            </div>
          </div>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-400 text-sm">基金代码</span>
              <span class="font-mono-number text-sci-cyan">{{ fund.fund_code }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400 text-sm">基金名称</span>
              <span class="text-gray-200">{{ fund.fund_name }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400 text-sm">基金类型</span>
              <span class="tag-tech-cyan text-xs">{{ fund.fund_type }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400 text-sm">创建时间</span>
              <span class="text-gray-400 text-sm">{{ formatDate(fund.created_at) }}</span>
            </div>
          </div>
        </div>
      </el-col>

      <!-- Holding Info Card -->
      <el-col :span="8" class="info-col">
        <div class="glass-card card-hover p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <span class="text-sci-gold text-lg">💼</span>
              <h4 class="text-white font-semibold">持仓信息</h4>
            </div>
          </div>
          <div v-if="holding" class="space-y-3">
            <div class="flex justify-between items-center">
              <span class="text-gray-400 text-sm">持有金额</span>
              <span class="font-mono-number text-gray-200">¥{{ formatNumber(holding.amount) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-400 text-sm">持有份额</span>
              <span class="font-mono-number text-gray-200">{{ formatNumber(holding.shares, 4) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-400 text-sm">成本单价</span>
              <span class="font-mono-number text-gray-300">¥{{ formatNumber(holding.cost_price, 4) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-400 text-sm">总成本</span>
              <span class="font-mono-number text-sci-cyan font-bold">¥{{ formatNumber(holding.cost) }}</span>
            </div>
          </div>
          <div v-else class="text-center py-8">
            <span class="text-gray-500">暂无持仓数据</span>
          </div>
        </div>
      </el-col>

      <!-- Latest NAV Card -->
      <el-col :span="8" class="info-col">
        <div class="glass-card card-hover p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <span class="text-sci-success text-lg">📊</span>
              <h4 class="text-white font-semibold">最新净值</h4>
            </div>
          </div>
          <div v-if="latestNav" class="space-y-3">
            <div class="flex justify-between items-center">
              <span class="text-gray-400 text-sm">净值日期</span>
              <span class="text-gray-400 text-sm">{{ formatDate(latestNav.date) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-400 text-sm">单位净值</span>
              <span class="font-mono-number text-gray-200">¥{{ formatNumber(latestNav.unit_nav, 4) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-400 text-sm">累计净值</span>
              <span class="font-mono-number text-gray-300">¥{{ formatNumber(latestNav.accumulated_nav, 4) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-400 text-sm">日增长率</span>
              <span class="font-mono-number font-bold"
                    :class="latestNav.daily_growth >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                {{ latestNav.daily_growth >= 0 ? '+' : '' }}{{ formatNumber(latestNav.daily_growth * 100, 2) }}%
              </span>
            </div>
          </div>
          <div v-else class="text-center py-8">
            <span class="text-gray-500">暂无净值数据</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Realtime Data Card -->
    <el-row :gutter="20" v-if="fund">
      <el-col :span="24">
        <div class="glass-card p-8">
          <!-- Card Header -->
          <div class="card-header flex items-center justify-between mb-6">
            <div class="flex items-center space-x-3">
              <div class="flex items-center space-x-2">
                <span class="text-lg">{{ realtimeData?.is_listed_fund ? '📈' : '📊' }}</span>
                <h3 class="text-lg font-semibold text-white">
                  {{ realtimeData?.is_listed_fund ? '实时股价' : '实时估值' }}
                </h3>
              </div>
              <div class="flex items-center space-x-2">
                <span v-if="realtimeData?.is_listed_fund" class="tag-tech-gold text-xs">场内基金</span>
                <span v-else class="tag-tech-cyan text-xs">场外基金</span>
                <span v-if="realtimeData?.is_trading_time" class="tag-tech-green text-xs">盘中实时</span>
                <span v-else class="tag-tech text-xs border-gray-500 text-gray-400">非交易时间</span>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <div class="flex items-center space-x-2 px-3 py-1.5
                            bg-navy-900/50 border border-sci-cyan/20 rounded-lg">
                <span class="w-1.5 h-1.5 rounded-full mr-2"
                      :class="autoRefresh ? 'bg-sci-success animate-pulse' : 'bg-gray-500'"></span>
                <span class="text-xs text-gray-400">
                  {{ autoRefresh ? '已开启 (每60秒)' : '已关闭' }}
                </span>
              </div>
              <button @click="toggleAutoRefresh" class="btn-tech text-sm">
                {{ autoRefresh ? '关闭自动刷新' : '开启自动刷新' }}
              </button>
            </div>
          </div>

          <!-- Realtime Data Content -->
          <div v-if="realtimeData && (realtimeData.increase_rate !== null || realtimeData.current_price)">
            <el-row :gutter="20">
              <!-- 场内基金：实时股价 -->
              <el-col v-if="realtimeData.is_listed_fund" :span="6">
                <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                  <div class="text-gray-400 text-sm mb-2">实时股价</div>
                  <div class="stat-value-glow text-3xl font-bold font-mono-number"
                       :class="realtimeData.increase_rate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                    ¥{{ formatNumber(realtimeData.current_price, 4) }}
                  </div>
                </div>
              </el-col>

              <!-- 场外基金：估算涨跌幅 -->
              <el-col v-else :span="6">
                <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                  <div class="text-gray-400 text-sm mb-2">估算涨跌幅</div>
                  <div class="stat-value-glow text-3xl font-bold font-mono-number"
                       :class="realtimeData.increase_rate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                    {{ realtimeData.increase_rate >= 0 ? '+' : '' }}{{ formatNumber(realtimeData.increase_rate, 2) }}%
                  </div>
                </div>
              </el-col>

              <!-- 涨跌幅 -->
              <el-col :span="6">
                <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                  <div class="text-gray-400 text-sm mb-2">涨跌幅</div>
                  <div class="text-2xl font-bold font-mono-number"
                       :class="realtimeData.increase_rate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                    {{ realtimeData.increase_rate >= 0 ? '+' : '' }}{{ formatNumber(realtimeData.increase_rate, 2) }}%
                  </div>
                  <div class="text-xs text-gray-500 mt-1">
                    {{ realtimeData.is_listed_fund ? '实际涨跌' : '估算涨跌' }}
                  </div>
                </div>
              </el-col>

              <!-- 数据更新时间 -->
              <el-col :span="6">
                <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                  <div class="text-gray-400 text-sm mb-2">数据更新时间</div>
                  <div class="text-lg font-mono-number text-gray-200">
                    {{ formatDateTime(realtimeData.estimate_time) }}
                  </div>
                </div>
              </el-col>

              <!-- 最新正式净值 -->
              <el-col :span="6">
                <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                  <div class="text-gray-400 text-sm mb-2">最新正式净值</div>
                  <div v-if="realtimeData.latest_nav_unit_nav" class="text-lg font-mono-number text-gray-200">
                    ¥{{ formatNumber(realtimeData.latest_nav_unit_nav, 4) }}
                    <div class="text-xs text-sci-cyan/60 mt-1">
                      {{ formatDate(realtimeData.latest_nav_date) }}
                    </div>
                  </div>
                  <span v-else class="text-gray-500">-</span>
                </div>
              </el-col>
            </el-row>
          </div>
          <div v-else class="text-center py-12">
            <span class="text-gray-500 text-lg">当前非交易时间，暂无实时数据</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Stock Positions Card -->
    <div class="glass-card p-8 mt-6" v-if="fund">
      <div class="card-header flex items-center justify-between mb-6">
        <div class="flex items-center space-x-2">
          <span class="text-sci-gold text-lg">📊</span>
          <h3 class="text-lg font-semibold text-white">股票持仓明细</h3>
        </div>
        <button @click="syncStockPositions"
                :disabled="syncingStock"
                class="btn-tech text-sm flex items-center space-x-2"
                :class="syncingStock ? 'opacity-50 cursor-not-allowed' : ''">
          <span v-if="!syncingStock">⟳</span>
          <span v-else class="animate-spin">⟳</span>
          <span>{{ syncingStock ? '同步中...' : '同步持仓' }}</span>
        </button>
      </div>

      <!-- Stock Positions Table -->
      <div v-if="stockPositions.length > 0">
        <el-table :data="stockPositions" class="table-sci-fi" stripe>
          <el-table-column prop="stock_code" label="股票代码" width="120" />
          <el-table-column prop="stock_name" label="股票名称" width="150" />
          <el-table-column prop="shares" label="持仓股数" align="right">
            <template #default="{ row }">
              <span class="font-mono-number">{{ formatNumber(row.shares, 0) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="market_value" label="持仓市值" align="right">
            <template #default="{ row }">
              <span class="font-mono-number">¥{{ formatNumber(row.market_value) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="weight" label="占净值比例" align="right" width="120">
            <template #default="{ row }">
              <span class="font-mono-number">{{ (row.weight * 100).toFixed(2) }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="report_date" label="报告期" width="120" />
        </el-table>
      </div>
      <div v-else class="text-center py-8">
        <span class="text-gray-500">暂无持仓数据，请点击"同步持仓"按钮从 Tushare 获取最新持仓</span>
      </div>

      <!-- Stock-based Realtime Valuation -->
      <div v-if="stockRealtimeNav" class="mt-6 p-5 bg-navy-900-50 rounded border border-sci-cyan-30">
        <div class="flex items-center space-x-2 mb-4">
          <span class="text-sci-cyan text-lg">💹</span>
          <h4 class="text-lg font-semibold text-white">基于持仓的实时估值</h4>
          <span class="text-xs text-gray-400 ml-2">由 Tushare 新浪财经源计算</span>
        </div>
        <div class="grid grid-cols-2 gap-6">
          <div class="flex items-center space-x-3">
            <span class="text-gray-400 text-sm">实时估值：</span>
            <span class="font-mono-number text-xl font-bold" :class="stockRealtimeNav.increase_rate >= 0 ? 'text-red-400' : 'text-green-400'">
              {{ stockRealtimeNav.realtime_nav }}
            </span>
          </div>
          <div class="flex items-center space-x-3">
            <span class="text-gray-400 text-sm">涨跌幅：</span>
            <span class="font-mono-number text-xl font-bold" :class="stockRealtimeNav.increase_rate >= 0 ? 'text-red-400' : 'text-green-400'">
              {{ stockRealtimeNav.increase_rate }}%
            </span>
          </div>
        </div>
        <p class="text-sm text-gray-400 mt-3">
          基于 {{ stockRealtimeNav.stock_count }} 只股票持仓计算
          · 更新时间：{{ formatDateTime(stockRealtimeNav.update_time) }}
        </p>
      </div>
    </div>

    <!-- Chart Card -->
    <div class="glass-card p-8">
      <!-- Card Header -->
      <div class="card-header flex items-center justify-between mb-6">
        <div class="flex items-center space-x-2">
          <span class="text-sci-cyan text-lg">📈</span>
          <h3 class="text-lg font-semibold text-white">收益趋势</h3>
        </div>
        <button @click="handleSync"
                :disabled="syncing"
                class="btn-tech-primary text-sm flex items-center space-x-2"
                :class="syncing ? 'opacity-50 cursor-not-allowed' : ''">
          <span v-if="!syncing">⟳</span>
          <span v-else class="animate-spin">⟳</span>
          <span>同步数据</span>
        </button>
      </div>

      <!-- Chart Container -->
      <div ref="chartRef" class="chart-container" style="height: 400px;"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { getFund, getHolding, getLatestNav, getPnLChartData, syncFund, getRealtimeValuation, getFundStockPositions, syncFundStockPositions, getStockRealtimeNav } from '@/api/fund'
import { formatNumber, formatDate, formatDateTime } from '@/utils/helpers'
import dayjs from 'dayjs'

const route = useRoute()
const fundId = ref(route.params.id)

const fund = ref(null)
const holding = ref(null)
const latestNav = ref(null)
const realtimeData = ref(null)
const loading = ref(false)
const syncing = ref(false)
const chartRef = ref(null)

// 股票持仓相关
const stockPositions = ref([])
const stockRealtimeNav = ref(null)
const syncingStock = ref(false)

// 自动刷新相关
const autoRefresh = ref(true)
const refreshInterval = ref(null)

const fetchData = async () => {
  loading.value = true
  try {
    fund.value = await getFund(fundId.value)
    holding.value = await getHolding(fundId.value).catch(() => null)
    latestNav.value = await getLatestNav(fund.value.fund_code).catch(() => null)
    await fetchRealtimeData()
    await fetchStockPositions()
    await fetchStockRealtimeNav()
    await initChart()
  } finally {
    loading.value = false
  }
}

// 获取股票持仓
const fetchStockPositions = async () => {
  if (!fund.value) return
  try {
    const response = await getFundStockPositions(fundId.value)
    stockPositions.value = response.data || []
  } catch (error) {
    console.error('获取持仓失败:', error)
    stockPositions.value = []
  }
}

// 同步股票持仓
const syncStockPositions = async () => {
  syncingStock.value = true
  try {
    const response = await syncFundStockPositions(fundId.value)
    if (response.data.success) {
      await fetchStockPositions()
      // 同步成功后也获取一次实时估值
      await fetchStockRealtimeNav()
    }
  } catch (error) {
    console.error('同步持仓失败:', error)
  } finally {
    syncingStock.value = false
  }
}

// 获取基于股票的实时估值
const fetchStockRealtimeNav = async () => {
  if (!fund.value) return
  try {
    const response = await getStockRealtimeNav(fund.value.fund_code)
    stockRealtimeNav.value = response.data
  } catch (error) {
    // 如果没有持仓数据或计算失败，不显示错误
    console.log('基于股票的实时估值不可用:', error.message)
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

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  // 每60秒刷新一次（包括基于股票的实时估值）
  refreshInterval.value = setInterval(() => {
    fetchRealtimeData()
    fetchStockRealtimeNav()
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
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#06b6d4'
        }
      },
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(6, 182, 212, 0.3)',
      borderWidth: 1,
      textStyle: {
        color: '#e2e8f0'
      }
    },
    legend: {
      data: ['市值', '收益', '收益率'],
      textStyle: {
        color: '#94a3b8'
      },
      selectedMode: true
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
      data: chartData.dates,
      axisLine: {
        lineStyle: {
          color: 'rgba(6, 182, 212, 0.3)'
        }
      },
      axisLabel: {
        color: '#94a3b8'
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '金额(元)',
        position: 'left',
        nameTextStyle: {
          color: '#94a3b8'
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(6, 182, 212, 0.3)'
          }
        },
        axisLabel: {
          color: '#94a3b8'
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(6, 182, 212, 0.1)'
          }
        }
      },
      {
        type: 'value',
        name: '收益率(%)',
        position: 'right',
        nameTextStyle: {
          color: '#94a3b8'
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(6, 182, 212, 0.3)'
          }
        },
        axisLabel: {
          color: '#94a3b8'
        },
        splitLine: {
          show: false
        }
      }
    ],
    series: [
      {
        name: '市值',
        type: 'line',
        data: chartData.market_values,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#06b6d4',
          width: 2,
          shadowColor: 'rgba(6, 182, 212, 0.5)',
          shadowBlur: 10
        },
        itemStyle: {
          color: '#06b6d4',
          borderColor: '#06b6d4',
          borderWidth: 2
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(6, 182, 212, 0.3)' },
              { offset: 1, color: 'rgba(6, 182, 212, 0.05)' }
            ]
          }
        }
      },
      {
        name: '收益',
        type: 'line',
        data: chartData.profits,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#f59e0b',
          width: 2,
          shadowColor: 'rgba(245, 158, 11, 0.5)',
          shadowBlur: 10
        },
        itemStyle: {
          color: '#f59e0b',
          borderColor: '#f59e0b',
          borderWidth: 2
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(245, 158, 11, 0.3)' },
              { offset: 1, color: 'rgba(245, 158, 11, 0.05)' }
            ]
          }
        }
      },
      {
        name: '收益率',
        type: 'line',
        yAxisIndex: 1,
        data: chartData.profit_rates,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#22c55e',
          width: 2,
          shadowColor: 'rgba(34, 197, 94, 0.5)',
          shadowBlur: 10
        },
        itemStyle: {
          color: '#22c55e',
          borderColor: '#22c55e',
          borderWidth: 2
        }
      }
    ]
  }

  chart.setOption(option)

  // Handle resize
  const resizeHandler = () => {
    chart.resize()
  }
  window.addEventListener('resize', resizeHandler)

  // Store cleanup
  const cleanup = () => {
    window.removeEventListener('resize', resizeHandler)
    chart.dispose()
  }

  // Call cleanup on unmount
  onUnmounted(() => {
    cleanup()
  })
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

.info-col {
  /* No custom margin - let Element Plus gutter handle spacing */
}

.glass-card {
  transition: all 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(6, 182, 212, 0.15),
              0 0 30px rgba(6, 182, 212, 0.1);
}

.chart-container {
  position: relative;
}

/* Responsive */
@media (max-width: 1024px) {
  .info-col {
    /* Let Element Plus handle spacing */
  }
}

@media (max-width: 768px) {
  .info-col {
    /* Let Element Plus handle spacing */
  }
}
</style>
