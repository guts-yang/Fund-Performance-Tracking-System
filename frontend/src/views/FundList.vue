<template>
  <div class="fund-list space-y-6">
    <!-- Main Card -->
    <div class="glass-card p-8">
      <!-- Card Header -->
      <div class="card-header flex items-center justify-between mb-8">
        <div class="flex items-center space-x-3">
          <div class="flex items-center space-x-2">
            <span class="text-sci-cyan text-2xl">📋</span>
            <h3 class="text-xl font-semibold text-white">基金管理</h3>
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <el-tag v-if="autoRefresh" type="success" class="tag-tech-green">
            <span class="flex items-center">
              <span class="w-1.5 h-1.5 bg-sci-success rounded-full mr-2 animate-pulse"></span>
              自动刷新中 ({{ lastUpdateTime ? lastUpdateTime : '--:--:--' }})
            </span>
          </el-tag>
          <button @click="toggleAutoRefresh" class="btn-tech">
            {{ autoRefresh ? '关闭自动刷新' : '开启自动刷新' }}
          </button>
          <button @click="showAddDialog" class="btn-tech-primary flex items-center space-x-2">
            <span>+</span>
            <span>添加基金</span>
          </button>
        </div>
      </div>

      <!-- Sci-Fi Table -->
      <div class="overflow-x-auto" v-loading="loading">
        <table class="table-sci-fi">
          <thead>
            <tr>
              <th>基金名称</th>
              <th>基金类型</th>
              <th class="text-right cursor-pointer hover:text-sci-cyan" @click="handleSort('holdings.amount', 'number')">
                持有金额
                <span v-if="sortState.key === 'holdings.amount'">
                  {{ sortState.order === 'desc' ? '↓' : '↑' }}
                </span>
              </th>
              <th class="text-right cursor-pointer hover:text-sci-cyan" @click="handleSort('holdings.shares', 'number')">
                持有份额
                <span v-if="sortState.key === 'holdings.shares'">
                  {{ sortState.order === 'desc' ? '↓' : '↑' }}
                </span>
              </th>
              <th class="text-right">最新净值</th>
              <th class="text-right cursor-pointer hover:text-sci-cyan" @click="handleSort('increase_rate', 'number')">
                实时数据
                <span v-if="sortState.key === 'increase_rate'">
                  {{ sortState.order === 'desc' ? '↓' : '↑' }}
                </span>
              </th>
              <th>创建时间</th>
              <th class="text-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in sortedFunds" :key="row.id" class="table-row">
              <td class="font-mono-number text-sci-cyan">{{ row.fund_name || row.fund_code }}</td>
              <td><span class="tag-tech-cyan text-xs">{{ row.fund_type }}</span></td>
              <td class="text-right font-mono-number">
                <span v-if="row.holdings && row.holdings.amount" class="text-gray-300">
                  ¥{{ formatNumber(row.holdings.amount) }}
                </span>
                <span v-else class="text-gray-500">未设置</span>
              </td>
              <td class="text-right font-mono-number">
                <span v-if="row.holdings && row.holdings.shares" class="text-gray-300">
                  {{ formatNumber(row.holdings.shares) }} 份
                </span>
                <span v-else class="text-gray-500">-</span>
              </td>
              <td class="text-right">
                <div v-if="row.latest_nav_value">
                  <span class="text-xs text-sci-cyan/60 block">正式</span>
                  <div class="font-mono-number">¥{{ formatNumber(row.latest_nav_value, 4) }}</div>
                </div>
                <div v-else class="text-gray-500">-</div>
              </td>
              <td class="text-right">
                <!-- 场内基金：显示实时股价和涨跌 -->
                <div v-if="row.is_listed_fund && row.current_price">
                  <span class="tag-tech-gold text-xs">场内</span>
                  <div class="mt-1 font-mono-number text-base font-bold"
                       :class="row.increase_rate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                    ¥{{ formatNumber(row.current_price, 4) }}
                  </div>
                  <div class="text-xs font-mono-number"
                       :class="row.increase_rate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                    {{ row.increase_rate >= 0 ? '+' : '' }}{{ formatNumber(row.increase_rate, 2) }}%
                  </div>
                </div>
                <!-- 场外基金：显示估算涨跌幅 -->
                <div v-else-if="row.increase_rate !== null && row.increase_rate !== undefined">
                  <span class="tag-tech-cyan text-xs">场外</span>
                  <div class="mt-1 font-mono-number text-lg font-bold"
                       :class="row.increase_rate >= 0 ? 'text-sci-success' : 'text-sci-danger'">
                    {{ row.increase_rate >= 0 ? '+' : '' }}{{ formatNumber(row.increase_rate, 2) }}%
                  </div>
                </div>
                <div v-else class="text-gray-500 text-xs">非交易时间</div>
              </td>
              <td class="text-gray-400 text-sm">{{ formatDate(row.created_at) }}</td>
              <td class="text-right">
                <div class="flex items-center justify-end space-x-3">
                  <button @click="showTradeDialog(row)"
                          class="text-sci-success hover:text-sci-success/80 text-base font-medium transition-colors px-3 py-2 rounded hover:bg-sci-success/10">
                    交易
                  </button>
                  <button @click="showSetHoldingDialog(row)"
                          class="text-sci-cyan hover:text-sci-cyan/80 text-base font-medium transition-colors px-3 py-2 rounded hover:bg-sci-cyan/10 hover:bg-sci-cyan/10">
                    设置持仓
                  </button>
                  <button @click="handleSync(row)"
                          :disabled="syncing[row.id]"
                          class="text-sci-gold hover:text-sci-gold/80 text-base font-medium transition-colors px-3 py-2 rounded hover:bg-sci-gold/10
                                 disabled:opacity-50 disabled:cursor-not-allowed">
                    <span v-if="!syncing[row.id]">⟳ 同步</span>
                    <span v-else class="animate-spin">⟳ 同步</span>
                  </button>
                  <router-link :to="`/funds/${row.id}`"
                               class="text-sci-cyan hover:text-sci-cyan/80 text-base font-medium transition-colors px-3 py-2 rounded hover:bg-sci-cyan/10">
                    详情
                  </router-link>
                  <button @click="handleDelete(row)"
                          class="text-sci-danger hover:text-sci-danger/80 text-base font-medium transition-colors px-3 py-2 rounded hover:bg-sci-danger/10">
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Fund Dialog -->
    <el-dialog v-model="addDialogVisible" title="添加基金" width="500px"
               class="dialog-sci-fi">
      <el-form :model="fundForm" label-width="100px" class="form-sci-fi">
        <el-form-item label="基金代码">
          <div class="fund-code-input-wrapper">
            <el-input
              v-model="fundForm.fund_code"
              placeholder="请输入6位基金代码，如：000001"
              @input="handleFundCodeInput"
              @keyup.enter="handleManualSearch"
              :disabled="fetchingInfo"
              maxlength="6"
              class="input-tech"
            />
            <el-button
              @click="handleManualSearch"
              :disabled="fetchingInfo || fundForm.fund_code.length !== 6"
              :loading="fetchingInfo"
              class="btn-search"
              size="large"
            >
              查询
            </el-button>
          </div>

          <!-- 查询状态提示 -->
          <div v-if="fetchingInfo" class="query-status querying">
            <span class="status-icon">⟳</span>
            正在获取基金信息...
          </div>

          <!-- 成功提示 -->
          <div v-if="fundInfoLoaded && !fundInfoError" class="query-status success">
            <span class="status-icon">✓</span>
            已获取基金信息
          </div>

          <!-- 错误提示 -->
          <div v-if="fundInfoError" class="query-status error">
            <span class="status-icon">⚠</span>
            未找到基金信息，请手动输入基金名称和类型
          </div>
        </el-form-item>
        <el-form-item label="基金名称">
          <el-input v-model="fundForm.fund_name" placeholder="自动获取，可手动修改" class="input-tech" :disabled="fetchingInfo" />
        </el-form-item>
        <el-form-item label="基金类型">
          <el-input v-model="fundForm.fund_type" placeholder="自动获取，可手动修改" class="input-tech" :disabled="fetchingInfo" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button @click="addDialogVisible = false" class="btn-tech">取消</button>
        <button
          @click="handleAdd"
          :disabled="submitting || fetchingInfo || (fundInfoError && !fundForm.fund_name)"
          class="btn-tech-primary"
        >
          <span v-if="!submitting && !fetchingInfo">确认添加</span>
          <span v-else-if="fetchingInfo">加载中...</span>
          <span v-else>添加中...</span>
        </button>
      </template>
    </el-dialog>

    <!-- Set Holding Dialog -->
    <el-dialog v-model="holdingDialogVisible" title="设置持仓" width="600px"
               class="dialog-sci-fi">
      <el-form :model="holdingForm" label-width="120px" class="form-sci-fi">
        <el-alert
          title="只需填写持有金额，系统将自动获取最新净值计算份额"
          type="info"
          :closable="false"
          class="alert-sci-fi mb-4"
        />

        <el-form-item label="持有金额">
          <el-input-number
            v-model="holdingForm.amount"
            :precision="2"
            :min="0"
            placeholder="请输入持有金额"
            controls-position="right"
            class="input-tech-number"
          />
          <span class="ml-2 text-gray-400">元</span>
        </el-form-item>

        <div class="border-t border-sci-cyan/20 pt-4 mt-4">
          <div class="text-sm text-sci-cyan mb-4 flex items-center">
            <span class="mr-2">⚡</span>
            <span>自动计算结果</span>
          </div>

          <el-form-item label="持有份额">
            <span class="text-sci-success font-mono-number text-base">
              {{ formatNumber(holdingForm.shares, 4) }} 份
            </span>
          </el-form-item>

          <el-form-item label="成本单价">
            <span class="text-sci-success font-mono-number text-base">
              ¥{{ formatNumber(holdingForm.cost_price, 4) }}
            </span>
          </el-form-item>

          <el-form-item label="总成本">
            <span class="text-xl font-bold text-sci-cyan font-mono-number stat-value-glow">
              ¥{{ formatNumber(holdingForm.shares * holdingForm.cost_price) }}
            </span>
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <button @click="holdingDialogVisible = false" class="btn-tech">取消</button>
        <button @click="handleSaveHolding" :disabled="submittingHolding" class="btn-tech-primary">
          <span v-if="!submittingHolding">保存持仓</span>
          <span v-else class="animate-pulse">保存中...</span>
        </button>
      </template>
    </el-dialog>

    <!-- Trade Dialog -->
    <el-dialog v-model="tradeDialogVisible" title="基金交易" width="600px"
               class="dialog-sci-fi">
      <el-form :model="tradeForm" label-width="120px" class="form-sci-fi">
        <el-form-item label="交易类型">
          <el-radio-group v-model="tradeForm.transaction_type" class="radio-sci-fi">
            <el-radio value="buy" class="text-gray-300">买入</el-radio>
            <el-radio value="sell" class="text-gray-300">卖出</el-radio>
          </el-radio-group>
        </el-form-item>

        <template v-if="tradeForm.transaction_type === 'buy'">
          <el-form-item label="买入金额">
            <el-input-number
              v-model="tradeForm.amount"
              :precision="2"
              :min="0"
              placeholder="请输入买入金额"
              controls-position="right"
              class="input-tech-number"
            />
            <span class="ml-2 text-gray-400">元</span>
          </el-form-item>
        </template>

        <template v-if="tradeForm.transaction_type === 'sell'">
          <el-form-item label="卖出方式">
            <el-radio-group v-model="sellMode" class="radio-sci-fi">
              <el-radio value="amount" class="text-gray-300">按金额</el-radio>
              <el-radio value="shares" class="text-gray-300">按份额</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item v-if="sellMode === 'amount'" label="卖出金额">
            <el-input-number
              v-model="tradeForm.amount"
              :precision="2"
              :min="0"
              :max="maxSellAmount"
              placeholder="请输入卖出金额"
              controls-position="right"
              class="input-tech-number"
            />
            <span class="ml-2 text-gray-400">元</span>
            <span class="ml-2 text-sci-cyan/60 text-sm">
              最大可卖出: ¥{{ formatNumber(maxSellAmount) }}
            </span>
          </el-form-item>

          <el-form-item v-else label="卖出份额">
            <el-input-number
              v-model="tradeForm.shares"
              :precision="4"
              :min="0"
              :max="maxSellShares"
              placeholder="请输入卖出份额"
              controls-position="right"
              class="input-tech-number"
            />
            <span class="ml-2 text-gray-400">份</span>
            <span class="ml-2 text-sci-cyan/60 text-sm">
              最大可卖出: {{ formatNumber(maxSellShares, 4) }} 份
            </span>
          </el-form-item>
        </template>

        <el-alert
          v-if="tradeForm.transaction_type === 'buy'"
          title="系统将自动获取当日净值计算买入份额"
          type="info"
          :closable="false"
          class="alert-sci-fi mt-4"
        />
        <el-alert
          v-else
          title="系统将自动获取当日净值，卖出后成本价保持不变"
          type="warning"
          :closable="false"
          class="alert-sci-fi mt-4"
        />
      </el-form>
      <template #footer>
        <button @click="tradeDialogVisible = false" class="btn-tech">取消</button>
        <button @click="handleTrade" :disabled="submittingTrade" class="btn-tech-primary">
          <span v-if="!submittingTrade">确定</span>
          <span v-else class="animate-pulse">处理中...</span>
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFunds, createFund, deleteFund, syncFund, getFundInfoByCode, createOrUpdateHolding, buyFund, sellFund, getBatchRealtimeValuation } from '@/api/fund'
import { formatNumber, formatDate, sortArray } from '@/utils/helpers'
import dayjs from 'dayjs'

const router = useRouter()
const funds = ref([])
const loading = ref(false)
const syncing = ref({})
const addDialogVisible = ref(false)
const submitting = ref(false)
const fetchingInfo = ref(false)
const fundInfoLoaded = ref(false)
const fundInfoError = ref(false)
const searchDebounceTimer = ref(null)
const fundInfoCache = ref({})
const holdingDialogVisible = ref(false)
const submittingHolding = ref(false)
const currentFund = ref(null)
const tradeDialogVisible = ref(false)
const submittingTrade = ref(false)
const sellMode = ref('amount')

// 自动刷新相关
const autoRefresh = ref(true)
const refreshInterval = ref(null)
const lastUpdateTime = ref('')

// 排序状态
const sortState = ref({
  key: null,
  order: 'desc',
  type: 'number'
})

// 排序后的基金列表
const sortedFunds = computed(() => {
  if (!sortState.value.key || !funds.value) {
    return funds.value || []
  }
  return sortArray(
    funds.value,
    sortState.value.key,
    sortState.value.order,
    sortState.value.type
  )
})

// 排序切换函数
const handleSort = (key, type = 'number') => {
  if (sortState.value.key === key) {
    sortState.value.order = sortState.value.order === 'desc' ? 'asc' : 'desc'
  } else {
    sortState.value.key = key
    sortState.value.order = 'desc'
    sortState.value.type = type
  }
}

const fundForm = reactive({
  fund_code: '',
  fund_name: '',
  fund_type: ''
})

const holdingForm = ref({
  fund_id: null,
  amount: null,
  shares: null,
  cost_price: null
})

const tradeForm = ref({
  fund_id: null,
  transaction_type: 'buy',
  amount: null,
  shares: null
})

// 计算最大可卖出金额和份额
const maxSellAmount = computed(() => {
  if (currentFund.value?.holdings) {
    return Number(currentFund.value.holdings.amount)
  }
  return 0
})

const maxSellShares = computed(() => {
  if (currentFund.value?.holdings) {
    return Number(currentFund.value.holdings.shares)
  }
  return 0
})

const fetchFunds = async () => {
  loading.value = true
  try {
    funds.value = await getFunds()
    await fetchRealtimeValuation()
  } finally {
    loading.value = false
  }
}

// 获取实时估值
const fetchRealtimeValuation = async () => {
  if (funds.value.length === 0) return

  try {
    const fundCodes = funds.value.map(f => f.fund_code)
    const result = await getBatchRealtimeValuation(fundCodes)

    // 合并实时估值数据
    const valuationMap = {}
    result.valuations.forEach(v => {
      valuationMap[v.fund_code] = v
    })

    funds.value.forEach(fund => {
      const valuation = valuationMap[fund.fund_code]
      if (valuation) {
        fund.increase_rate = valuation.increase_rate
        fund.latest_nav_value = valuation.latest_nav_unit_nav
        fund.is_listed_fund = valuation.is_listed_fund
        fund.current_price = valuation.current_price
        fund.data_source = valuation.data_source
      }
    })

    lastUpdateTime.value = dayjs().format('HH:mm:ss')
  } catch (error) {
    console.error('获取实时估值失败:', error)
  }
}

// 切换自动刷新
const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

// 开启自动刷新
const startAutoRefresh = () => {
  // 每60秒刷新一次
  refreshInterval.value = setInterval(() => {
    fetchRealtimeValuation()
  }, 60000)
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

const showAddDialog = () => {
  fundForm.fund_code = ''
  fundForm.fund_name = ''
  fundForm.fund_type = ''
  addDialogVisible.value = true

  // 重置状态
  resetFundInfoState()
  if (searchDebounceTimer.value) {
    clearTimeout(searchDebounceTimer.value)
    searchDebounceTimer.value = null
  }
}

const handleAdd = async () => {
  // 验证基金代码
  if (!fundForm.fund_code) {
    ElMessage.warning('请输入基金代码')
    return
  }

  // 如果查询失败，需要验证手动填写的信息
  if (fundInfoError.value) {
    if (!fundForm.fund_name) {
      ElMessage.warning('请填写基金名称')
      return
    }
  }

  submitting.value = true
  try {
    await createFund(fundForm)
    ElMessage.success('添加成功')
    addDialogVisible.value = false
    await fetchFunds()
  } finally {
    submitting.value = false
  }
}

const handleSync = async (fund) => {
  syncing.value[fund.id] = true
  try {
    await syncFund(fund.id)
    ElMessage.success('同步成功')
  } finally {
    syncing.value[fund.id] = false
  }
}

// 输入事件处理 - 防抖触发
const handleFundCodeInput = () => {
  const code = fundForm.fund_code.trim()

  // 清除之前的定时器
  if (searchDebounceTimer.value) {
    clearTimeout(searchDebounceTimer.value)
  }

  // 如果输入达到6位，设置防抖查询
  if (code.length === 6) {
    searchDebounceTimer.value = setTimeout(() => {
      performFundSearch(code)
    }, 500)
  } else {
    // 重置状态
    resetFundInfoState()
  }
}

// 手动查询
const handleManualSearch = async () => {
  const code = fundForm.fund_code.trim()
  if (code.length === 6) {
    await performFundSearch(code)
  }
}

// 执行查询（核心逻辑）
const performFundSearch = async (code) => {
  if (fetchingInfo.value) return

  // 检查缓存
  if (fundInfoCache.value[code]) {
    setFundInfo(fundInfoCache.value[code])
    fundInfoLoaded.value = true
    fundInfoError.value = false
    return
  }

  fetchingInfo.value = true
  fundInfoError.value = false

  try {
    const info = await getFundInfoByCode(code)

    // 缓存结果
    fundInfoCache.value[code] = info

    // 设置表单数据
    setFundInfo(info)

    // 更新状态
    fundInfoLoaded.value = true
    fundInfoError.value = false

    ElMessage.success('基金信息已自动获取')
  } catch (error) {
    console.warn('获取基金信息失败', error)
    fundInfoError.value = true
    fundInfoLoaded.value = false
    ElMessage.warning('未找到基金信息，请手动输入')
  } finally {
    fetchingInfo.value = false
  }
}

// 设置基金信息
const setFundInfo = (info) => {
  fundForm.fund_name = info.fund_name || ''
  fundForm.fund_type = info.fund_type || '开放式基金'
}

// 重置基金信息状态
const resetFundInfoState = () => {
  fundInfoLoaded.value = false
  fundInfoError.value = false
}

// 显示设置持仓对话框
const showSetHoldingDialog = (fund) => {
  currentFund.value = fund
  holdingForm.value = {
    fund_id: fund.id,
    amount: null,
    shares: null,
    cost_price: null
  }

  // 如果已有持仓数据，加载现有持仓
  if (fund.holdings) {
    holdingForm.value = {
      fund_id: fund.id,
      amount: Number(fund.holdings.amount) || null,
      shares: Number(fund.holdings.shares) || null,
      cost_price: Number(fund.holdings.cost_price) || null
    }
  }

  holdingDialogVisible.value = true
}

// 保存持仓
const handleSaveHolding = async () => {
  if (!holdingForm.value.amount || holdingForm.value.amount <= 0) {
    ElMessage.warning('请填写持有金额')
    return
  }

  submittingHolding.value = true
  try {
    const payload = {
      fund_id: holdingForm.value.fund_id,
      amount: holdingForm.value.amount,
      auto_fetch_nav: true  // 启用自动获取净值
    }

    const response = await createOrUpdateHolding(payload)

    // 更新表单显示计算结果
    holdingForm.value.shares = Number(response.shares)
    holdingForm.value.cost_price = Number(response.cost_price)

    ElMessage.success('持仓设置成功，已自动获取净值')
    holdingDialogVisible.value = false
    await fetchFunds()
  } catch (error) {
    ElMessage.error('保存失败：' + (error.response?.data?.detail || error.message))
  } finally {
    submittingHolding.value = false
  }
}

// 显示交易对话框
const showTradeDialog = (fund) => {
  currentFund.value = fund
  tradeForm.value = {
    fund_id: fund.id,
    transaction_type: 'buy',
    amount: null,
    shares: null
  }
  sellMode.value = 'amount'
  tradeDialogVisible.value = true
}

// 执行交易
const handleTrade = async () => {
  if (tradeForm.value.transaction_type === 'buy') {
    if (!tradeForm.value.amount || tradeForm.value.amount <= 0) {
      ElMessage.warning('请输入买入金额')
      return
    }
  } else {
    // 卖出验证
    if (sellMode.value === 'amount') {
      if (!tradeForm.value.amount || tradeForm.value.amount <= 0) {
        ElMessage.warning('请输入卖出金额')
        return
      }
    } else {
      if (!tradeForm.value.shares || tradeForm.value.shares <= 0) {
        ElMessage.warning('请输入卖出份额')
        return
      }
    }
  }

  submittingTrade.value = true
  try {
    const payload = {
      fund_id: tradeForm.value.fund_id,
      transaction_type: tradeForm.value.transaction_type
    }

    if (tradeForm.value.transaction_type === 'buy') {
      payload.amount = tradeForm.value.amount
      const response = await buyFund(payload)
      ElMessage.success(`买入成功，获得 ${response.shares} 份`)
    } else {
      if (sellMode.value === 'amount') {
        payload.amount = tradeForm.value.amount
      } else {
        payload.shares = tradeForm.value.shares
      }
      const response = await sellFund(payload)
      ElMessage.success(`卖出成功，卖出 ${response.shares} 份`)
    }

    tradeDialogVisible.value = false
    await fetchFunds()
  } catch (error) {
    ElMessage.error('交易失败：' + (error.response?.data?.detail || error.message))
  } finally {
    submittingTrade.value = false
  }
}

const handleDelete = async (fund) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除基金 ${fund.fund_name || fund.fund_code} 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteFund(fund.id)
    ElMessage.success('删除成功')
    await fetchFunds()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchFunds()
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.fund-list {
  padding: 0;
}

.table-row {
  transition: all 0.2s ease;
}

.table-row:hover {
  background: rgba(6, 182, 212, 0.05);
}

/* Dialog Styles */
.dialog-sci-fi :deep(.el-dialog) {
  background-color: var(--navy-900-95);
  border: 1px solid var(--sci-cyan-30);
  backdrop-filter: blur(24px);
}

.dialog-sci-fi :deep(.el-dialog__header) {
  border-bottom: 1px solid var(--sci-cyan-20);
}

.dialog-sci-fi :deep(.el-dialog__title) {
  color: rgb(243 244 246);
}

.dialog-sci-fi :deep(.el-dialog__body) {
  color: rgb(209 213 219);
}

/* Form Styles */
.form-sci-fi :deep(.el-form-item__label) {
  color: rgb(209 213 219);
}

.alert-sci-fi {
  background-color: var(--sci-cyan-10);
  border: 1px solid var(--sci-cyan-30);
  color: rgba(0, 212, 255, 0.8);
}

/* Radio Group */
.radio-sci-fi :deep(.el-radio__label) {
  color: rgb(209 213 219);
}

.radio-sci-fi :deep(.el-radio__input.is-checked .el-radio__inner) {
  background-color: var(--sci-cyan);
  border-color: var(--sci-cyan);
}

/* Input Number */
.input-tech-number :deep(.el-input__inner) {
  background-color: var(--navy-900-50);
  border: 1px solid var(--sci-cyan-30);
  color: rgb(243 244 246);
}

.input-tech-number :deep(.el-input-number__decrease),
.input-tech-number :deep(.el-input-number__increase) {
  background-color: var(--navy-800);
  border: 1px solid var(--sci-cyan-20);
  color: var(--sci-cyan);
}

.input-tech-number :deep(.el-input-number__decrease:hover),
.input-tech-number :deep(.el-input-number__increase:hover) {
  background-color: var(--sci-cyan-20);
}

/* 基金代码输入框包装器 */
.fund-code-input-wrapper {
  display: flex;
  gap: 8px;
  align-items: center;
}

.fund-code-input-wrapper .el-input {
  flex: 1;
}

/* 查询按钮 */
.btn-search {
  min-width: 80px;
  flex-shrink: 0;
}

/* 查询状态提示 */
.query-status {
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.query-status.querying {
  background-color: rgba(0, 212, 255, 0.1);
  color: var(--sci-cyan);
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.query-status.success {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--sci-success);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.query-status.error {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--sci-danger);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

/* 状态图标动画 */
.status-icon {
  display: inline-block;
}

.query-status.querying .status-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
