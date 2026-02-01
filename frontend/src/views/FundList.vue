<template>
  <div class="fund-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>基金管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon> 添加基金
          </el-button>
        </div>
      </template>

      <el-table :data="funds" stripe v-loading="loading">
        <el-table-column prop="fund_code" label="基金代码" width="120" />
        <el-table-column prop="fund_name" label="基金名称" />
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
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
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
          title="输入任意两个字段，第三个将自动计算"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        />

        <el-form-item label="持有金额">
          <el-input-number
            v-model="holdingForm.amount"
            :precision="2"
            :min="0"
            placeholder="持有金额"
            @change="calculateThirdField"
            style="width: 200px;"
          />
          <span style="margin-left: 10px; color: #909399;">元</span>
        </el-form-item>

        <el-form-item label="持有份额">
          <el-input-number
            v-model="holdingForm.shares"
            :precision="4"
            :min="0"
            placeholder="持有份额"
            @change="calculateThirdField"
            style="width: 200px;"
          />
          <span style="margin-left: 10px; color: #909399;">份</span>
        </el-form-item>

        <el-form-item label="成本单价">
          <el-input-number
            v-model="holdingForm.cost_price"
            :precision="4"
            :min="0"
            placeholder="成本单价"
            @change="calculateThirdField"
            style="width: 200px;"
          />
          <span style="margin-left: 10px; color: #909399;">元/份</span>
        </el-form-item>

        <el-divider />

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
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { getFunds, createFund, deleteFund, syncFund, getFundInfoByCode, createOrUpdateHolding } from '@/api/fund'
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

const fetchFunds = async () => {
  loading.value = true
  try {
    funds.value = await getFunds()
  } finally {
    loading.value = false
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
      amount: parseFloat(fund.holdings.amount) || null,
      shares: parseFloat(fund.holdings.shares) || null,
      cost_price: parseFloat(fund.holdings.cost_price) || null
    }
  }

  holdingDialogVisible.value = true
}

// 自动计算第三个字段
const calculateThirdField = () => {
  const { amount, shares, cost_price } = holdingForm.value

  // 统计已填写的字段数量
  const filled = [amount, shares, cost_price].filter(v => v !== null && v !== undefined && v > 0).length

  if (filled === 2) {
    // 输入两个字段，自动计算第三个
    if (amount && cost_price && !shares) {
      // 计算份额 = 金额 / 成本价
      holdingForm.value.shares = parseFloat((amount / cost_price).toFixed(4))
    } else if (amount && shares && !cost_price) {
      // 计算成本价 = 金额 / 份额
      holdingForm.value.cost_price = parseFloat((amount / shares).toFixed(4))
    } else if (shares && cost_price && !amount) {
      // 计算金额 = 份额 * 成本价
      holdingForm.value.amount = parseFloat((shares * cost_price).toFixed(2))
    }
  }
}

// 保存持仓
const handleSaveHolding = async () => {
  if (!holdingForm.value.amount || !holdingForm.value.shares || !holdingForm.value.cost_price) {
    ElMessage.warning('请填写完整持仓信息（或输入两个字段自动计算）')
    return
  }

  submittingHolding.value = true
  try {
    await createOrUpdateHolding(holdingForm.value)
    ElMessage.success('持仓设置成功')
    holdingDialogVisible.value = false
    await fetchFunds()
  } catch (error) {
    ElMessage.error('保存失败：' + (error.response?.data?.detail || error.message))
  } finally {
    submittingHolding.value = false
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
</style>
