<template>
  <div class="holdings-filters glass-card p-4 mb-6">
    <el-row :gutter="16">
      <!-- Search -->
      <el-col :span="6">
        <el-input
          v-model="localSearch"
          placeholder="搜索基金代码/名称"
          prefix-icon="Search"
          clearable
          size="default"
          class="filter-input"
        />
      </el-col>

      <!-- Profit Filter -->
      <el-col :span="4">
        <el-select
          v-model="localProfitFilter"
          placeholder="盈亏状态"
          clearable
          size="default"
          class="filter-select"
        >
          <el-option label="全部" value="" />
          <el-option label="仅盈利" value="profit" />
          <el-option label="仅亏损" value="loss" />
        </el-select>
      </el-col>

      <!-- Amount Range -->
      <el-col :span="4">
        <el-select
          v-model="localAmountRange"
          placeholder="持有金额"
          clearable
          size="default"
          class="filter-select"
        >
          <el-option label="全部" value="" />
          <el-option label="< 1万" value="small" />
          <el-option label="1万-10万" value="medium" />
          <el-option label="> 10万" value="large" />
        </el-select>
      </el-col>

      <!-- Sort By -->
      <el-col :span="4">
        <el-select
          v-model="localSortBy"
          placeholder="排序方式"
          size="default"
          class="filter-select"
        >
          <el-option label="持有金额" value="amount" />
          <el-option label="收益率" value="profit_rate" />
          <el-option label="今日收益" value="daily_profit_rate" />
        </el-select>
      </el-col>

      <!-- Sort Order -->
      <el-col :span="6">
        <div class="flex items-center space-x-2">
          <el-button-group class="sort-buttons">
            <el-button
              :type="localSortOrder === 'desc' ? 'primary' : ''"
              @click="localSortOrder = 'desc'"
              size="default"
            >
              降序 ↓
            </el-button>
            <el-button
              :type="localSortOrder === 'asc' ? 'primary' : ''"
              @click="localSortOrder = 'asc'"
              size="default"
            >
              升序 ↑
            </el-button>
          </el-button-group>
          <el-button
            v-if="hasActiveFilters"
            @click="resetFilters"
            size="default"
            class="ml-auto"
          >
            重置
          </el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  search: String,
  profitFilter: String,
  amountRange: String,
  sortBy: String,
  sortOrder: String
})

const emit = defineEmits([
  'update:search',
  'update:profitFilter',
  'update:amountRange',
  'update:sortBy',
  'update:sortOrder'
])

const localSearch = ref(props.search || '')
const localProfitFilter = ref(props.profitFilter || '')
const localAmountRange = ref(props.amountRange || '')
const localSortBy = ref(props.sortBy || 'amount')
const localSortOrder = ref(props.sortOrder || 'desc')

// Watch for changes and emit
watch(localSearch, (val) => emit('update:search', val))
watch(localProfitFilter, (val) => emit('update:profitFilter', val))
watch(localAmountRange, (val) => emit('update:amountRange', val))
watch(localSortBy, (val) => emit('update:sortBy', val))
watch(localSortOrder, (val) => emit('update:sortOrder', val))

// Check if any filters are active
const hasActiveFilters = computed(() => {
  return localSearch.value ||
         localProfitFilter.value ||
         localAmountRange.value ||
         localSortBy.value !== 'amount' ||
         localSortOrder.value !== 'desc'
})

// Reset all filters
const resetFilters = () => {
  localSearch.value = ''
  localProfitFilter.value = ''
  localAmountRange.value = ''
  localSortBy.value = 'amount'
  localSortOrder.value = 'desc'
}
</script>

<style scoped>
.holdings-filters {
  border-radius: 12px;
}

.glass-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(6, 182, 212, 0.15);
}

.filter-input :deep(.el-input__wrapper) {
  background-color: rgba(15, 23, 42, 0.8);
  border-color: rgba(6, 182, 212, 0.2);
  box-shadow: none;
}

.filter-input :deep(.el-input__wrapper:hover),
.filter-input :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(0, 212, 255, 0.5);
  box-shadow: 0 0 0 1px rgba(0, 212, 255, 0.1);
}

.filter-input :deep(.el-input__inner) {
  color: #e2e8f0;
}

.filter-select {
  width: 100%;
}

.filter-select :deep(.el-select__wrapper) {
  background-color: rgba(15, 23, 42, 0.8);
  border-color: rgba(6, 182, 212, 0.2);
  box-shadow: none;
}

.filter-select :deep(.el-select__wrapper:hover),
.filter-select :deep(.el-select__wrapper.is-focused) {
  border-color: rgba(0, 212, 255, 0.5);
  box-shadow: 0 0 0 1px rgba(0, 212, 255, 0.1);
}

.sort-buttons :deep(.el-button) {
  background-color: rgba(15, 23, 42, 0.8);
  border-color: rgba(6, 182, 212, 0.2);
  color: #94a3b8;
}

.sort-buttons :deep(.el-button:hover) {
  border-color: rgba(0, 212, 255, 0.5);
  color: #00d4ff;
}

.sort-buttons :deep(.el-button.el-button--primary) {
  background-color: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  color: #00d4ff;
}
</style>
