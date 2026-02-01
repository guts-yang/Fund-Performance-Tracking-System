<template>
  <div class="holding-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>持仓管理</span>
        </div>
      </template>

      <el-table :data="holdings" stripe v-loading="loading">
        <el-table-column prop="fund.fund_code" label="基金代码" width="120" />
        <el-table-column prop="fund.fund_name" label="基金名称" />
        <el-table-column prop="amount" label="持有金额" align="right">
          <template #default="{ row }">
            ¥{{ formatNumber(row.amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="shares" label="持有份额" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.shares, 4) }}
          </template>
        </el-table-column>
        <el-table-column prop="cost_price" label="成本单价" align="right">
          <template #default="{ row }">
            ¥{{ formatNumber(row.cost_price, 4) }}
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="总成本" align="right">
          <template #default="{ row }">
            ¥{{ formatNumber(row.cost) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showEditDialog(row)">
              编辑
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Edit Dialog -->
    <el-dialog v-model="editDialogVisible" title="编辑持仓" width="600px">
      <el-form :model="holdingForm" label-width="120px">
        <el-form-item label="基金代码">
          <el-input v-model="currentFund.fund_code" disabled />
        </el-form-item>
        <el-form-item label="基金名称">
          <el-input v-model="currentFund.fund_name" disabled />
        </el-form-item>
        <el-form-item label="持有金额">
          <el-input-number
            v-model="holdingForm.amount"
            :precision="2"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="持有份额">
          <el-input-number
            v-model="holdingForm.shares"
            :precision="4"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="成本单价">
          <el-input-number
            v-model="holdingForm.cost_price"
            :precision="4"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="总成本">
          <span style="font-size: 16px; font-weight: bold; color: #409eff;">
            ¥{{ formatNumber(holdingForm.shares * holdingForm.cost_price) }}
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getHoldings, updateHolding, deleteHolding } from '@/api/fund'
import dayjs from 'dayjs'

const holdings = ref([])
const loading = ref(false)
const editDialogVisible = ref(false)
const submitting = ref(false)

const holdingForm = reactive({
  amount: 0,
  shares: 0,
  cost_price: 0
})

const currentFund = ref({
  fund_code: '',
  fund_name: ''
})

const currentFundId = ref(null)

const fetchHoldings = async () => {
  loading.value = true
  try {
    holdings.value = await getHoldings()
  } finally {
    loading.value = false
  }
}

const showEditDialog = (holding) => {
  currentFundId.value = holding.fund_id
  currentFund.value = {
    fund_code: holding.fund.fund_code,
    fund_name: holding.fund.fund_name
  }
  holdingForm.amount = Number(holding.amount)
  holdingForm.shares = Number(holding.shares)
  holdingForm.cost_price = Number(holding.cost_price)
  editDialogVisible.value = true
}

const handleUpdate = async () => {
  submitting.value = true
  try {
    await updateHolding(currentFundId.value, holdingForm)
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    await fetchHoldings()
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (holding) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${holding.fund.fund_name} 的持仓吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteHolding(holding.fund_id)
    ElMessage.success('删除成功')
    await fetchHoldings()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined) return '0.00'
  return Number(num).toFixed(decimals)
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  fetchHoldings()
})
</script>

<style scoped>
.holding-list {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
