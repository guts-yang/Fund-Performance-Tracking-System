<template>
  <div class="fund-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>基金管理</span>
          <div>
            <el-tag v-if="autoRefresh" type="success" style="margin-right: 10px;">
              自动刷新中 ({{ lastUpdateTime ? lastUpdateTime : '--:--:--' }})
            </el-tag>
            <el-button @click="toggleAutoRefresh" style="margin-right: 10px;">
              {{ autoRefresh ? '关闭自动刷新' : '开启自动刷新' }}
            </el-button>
            <el-button type="primary" @click="showAddDialog">
              <el-icon><Plus /></el-icon> 添加基金
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="funds" stripe v-loading="loading">
        <el-table-column prop="fund_code" label="基金名称" width="200">
          <template #default="{ row }">
            {{ row.fund_name || row.fund_code }}
          </template>
        </el-table-column>
        <el-table-column prop="fund_type" label="基金类型" width="150" />
        <el-table-column label="持有金额" align="right" width="150">
          <template #default="{ row }">
            <span v-if="row.holdings && row.holdings.amount">
              ¥{{ formatNumber(row.holdings.amount) }}
            </span>
            <span v-else style="color: #ccc;">未设置</span>
          </template>
        </el-table-column>
        <el-table-column label="持有份额" align="right" width="150">
          <template #default="{ row }">
            <span v-if="row.holdings && row.holdings.shares">
              {{ formatNumber(row.holdings.shares) }} 份
            </span>
            <span v-else style="color: #ccc;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="最新净值" align="right" width="120">
          <template #default="{ row }">
            <span v-if="row.latest_nav_value" style="color: #909399; font-size: 12px;">
              正式
            </span>
            <div v-if="row.latest_nav_value">
              ¥{{ formatNumber(row.latest_nav_value, 4) }}
            </div>
            <div v-else style="color: #ccc;">-</div>
          </template>
        </el-table-column>
        <el-table-column label="实时涨跌幅" align="right" width="150">
          <template #default="{ row }">
            <div v-if="row.increase_rate !== null && row.increase_rate !== undefined">
              <div :class="row.increase_rate >= 0 ? 'text-red' : 'text-green'" style="font-size: 20px; font-weight: bold;">
                {{ row.increase_rate >= 0 ? '+' : '' }}{{ formatNumber(row.increase_rate, 2) }}%
              </div>
              <div style="font-size: 12px; color: #909399;">
                实时估算
              </div>
            </div>
            <div v-else style="color: #ccc; font-size: 12px;">非交易时间</div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="350" fixed="right">
          <template #default="{ row }">
            <el-button type="success" link @click="showTradeDialog(row)">
              交易
            </el-button>
            <el-button type="primary" link @click="showSetHoldingDialog(row)">
              设置持仓
            </el-button>
            <el-button type="primary" link @click="handleSync(row)" :loading="syncing[row.id]">
              <el-icon><Refresh /></el-icon> 同步
            </el-button>
            <el-button type="primary" link @click="$router.push(`/funds/${row.id}`)">
              详情
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Add Fund Dialog -->
    <el-dialog v-model="addDialogVisible" title="添加基金" width="500px">
      <el-form :model="fundForm" label-width="100px">
        <el-form-item label="基金代码">
          <el-input
            v-model="fundForm.fund_code"
            placeholder="请输入6位基金代码，如：000001"
            @blur="handleFetchFundInfo"
            :disabled="fetchingInfo"
            maxlength="6"
          />
          <span v-if="fetchingInfo" style="color: #409eff; font-size: 12px; margin-top: 5px; display: block;">
            正在获取基金信息...
          </span>
        </el-form-item>
        <el-form-item label="基金名称">
          <el-input v-model="fundForm.fund_name" placeholder="自动获取，可手动修改" />
        </el-form-item>
        <el-form-item label="基金类型">
          <el-input v-model="fundForm.fund_type" placeholder="自动获取，可手动修改" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAdd" :loading="submitting">确定添加</el-button>
      </template>
    </el-dialog>

    <!-- Set Holding Dialog -->
    <el-dialog v-model="holdingDialogVisible" title="设置持仓" width="600px">
      <el-form :model="holdingForm" label-width="120px">
        <el-alert
          title="只需填写持有金额，系统将自动获取最新净值计算份额"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        />

        <el-form-item label="持有金额">
          <el-input-number
            v-model="holdingForm.amount"
            :precision="2"
            :min="0"
            placeholder="请输入持有金额"
            style="width: 200px;"
          />
          <span style="margin-left: 10px; color: #909399;">元</span>
        </el-form-item>

        <el-divider content-position="left">自动计算结果</el-divider>

        <el-form-item label="持有份额">
          <span style="color: #67c23a;">
            {{ formatNumber(holdingForm.shares, 4) }} 份
          </span>
        </el-form-item>

        <el-form-item label="成本单价">
          <span style="color: #67c23a;">
            ¥{{ formatNumber(holdingForm.cost_price, 4) }}
          </span>
        </el-form-item>

        <el-form-item label="总成本">
          <span style="font-size: 18px; font-weight: bold; color: #409eff;">
            ¥{{ formatNumber(holdingForm.shares * holdingForm.cost_price) }}
          </span>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="holdingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveHolding" :loading="submittingHolding">
          保存持仓
        </el-button>
      </template>
    </el-dialog>

    <!-- Trade Dialog -->
    <el-dialog v-model="tradeDialogVisible" title="基金交易" width="600px">
      <el-form :model="tradeForm" label-width="120px">
        <el-form-item label="交易类型">
          <el-radio-group v-model="tradeForm.transaction_type">
            <el-radio value="buy">买入</el-radio>
            <el-radio value="sell">卖出</el-radio>
          </el-radio-group>
        </el-form-item>

        <template v-if="tradeForm.transaction_type === 'buy'">
          <el-form-item label="买入金额">
            <el-input-number
              v-model="tradeForm.amount"
              :precision="2"
              :min="0"
              placeholder="请输入买入金额"
              style="width: 200px;"
            />
            <span style="margin-left: 10px; color: #909399;">元</span>
          </el-form-item>
        </template>

        <template v-if="tradeForm.transaction_type === 'sell'">
          <el-form-item label="卖出方式">
            <el-radio-group v-model="sellMode">
              <el-radio value="amount">按金额</el-radio>
              <el-radio value="shares">按份额</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item v-if="sellMode === 'amount'" label="卖出金额">
            <el-input-number
              v-model="tradeForm.amount"
              :precision="2"
              :min="0"
              :max="maxSellAmount"
              placeholder="请输入卖出金额"
              style="width: 200px;"
            />
            <span style="margin-left: 10px; color: #909399;">元</span>
            <span style="margin-left: 10px; color: #909399;">最大可卖出: ¥{{ formatNumber(maxSellAmount) }}</span>
          </el-form-item>

          <el-form-item v-else label="卖出份额">
            <el-input-number
              v-model="tradeForm.shares"
              :precision="4"
              :min="0"
              :max="maxSellShares"
              placeholder="请输入卖出份额"
              style="width: 200px;"
            />
            <span style="margin-left: 10px; color: #909399;">份</span>
            <span style="margin-left: 10px; color: #909399;">最大可卖出: {{ formatNumber(maxSellShares, 4) }} 份</span>
          </el-form-item>
        </template>

        <el-alert
          v-if="tradeForm.transaction_type === 'buy'"
          title="系统将自动获取当日净值计算买入份额"
          type="info"
          :closable="false"
          style="margin-top: 20px;"
        />
        <el-alert
          v-else
          title="系统将自动获取当日净值，卖出后成本价保持不变"
          type="warning"
          :closable="false"
          style="margin-top: 20px;"
        />
      </el-form>

      <template #footer>
        <el-button @click="tradeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleTrade" :loading="submittingTrade">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { getFunds, createFund, deleteFund, syncFund, getFundInfoByCode, createOrUpdateHolding, buyFund, sellFund, getBatchRealtimeValuation } from '@/api/fund'
import dayjs from 'dayjs'

const router = useRouter()
const funds = ref([])
const loading = ref(false)
const syncing = ref({})
const addDialogVisible = ref(false)
const submitting = ref(false)
const fetchingInfo = ref(false)
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
}

const handleAdd = async () => {
  if (!fundForm.fund_code) {
    ElMessage.warning('请输入基金代码')
    return
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

// 自动获取基金信息
const handleFetchFundInfo = async () => {
  const code = fundForm.fund_code.trim()
  if (!code || code.length !== 6) {
    return
  }

  fetchingInfo.value = true
  try {
    const info = await getFundInfoByCode(code)
    // 自动填充基金名称和类型
    fundForm.fund_name = info.fund_name || ''
    fundForm.fund_type = info.fund_type || '开放式基金'
    ElMessage.success('基金信息已自动获取')
  } catch (error) {
    console.warn('获取基金信息失败，可手动输入', error)
  } finally {
    fetchingInfo.value = false
  }
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

// 格式化数字
const formatNumber = (num) => {
  if (num === null || num === undefined || isNaN(num)) return '0.00'
  return Number(num).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
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

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
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
