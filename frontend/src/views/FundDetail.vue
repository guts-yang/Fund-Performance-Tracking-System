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
              <span class="text-gray-200 text-sm">基金代码</span>
              <span class="font-mono-number text-sci-cyan">{{ fund.fund_code }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-200 text-sm">基金名称</span>
              <span class="text-white">{{ fund.fund_name }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-200 text-sm">基金类型</span>
              <span class="tag-tech-cyan text-xs">{{ fund.fund_type }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-200 text-sm">创建时间</span>
              <span class="text-gray-200 text-sm">{{ formatDate(fund.created_at) }}</span>
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
              <span class="text-gray-200 text-sm">持有金额</span>
              <span class="font-mono-number text-white">¥{{ formatNumber(holding.amount) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-200 text-sm">持有份额</span>
              <span class="font-mono-number text-white">{{ formatNumber(holding.shares, 4) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-200 text-sm">成本单价</span>
              <span class="font-mono-number text-white">¥{{ formatNumber(holding.cost_price, 4) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-200 text-sm">总成本</span>
              <span class="font-mono-number text-sci-cyan font-bold">¥{{ formatNumber(holding.cost) }}</span>
            </div>
          </div>
          <div v-else class="text-center py-8">
            <span class="text-gray-300">暂无持仓数据</span>
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
              <span class="text-gray-200 text-sm">净值日期</span>
              <span class="text-gray-200 text-sm">{{ formatDate(latestNav.date) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-200 text-sm">单位净值</span>
              <span class="font-mono-number text-white">¥{{ formatNumber(latestNav.unit_nav, 4) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-200 text-sm">累计净值</span>
              <span class="font-mono-number text-white">¥{{ formatNumber(latestNav.accumulated_nav, 4) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-200 text-sm">日增长率</span>
              <span class="font-mono-number font-bold"
                    :class="latestNav.daily_growth >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                {{ latestNav.daily_growth >= 0 ? '+' : '' }}{{ formatNumber(latestNav.daily_growth * 100, 2) }}%
              </span>
            </div>
          </div>
          <div v-else class="text-center py-8">
            <span class="text-gray-300">暂无净值数据</span>
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
                <span v-else class="tag-tech text-xs border-gray-500 text-gray-200">非交易时间</span>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <div class="flex items-center space-x-2 px-3 py-1.5
                            bg-navy-900/50 border border-sci-cyan/20 rounded-lg">
                <span class="w-1.5 h-1.5 rounded-full mr-2"
                      :class="autoRefresh ? 'bg-sci-success animate-pulse' : 'bg-gray-500'"></span>
                <span class="text-xs text-gray-200">
                  {{ autoRefresh ? '已开启' : '已关闭' }}
                </span>
                <span v-if="autoRefresh" class="ml-2 text-xs" :class="isTradingTime() ? 'text-sci-success' : 'text-gray-300'">
                  {{ isTradingTime() ? '🔴 交易中' : '⚫ 非交易' }}
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
                  <div class="text-gray-200 text-sm mb-2">实时股价</div>
                  <div class="stat-value-glow text-3xl font-bold font-mono-number"
                       :class="realtimeData.increase_rate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                    ¥{{ formatNumber(realtimeData.current_price, 4) }}
                  </div>
                </div>
              </el-col>

              <!-- 场外基金：估算涨跌幅 -->
              <el-col v-else :span="6">
                <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                  <div class="text-gray-200 text-sm mb-2">估算涨跌幅</div>
                  <div class="stat-value-glow text-3xl font-bold font-mono-number"
                       :class="realtimeData.increase_rate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                    {{ realtimeData.increase_rate >= 0 ? '+' : '' }}{{ formatNumber(realtimeData.increase_rate, 2) }}%
                  </div>
                </div>
              </el-col>

              <!-- 涨跌幅 -->
              <el-col :span="6">
                <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                  <div class="text-gray-200 text-sm mb-2">涨跌幅</div>
                  <div class="text-2xl font-bold font-mono-number"
                       :class="realtimeData.increase_rate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                    {{ realtimeData.increase_rate >= 0 ? '+' : '' }}{{ formatNumber(realtimeData.increase_rate, 2) }}%
                  </div>
                  <div class="text-xs text-gray-300 mt-1">
                    {{ realtimeData.is_listed_fund ? '实际涨跌' : '估算涨跌' }}
                  </div>
                </div>
              </el-col>

              <!-- 数据更新时间 -->
              <el-col :span="6">
                <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                  <div class="text-gray-200 text-sm mb-2">数据更新时间</div>
                  <div class="text-lg font-mono-number text-white">
                    {{ formatDateTime(realtimeData.estimate_time) }}
                  </div>
                </div>
              </el-col>

              <!-- 最新正式净值 -->
              <el-col :span="6">
                <div class="text-center p-4 bg-navy-900/30 rounded-lg border border-sci-cyan/10">
                  <div class="text-gray-200 text-sm mb-2">最新正式净值</div>
                  <div v-if="realtimeData.latest_nav_unit_nav" class="text-lg font-mono-number text-white">
                    ¥{{ formatNumber(realtimeData.latest_nav_unit_nav, 4) }}
                    <div class="text-xs text-sci-cyan/60 mt-1">
                      {{ formatDate(realtimeData.latest_nav_date) }}
                    </div>
                  </div>
                  <span v-else class="text-gray-300">-</span>
                </div>
              </el-col>
            </el-row>
          </div>
          <div v-else class="text-center py-12">
            <span class="text-gray-300 text-lg">当前非交易时间，暂无实时数据</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Stock Positions Card -->
    <div class="glass-card p-4 mt-6" v-if="fund">
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
        <el-table :data="stockPositions" class="table-sci-fi" stripe
                  :default-sort="{ prop: 'weight', order: 'descending' }">
          <el-table-column prop="stock_code" label="股票代码" width="150">
            <template #default="{ row }">
              <div class="flex items-center space-x-2">
                <span class="font-mono-number">{{ row.stock_code }}</span>
                <span v-if="isOverseasStock(row.stock_code)"
                      class="text-warning text-xs"
                      title="境外股票数据可能不完整">
                  ⚠️
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="stock_name" label="股票名称" width="150" />
          <el-table-column prop="shares" label="持仓股数" align="right" sortable>
            <template #default="{ row }">
              <span class="font-mono-number">{{ row.shares ? formatNumber(row.shares, 0) : '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="market_value" label="持仓市值" align="right" sortable>
            <template #default="{ row }">
              <span class="font-mono-number">¥{{ row.market_value ? formatNumber(row.market_value) : '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="weight" label="占净值比例" align="right" width="120" sortable>
            <template #default="{ row }">
              <span v-if="row.weight" class="font-mono-number">{{ (row.weight * 100).toFixed(2) }}%</span>
              <span v-else class="text-gray-300 text-xs">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="report_date" label="报告期" width="120" />
        </el-table>
      </div>
      <div v-else class="text-center py-8">
        <span class="text-gray-300">暂无持仓数据，请点击"同步持仓"按钮从 Tushare 获取最新持仓</span>
      </div>

      <!-- Holdings Pie Chart -->
      <div v-if="stockPositions.length > 0" class="mt-6">
        <div class="flex items-center space-x-2 mb-4">
          <span class="text-sci-cyan text-lg">🥧</span>
          <h4 class="text-lg font-semibold text-white">持仓占比分析</h4>
          <span class="text-xs text-gray-200 ml-2">Top 10 重仓股</span>
        </div>

        <div ref="pieChartRef" class="pie-chart-container" style="height: 400px;"></div>
      </div>

      <!-- Stock-based Realtime Valuation -->
      <div v-if="stockRealtimeNav" class="mt-6 p-5 bg-navy-900-50 rounded border border-sci-cyan-30">
        <div class="flex items-center space-x-2 mb-4">
          <span class="text-sci-cyan text-lg">💹</span>
          <h4 class="text-lg font-semibold text-white">基于持仓的实时估值</h4>
          <span class="text-xs text-gray-200 ml-2">由 Tushare 新浪财经源计算</span>
        </div>
        <div class="grid grid-cols-2 gap-6">
          <div class="flex items-center space-x-3">
            <span class="text-gray-200 text-sm">实时估值：</span>
            <span class="font-mono-number text-xl font-bold" :class="stockRealtimeNav.increase_rate >= 0 ? 'text-red-400' : 'text-green-400'">
              {{ stockRealtimeNav.realtime_nav }}
            </span>
          </div>
          <div class="flex items-center space-x-3">
            <span class="text-gray-200 text-sm">涨跌幅：</span>
            <span class="font-mono-number text-xl font-bold" :class="stockRealtimeNav.increase_rate >= 0 ? 'text-red-400' : 'text-green-400'">
              {{ stockRealtimeNav.increase_rate }}%
            </span>
          </div>
        </div>
        <p class="text-sm text-gray-200 mt-3">
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
import { ref, onMounted, onUnmounted, watchEffect, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getFund, getHolding, getLatestNav, getPnLChartData, syncFund, getRealtimeValuation, getFundStockPositions, syncFundStockPositions, getStockRealtimeNav } from '@/api/fund'
import { formatNumber, formatDate, formatDateTime } from '@/utils/helpers'
import { isTradingTime, getDynamicRefreshInterval } from '@/utils/trading_time'
import dayjs from 'dayjs'

// 判断是否为海外股票（非A股）
const isOverseasStock = (stockCode) => {
  if (!stockCode) return false
  return !stockCode.endsWith('.SZ') && !stockCode.endsWith('.SH')
}

// 获取市场标签
const getMarketLabel = (stockCode) => {
  if (!stockCode) return ''
  if (stockCode.endsWith('.SZ')) return '深交所'
  if (stockCode.endsWith('.SH')) return '上交所'
  if (stockCode.endsWith('.HK')) return '港交所'
  return '境外'
}

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
const stockRealtimeNavError = ref(null)
const syncingStock = ref(false)
const pieChartRef = ref(null)  // v1.7.3: 饼图引用
const pieChartCleanup = ref(null)  // v2.0: 饼图清理函数

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
    stockPositions.value = response || []

    // v2.2: 等待 Vue 完成 DOM 渲染后再初始化饼图
    // 因为 pieChartRef 元素在 v-if="stockPositions.length > 0" 内部
    // 必须等待 nextTick 确保 DOM 已更新
    await nextTick()

    // v1.7.3: 获取持仓后初始化饼图
    await initPieChart()
  } catch (error) {
    console.error('获取持仓失败:', error)
    stockPositions.value = []
  }
}

// v2.1: 增强版初始化持仓占比饼图（带详细调试）
const initPieChart = async () => {
  console.log('🥧 [initPieChart] ========== 开始执行 ==========')

  // 检查 1: pieChartRef 是否存在
  if (!pieChartRef.value) {
    console.error('🥧 [initPieChart] ❌ ERROR: pieChartRef.value 是 null')
    console.log('🥧 [initPieChart] 可能原因：DOM 元素还未渲染')
    return
  }
  console.log('🥧 [initPieChart] ✅ pieChartRef.value 存在')

  // 检查 2: stockPositions 是否有数据
  if (!stockPositions.value || stockPositions.value.length === 0) {
    console.error('🥧 [initPieChart] ❌ ERROR: stockPositions 为空')
    return
  }
  console.log(`🥧 [initPieChart] ✅ stockPositions 有 ${stockPositions.value.length} 条记录`)

  // 检查 3: DOM 元素是否已渲染
  await nextTick()
  console.log('🥧 [initPieChart] ✅ nextTick 完成')

  const domWidth = pieChartRef.value?.offsetWidth
  const domHeight = pieChartRef.value?.offsetHeight
  console.log(`🥧 [initPieChart] DOM 尺寸: ${domWidth}px × ${domHeight}px`)

  if (!domWidth || !domHeight) {
    console.error('🥧 [initPieChart] ❌ ERROR: DOM 元素尺寸为 0')
    return
  }

  // 步骤 1: 数据类型转换
  console.log('🥧 [initPieChart] 步骤 1: 数据类型转换')
  const positionsWithNumericData = stockPositions.value.map((p, index) => {
    const weight_num = p.weight ? parseFloat(p.weight) : null
    const market_value_num = p.market_value ? parseFloat(p.market_value) : 0

    if (index < 3) {
      // 只打印前 3 条作为示例
      console.log(`  📊 记录 ${index}: ${p.stock_code}`)
      console.log(`    weight: ${p.weight} (${typeof p.weight}) → ${weight_num} (${typeof weight_num}), isNaN: ${isNaN(weight_num)}`)
      console.log(`    market_value: ${p.market_value} (${typeof p.market_value}) → ${market_value_num} (${typeof market_value_num}), isNaN: ${isNaN(market_value_num)}`)
    }

    return {
      ...p,
      weight_num,
      market_value_num
    }
  })

  // 步骤 2: 检查权重数据
  console.log('🥧 [initPieChart] 步骤 2: 检查权重数据')
  const hasOfficialWeight = positionsWithNumericData.some(p => p.weight_num !== null && !isNaN(p.weight_num) && p.weight_num > 0)
  console.log(`🥧 [initPieChart] hasOfficialWeight: ${hasOfficialWeight}`)

  let topPositions = []

  if (hasOfficialWeight) {
    console.log('🥧 [initPieChart] 使用方案 1: 官方权重数据')
    topPositions = positionsWithNumericData
      .filter(p => p.weight_num !== null && !isNaN(p.weight_num) && p.weight_num > 0)
      .sort((a, b) => b.weight_num - a.weight_num)
      .slice(0, 10)
      .map(p => ({
        ...p,
        effective_weight: p.weight_num
      }))
  } else {
    console.log('🥧 [initPieChart] 使用方案 2: market_value 计算')
    const totalMarketValue = positionsWithNumericData.reduce((sum, p) => {
      const val = !isNaN(p.market_value_num) ? p.market_value_num : 0
      return sum + val
    }, 0)

    console.log(`🥧 [initPieChart] 总市值: ${totalMarketValue}`)

    if (totalMarketValue > 0) {
      topPositions = positionsWithNumericData
        .filter(p => !isNaN(p.market_value_num) && p.market_value_num > 0)
        .map(p => ({
          ...p,
          effective_weight: p.market_value_num / totalMarketValue
        }))
        .sort((a, b) => b.effective_weight - a.effective_weight)
        .slice(0, 10)
    }
  }

  // 步骤 3: 检查 topPositions
  console.log(`🥧 [initPieChart] 步骤 3: topPositions.length = ${topPositions.length}`)

  if (topPositions.length === 0) {
    console.error('🥧 [initPieChart] ❌ ERROR: topPositions 为空，无法渲染图表')
    return
  }

  console.log('🥧 [initPieChart] Top 3 重仓股:')
  topPositions.slice(0, 3).forEach((p, i) => {
    console.log(`  ${i + 1}. ${p.stock_name || p.stock_code}: ${(p.effective_weight * 100).toFixed(2)}%`)
  })

  // 步骤 4: 初始化 ECharts
  console.log('🥧 [initPieChart] 步骤 4: 初始化 ECharts')

  try {
    const chart = echarts.init(pieChartRef.value)
    console.log('🥧 [initPieChart] ✅ ECharts 实例创建成功')

    const chartData = topPositions.map(p => ({
      name: p.stock_name || p.stock_code,
      value: (p.effective_weight * 100).toFixed(2)
    }))

    console.log('🥧 [initPieChart] 图表数据:', chartData)

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
        textStyle: { color: '#94a3b8' }
      },
      series: [
        {
          name: '持仓占比',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
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
        }
      ]
    }

    chart.setOption(option)
    console.log('🥧 [initPieChart] ✅ 图表配置已设置')

    // 手动管理 resize 监听器
    const resizeHandler = () => {
      if (chart && !chart.isDisposed()) {
        chart.resize()
      }
    }
    window.addEventListener('resize', resizeHandler)

    // 保存清理函数
    pieChartCleanup.value = () => {
      console.log('🥧 [initPieChart] 🧹 清理图表')
      window.removeEventListener('resize', resizeHandler)
      if (chart && !chart.isDisposed()) {
        chart.dispose()
      }
    }

    console.log('🥧 [initPieChart] ========== 完成 ==========')

  } catch (error) {
    console.error('🥧 [initPieChart] ❌ ERROR: ECharts 初始化失败', error)
    console.error('🥧 [initPieChart] 错误堆栈:', error.stack)
  }
}

// 同步股票持仓
const syncStockPositions = async () => {
  syncingStock.value = true
  try {
    const response = await syncFundStockPositions(fundId.value)
    if (response?.data?.success) {
      await fetchStockPositions()
      // 同步成功后也获取一次实时估值
      await fetchStockRealtimeNav()
      ElMessage.success(`成功同步 ${response.data.funds_updated} 条持仓记录`)
    } else {
      ElMessage.error(response?.data?.message || '同步失败')
    }
  } catch (error) {
    console.error('同步持仓失败:', error)
    const errorMsg = error.response?.data?.detail || error.message
    ElMessage.error('同步持仓失败: ' + errorMsg)
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
    stockRealtimeNavError.value = null
  } catch (error) {
    // 如果没有持仓数据或计算失败，不显示错误
    const errorMsg = error.response?.data?.detail || error.message
    stockRealtimeNav.value = null
    stockRealtimeNavError.value = errorMsg
    console.log('基于股票的实时估值不可用:', errorMsg)
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

  // 在获取数据后重新启动定时器（动态调整间隔）
  if (autoRefresh.value) {
    startAutoRefresh()
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
  stopAutoRefresh() // 先停止现有的定时器

  const interval = getDynamicRefreshInterval()
  refreshInterval.value = setInterval(() => {
    fetchRealtimeData()
    fetchStockRealtimeNav()
  }, interval)

  console.log(`[FundDetail] 自动刷新已启动，间隔: ${interval / 1000}秒，交易时间: ${isTradingTime()}`)
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

  // 反转数据数组，使时间从左到右递增（早→晚）
  // 后端返回的是降序数据（新→旧），需要反转以符合常规阅读习惯
  const dates = [...chartData.dates].reverse()
  const market_values = [...chartData.market_values].reverse()
  const profits = [...chartData.profits].reverse()
  const profit_rates = [...chartData.profit_rates].reverse()

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
        data: market_values,
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
        data: profits,
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
        data: profit_rates,
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
  // v2.0: 清理饼图
  if (pieChartCleanup.value) {
    pieChartCleanup.value()
  }
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
