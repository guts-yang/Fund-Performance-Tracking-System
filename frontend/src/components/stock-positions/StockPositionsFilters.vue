<template>
  <div class="glass-card p-6 mb-6">
    <el-row :gutter="20">
      <!-- 基金选择 -->
      <el-col :span="6">
        <div class="filter-item">
          <label class="filter-label">基金</label>
          <el-select
            v-model="localFundId"
            placeholder="全部基金"
            clearable
            filterable
            class="w-full"
            @change="handleFundChange"
          >
            <el-option label="全部基金" :value="null" />
            <el-option
              v-for="fund in funds"
              :key="fund.id"
              :label="`${fund.fund_code} - ${fund.fund_name}`"
              :value="fund.id"
            />
          </el-select>
        </div>
      </el-col>

      <!-- 报告期选择 -->
      <el-col :span="6">
        <div class="filter-item">
          <label class="filter-label">报告期</label>
          <el-select
            v-model="localReportDate"
            placeholder="最新报告期"
            clearable
            class="w-full"
          >
            <el-option label="最新报告期" :value="null" />
            <el-option
              v-for="date in reportDates"
              :key="date"
              :label="date"
              :value="date"
            />
          </el-select>
        </div>
      </el-col>

      <!-- 市场筛选 -->
      <el-col :span="6">
        <div class="filter-item">
          <label class="filter-label">市场</label>
          <el-radio-group v-model="localMarket" class="w-full">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button label="a-share">A股</el-radio-button>
            <el-radio-button label="hk">港股</el-radio-button>
          </el-radio-group>
        </div>
      </el-col>

      <!-- 搜索 -->
      <el-col :span="6">
        <div class="filter-item">
          <label class="filter-label">搜索</label>
          <el-input
            v-model="localSearchKeyword"
            placeholder="股票代码/名称"
            clearable
          >
            <template #prefix>
              <span class="text-gray-400">🔍</span>
            </template>
          </el-input>
        </div>
      </el-col>
    </el-row>

    <!-- 操作按钮 -->
    <el-row :gutter="10" class="mt-4">
      <el-col :span="24">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <button
              @click="handleSync"
              :disabled="!localFundId || loading"
              class="btn-tech text-sm flex items-center space-x-2"
              :class="(!localFundId || loading) ? 'opacity-50 cursor-not-allowed' : ''"
            >
              <span v-if="!loading">⟳</span>
              <span v-else class="animate-spin">⟳</span>
              <span>{{ loading ? '同步中...' : '同步持仓' }}</span>
            </button>

            <button
              @click="handleCheckQuality"
              :disabled="!localFundId"
              class="btn-tech text-sm"
              :class="!localFundId ? 'opacity-50 cursor-not-allowed' : ''"
            >
              <span>📊</span>
              <span>数据质量</span>
            </button>
          </div>

          <div class="text-sm text-gray-400">
            <span v-if="localFundId">已选择基金</span>
            <span v-else>显示全部基金的持仓</span>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  fundId: {
    type: Number,
    default: null
  },
  reportDate: {
    type: String,
    default: null
  },
  market: {
    type: String,
    default: 'all'
  },
  searchKeyword: {
    type: String,
    default: ''
  },
  funds: {
    type: Array,
    default: () => []
  },
  reportDates: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'update:fundId',
  'update:reportDate',
  'update:market',
  'update:searchKeyword',
  'sync',
  'checkQuality'
])

// Local state for two-way binding
const localFundId = ref(props.fundId)
const localReportDate = ref(props.reportDate)
const localMarket = ref(props.market)
const localSearchKeyword = ref(props.searchKeyword)

// Watch for prop changes
watch(() => props.fundId, (newVal) => {
  localFundId.value = newVal
})

watch(() => props.reportDate, (newVal) => {
  localReportDate.value = newVal
})

watch(() => props.market, (newVal) => {
  localMarket.value = newVal
})

watch(() => props.searchKeyword, (newVal) => {
  localSearchKeyword.value = newVal
})

// Emit changes
watch(localFundId, (newVal) => {
  emit('update:fundId', newVal)
})

watch(localReportDate, (newVal) => {
  emit('update:reportDate', newVal)
})

watch(localMarket, (newVal) => {
  emit('update:market', newVal)
})

watch(localSearchKeyword, (newVal) => {
  emit('update:searchKeyword', newVal)
})

// Event handlers
const handleSync = () => {
  emit('sync', localFundId.value)
}

const handleCheckQuality = () => {
  emit('checkQuality')
}

const handleFundChange = () => {
  // Reset report date when fund changes
  localReportDate.value = null
  emit('update:reportDate', null)
}
</script>

<style scoped>
.filter-item {
  margin-bottom: 0;
}

.filter-label {
  display: block;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.glass-card {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 12px;
}

.btn-tech {
  padding: 8px 16px;
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.3);
  border-radius: 6px;
  color: #00d4ff;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-tech:hover:not(.opacity-50) {
  background: rgba(6, 182, 212, 0.2);
  border-color: rgba(6, 182, 212, 0.5);
  box-shadow: 0 0 15px rgba(6, 182, 212, 0.3);
}

.btn-tech:disabled,
.btn-tech.opacity-50 {
  cursor: not-allowed;
  opacity: 0.5;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
