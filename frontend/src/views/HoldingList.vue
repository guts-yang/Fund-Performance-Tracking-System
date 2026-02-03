<template>
  <div class="holding-list space-y-6">
    <!-- Main Card -->
    <div class="glass-card p-8">
      <!-- Card Header -->
      <div class="card-header flex items-center justify-between mb-8">
        <div class="flex items-center space-x-3">
          <span class="text-sci-cyan text-2xl">💼</span>
          <h3 class="text-xl font-semibold text-white">持仓管理</h3>
        </div>
      </div>

      <!-- Sci-Fi Table -->
      <div class="overflow-x-auto" v-loading="loading">
        <table class="table-sci-fi w-full">
          <thead>
            <tr>
              <th>基金代码</th>
              <th>基金名称</th>
              <th class="text-right">持有金额</th>
              <th class="text-right">持有份额</th>
              <th class="text-right">成本单价</th>
              <th class="text-right">总成本</th>
              <th>更新时间</th>
              <th class="text-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in holdings" :key="row.fund_id" class="table-row">
              <td class="font-mono-number text-sci-cyan text-base">{{ row.fund.fund_code }}</td>
              <td class="text-base">{{ row.fund.fund_name }}</td>
              <td class="text-right">
                <span class="font-mono-number text-gray-200 text-base">¥{{ formatNumber(row.amount) }}</span>
              </td>
              <td class="text-right">
                <span class="font-mono-number text-gray-300 text-base">{{ formatNumber(row.shares, 4) }}</span>
              </td>
              <td class="text-right">
                <span class="font-mono-number text-gray-400 text-base">¥{{ formatNumber(row.cost_price, 4) }}</span>
              </td>
              <td class="text-right">
                <span class="font-mono-number text-sci-cyan font-bold text-base">¥{{ formatNumber(row.cost) }}</span>
              </td>
              <td class="text-gray-400 text-sm">{{ formatDate(row.updated_at) }}</td>
              <td class="text-right">
                <div class="flex items-center justify-end space-x-3">
                  <button @click="showEditDialog(row)"
                          class="text-sci-cyan hover:text-sci-cyan/80 text-base font-medium transition-colors px-2 py-1 rounded hover:bg-sci-cyan/10">
                    编辑
                  </button>
                  <button @click="handleDelete(row)"
                          class="text-sci-danger hover:text-sci-danger/80 text-base font-medium transition-colors px-2 py-1 rounded hover:bg-sci-danger/10">
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Dialog -->
    <el-dialog v-model="editDialogVisible" title="编辑持仓" width="650px"
               class="dialog-sci-fi">
      <el-form :model="holdingForm" label-width="140px" class="form-sci-fi">
        <el-form-item label="基金代码">
          <el-input v-model="currentFund.fund_code" disabled class="input-tech" size="large" />
        </el-form-item>
        <el-form-item label="基金名称">
          <el-input v-model="currentFund.fund_name" disabled class="input-tech" size="large" />
        </el-form-item>
        <el-form-item label="持有金额">
          <el-input-number
            v-model="holdingForm.amount"
            :precision="2"
            :min="0"
            controls-position="right"
            class="input-tech-number w-full"
            size="large"
          />
        </el-form-item>
        <el-form-item label="持有份额">
          <el-input-number
            v-model="holdingForm.shares"
            :precision="4"
            :min="0"
            controls-position="right"
            class="input-tech-number w-full"
            size="large"
          />
        </el-form-item>
        <el-form-item label="成本单价">
          <el-input-number
            v-model="holdingForm.cost_price"
            :precision="4"
            :min="0"
            controls-position="right"
            class="input-tech-number w-full"
            size="large"
          />
        </el-form-item>
        <el-form-item label="总成本">
          <span class="text-2xl font-bold text-sci-cyan font-mono-number stat-value-glow">
            ¥{{ formatNumber(holdingForm.shares * holdingForm.cost_price) }}
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <button @click="editDialogVisible = false" class="btn-tech">取消</button>
        <button @click="handleUpdate" :disabled="submitting" class="btn-tech-primary">
          <span v-if="!submitting">保存</span>
          <span v-else class="animate-pulse">保存中...</span>
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getHoldings, updateHolding, deleteHolding } from '@/api/fund'
import { formatNumber, formatDate } from '@/utils/helpers'

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

onMounted(() => {
  fetchHoldings()
})
</script>

<style scoped>
.holding-list {
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
  font-size: 1.25rem;
}

.dialog-sci-fi :deep(.el-dialog__body) {
  color: rgb(209 213 219);
  font-size: 1rem;
}

/* Form Styles */
.form-sci-fi :deep(.el-form-item__label) {
  color: rgb(209 213 219);
  font-size: 1rem;
  font-weight: 500;
}

.form-sci-fi :deep(.el-form-item) {
  margin-bottom: 1.5rem;
}

/* Input Number */
.input-tech-number :deep(.el-input__wrapper) {
  background-color: var(--navy-900-50);
  border: 1px solid var(--sci-cyan-30);
  color: rgb(243 244 246);
  padding: 0.5rem 0.75rem;
  box-shadow: none;
}

.input-tech-number :deep(.el-input__inner) {
  color: rgb(243 244 246);
  font-size: 1rem;
  height: 40px;
  line-height: 40px;
}

.input-tech-number :deep(.el-input-number__decrease),
.input-tech-number :deep(.el-input-number__increase) {
  background-color: var(--navy-800);
  border: 1px solid var(--sci-cyan-20);
  color: var(--sci-cyan);
  width: 40px;
  height: 20px;
}

.input-tech-number :deep(.el-input-number__decrease:hover),
.input-tech-number :deep(.el-input-number__increase:hover) {
  background-color: var(--sci-cyan-20);
}
</style>
