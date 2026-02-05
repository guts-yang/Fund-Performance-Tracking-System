<template>
  <div class="analysis space-y-6">
    <!-- Page Title -->
    <div class="flex items-center space-x-3 mb-6">
      <span class="text-sci-cyan text-2xl">📊</span>
      <h2 class="text-2xl font-bold text-white">收益分析</h2>
    </div>

    <!-- Summary Stats Row -->
    <el-row :gutter="20">
      <el-col :span="6">
        <div class="glass-card card-hover p-5">
          <div class="text-gray-400 text-sm mb-2">总资产</div>
          <div class="stat-value-glow text-sci-gold text-2xl font-bold font-mono-number">
            ¥{{ formatNumber(totalAssets) }}
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="glass-card card-hover p-5">
          <div class="text-gray-400 text-sm mb-2">总收益</div>
          <div class="stat-value-glow text-2xl font-bold font-mono-number"
               :class="totalProfit >= 0 ? 'text-sci-success' : 'text-sci-danger'">
            {{ totalProfit >= 0 ? '+' : '' }}¥{{ formatNumber(totalProfit) }}
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="glass-card card-hover p-5">
          <div class="text-gray-400 text-sm mb-2">总收益率</div>
          <div class="stat-value-glow text-2xl font-bold font-mono-number"
               :class="totalProfitRate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
            {{ totalProfitRate >= 0 ? '+' : '' }}{{ formatNumber(totalProfitRate, 2) }}%
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="glass-card card-hover p-5">
          <div class="text-gray-400 text-sm mb-2">基金数量</div>
          <div class="stat-value-glow text-sci-cyan text-2xl font-bold font-mono-number">
            {{ fundCount }}
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20">
      <!-- Portfolio Distribution Chart -->
      <el-col :span="12">
        <div class="glass-card p-6 h-full">
          <div class="card-header flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <span class="text-sci-cyan text-lg">🥧</span>
              <h3 class="text-lg font-semibold text-white">持仓分布</h3>
            </div>
          </div>
          <div ref="pieChartRef" style="height: 350px;"></div>
        </div>
      </el-col>

      <!-- Profit Trend Chart -->
      <el-col :span="12">
        <div class="glass-card p-6 h-full">
          <div class="card-header flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <span class="text-sci-gold text-lg">📈</span>
              <h3 class="text-lg font-semibold text-white">收益趋势</h3>
            </div>
          </div>
          <div ref="trendChartRef" style="height: 350px;"></div>
        </div>
      </el-col>
    </el-row>

    <!-- Performance Metrics -->
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="glass-card p-6">
          <div class="card-header flex items-center justify-between mb-6">
            <div class="flex items-center space-x-2">
              <span class="text-sci-success text-lg">⚡</span>
              <h3 class="text-lg font-semibold text-white">绩效指标</h3>
            </div>
          </div>

          <el-row :gutter="20">
            <el-col :span="6">
              <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                <div class="text-gray-400 text-sm mb-2">最佳收益基金</div>
                <div class="text-sci-success font-bold">{{ bestPerformer?.name || '-' }}</div>
                <div class="text-xs text-sci-success/80 mt-1">
                  {{ bestPerformer?.rate >= 0 ? '+' : '' }}{{ formatNumber(bestPerformer?.rate || 0, 2) }}%
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                <div class="text-gray-400 text-sm mb-2">最差收益基金</div>
                <div class="text-sci-danger font-bold">{{ worstPerformer?.name || '-' }}</div>
                <div class="text-xs text-sci-danger/80 mt-1">
                  {{ worstPerformer?.rate >= 0 ? '+' : '' }}{{ formatNumber(worstPerformer?.rate || 0, 2) }}%
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                <div class="text-gray-400 text-sm mb-2">平均收益率</div>
                <div class="text-sci-cyan font-bold">
                  {{ formatNumber(avgProfitRate, 2) }}%
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                <div class="text-gray-400 text-sm mb-2">盈利基金数</div>
                <div class="text-sci-success font-bold">
                  {{ profitableFunds }} / {{ fundCount }}
                </div>
                <div class="text-xs text-gray-500 mt-1">
                  {{ formatNumber((profitableFunds / fundCount) * 100, 1) }}%
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getPortfolioSummary } from '@/api/fund'
import { formatNumber } from '@/utils/helpers'

// Stats
const totalAssets = ref(0)
const totalProfit = ref(0)
const totalProfitRate = ref(0)
const fundCount = ref(0)
const bestPerformer = ref(null)
const worstPerformer = ref(null)
const avgProfitRate = ref(0)
const profitableFunds = ref(0)

// Chart refs
const pieChartRef = ref(null)
const trendChartRef = ref(null)

let pieChart = null
let trendChart = null

const fetchData = async () => {
  try {
    const summary = await getPortfolioSummary()

    // Update stats
    totalAssets.value = summary.total_market_value || 0
    totalProfit.value = summary.total_profit || 0
    totalProfitRate.value = summary.total_profit_rate || 0
    fundCount.value = summary.fund_count || 0

    // Calculate performance metrics
    if (summary.funds && summary.funds.length > 0) {
      const funds = summary.funds

      // Find best and worst performers
      const sorted = [...funds].sort((a, b) => b.profit_rate - a.profit_rate)
      bestPerformer.value = {
        name: sorted[0]?.fund_name || sorted[0]?.fund_code,
        rate: sorted[0]?.profit_rate || 0
      }
      worstPerformer.value = {
        name: sorted[sorted.length - 1]?.fund_name || sorted[sorted.length - 1]?.fund_code,
        rate: sorted[sorted.length - 1]?.profit_rate || 0
      }

      // Calculate average profit rate
      const totalRate = funds.reduce((sum, f) => sum + (f.profit_rate || 0), 0)
      avgProfitRate.value = totalRate / funds.length

      // Count profitable funds
      profitableFunds.value = funds.filter(f => f.profit_rate > 0).length

      // Initialize pie chart
      initPieChart(funds)

      // Initialize trend chart (mock data for now)
      initTrendChart()
    }
  } catch (error) {
    console.error('Failed to fetch analysis data:', error)
  }
}

const initPieChart = (funds) => {
  if (!pieChartRef.value) return

  pieChart = echarts.init(pieChartRef.value)

  // Prepare data for pie chart
  const data = funds.map(fund => ({
    name: fund.fund_name || fund.fund_code,
    value: fund.market_value || 0
  }))

  const colors = [
    '#06b6d4', '#f59e0b', '#22c55e', '#ef4444',
    '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'
  ]

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(6, 182, 212, 0.3)',
      borderWidth: 1,
      textStyle: {
        color: '#e2e8f0'
      },
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: {
        color: '#94a3b8'
      },
      itemWidth: 12,
      itemHeight: 12
    },
    series: [
      {
        name: '持仓分布',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#0f172a',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold',
            color: '#e2e8f0'
          }
        },
        labelLine: {
          show: false
        },
        data: data,
        color: colors
      }
    ]
  }

  pieChart.setOption(option)
}

const initTrendChart = () => {
  if (!trendChartRef.value) return

  trendChart = echarts.init(trendChartRef.value)

  // Mock trend data (last 7 days)
  const dates = []
  const values = []
  const today = new Date()

  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`)

    // Simulate values based on current total profit
    const baseValue = parseFloat(totalAssets.value) || 0
    const variance = (Math.random() - 0.5) * baseValue * 0.02
    values.push((baseValue + variance * (6 - i)).toFixed(2))
  }

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(6, 182, 212, 0.3)',
      borderWidth: 1,
      textStyle: {
        color: '#e2e8f0'
      }
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
      data: dates,
      axisLine: {
        lineStyle: {
          color: 'rgba(6, 182, 212, 0.3)'
        }
      },
      axisLabel: {
        color: '#94a3b8'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: 'rgba(6, 182, 212, 0.3)'
        }
      },
      axisLabel: {
        color: '#94a3b8',
        formatter: '¥{value}'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(6, 182, 212, 0.1)'
        }
      }
    },
    series: [
      {
        name: '总资产',
        type: 'line',
        data: values,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          color: '#f59e0b',
          width: 3,
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
              { offset: 0, color: 'rgba(245, 158, 11, 0.4)' },
              { offset: 1, color: 'rgba(245, 158, 11, 0.05)' }
            ]
          }
        }
      }
    ]
  }

  trendChart.setOption(option)
}

onMounted(() => {
  fetchData()

  // Handle resize
  const resizeHandler = () => {
    pieChart?.resize()
    trendChart?.resize()
  }
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  pieChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
.analysis {
  padding: 0;
}

.glass-card {
  transition: all 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(6, 182, 212, 0.15),
              0 0 30px rgba(6, 182, 212, 0.1);
}
</style>
