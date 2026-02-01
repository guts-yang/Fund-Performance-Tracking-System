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
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
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
          <el-input v-model="fundForm.fund_code" placeholder="请输入基金代码，如：000001" />
        </el-form-item>
        <el-form-item label="基金名称">
          <el-input v-model="fundForm.fund_name" placeholder="可选，自动获取" />
        </el-form-item>
        <el-form-item label="基金类型">
          <el-input v-model="fundForm.fund_type" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAdd" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { getFunds, createFund, deleteFund, syncFund } from '@/api/fund'
import dayjs from 'dayjs'

const router = useRouter()
const funds = ref([])
const loading = ref(false)
const syncing = ref({})
const addDialogVisible = ref(false)
const submitting = ref(false)

const fundForm = reactive({
  fund_code: '',
  fund_name: '',
  fund_type: ''
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
