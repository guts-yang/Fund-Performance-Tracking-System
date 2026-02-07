import { ref, computed } from 'vue'
import { getFunds, getFundStockPositions, syncFundStockPositions } from '@/api/fund'
import { ElMessage } from 'element-plus'
import axios from 'axios'

export function useStockPositions(fundId, reportDate, market, searchKeyword) {
  const stockPositions = ref([])
  const loading = ref(false)
  const fundsList = ref([])

  const pagination = ref({
    currentPage: 1,
    pageSize: 20,
    total: 0
  })

  // 获取所有基金的持仓数据
  const fetchAllPositions = async () => {
    loading.value = true
    try {
      // 获取基金列表
      if (fundsList.value.length === 0) {
        const funds = await getFunds()
        fundsList.value = funds || []
      }

      // 确定要查询的基金
      const targetFundIds = fundId.value
        ? [fundId.value]
        : fundsList.value.map(f => f.id)

      if (targetFundIds.length === 0) {
        stockPositions.value = []
        return
      }

      // 并发查询所有基金的持仓
      const promises = targetFundIds.map(id =>
        getFundStockPositions(id, reportDate.value ? { report_date: reportDate.value } : {})
      )

      const results = await Promise.allSettled(promises)

      // 处理结果
      const allPositions = []
      results.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value) {
          // 为每条持仓记录添加基金信息
          const fund = fundsList.value.find(f => f.id === targetFundIds[index])
          const positionsWithFund = (result.value || []).map(p => ({
            ...p,
            fund_id: targetFundIds[index],
            fund_code: fund?.fund_code || '',
            fund_name: fund?.fund_name || ''
          }))
          allPositions.push(...positionsWithFund)
        }
      })

      stockPositions.value = allPositions

      // 更新分页
      pagination.value.total = allPositions.length
      pagination.value.currentPage = 1

    } catch (error) {
      console.error('获取持仓数据失败:', error)
      ElMessage.error('获取持仓数据失败')
      stockPositions.value = []
    } finally {
      loading.value = false
    }
  }

  // 筛选后的数据
  const filteredPositions = computed(() => {
    let data = stockPositions.value

    // 市场筛选
    if (market.value && market.value !== 'all') {
      data = data.filter(p => {
        const code = p.stock_code
        if (market.value === 'a-share') return code.endsWith('.SZ') || code.endsWith('.SH')
        if (market.value === 'hk') return code.endsWith('.HK')
        if (market.value === 'us') return !code.endsWith('.SZ') && !code.endsWith('.SH') && !code.endsWith('.HK')
        return true
      })
    }

    // 搜索筛选
    if (searchKeyword.value && searchKeyword.value.trim()) {
      const keyword = searchKeyword.value.trim().toLowerCase()
      data = data.filter(p => {
        return (p.stock_name && p.stock_name.toLowerCase().includes(keyword)) ||
               (p.stock_code && p.stock_code.toLowerCase().includes(keyword)) ||
               (p.fund_name && p.fund_name.toLowerCase().includes(keyword))
      })
    }

    // 默认按占净值比例降序
    return data.sort((a, b) => (b.weight || 0) - (a.weight || 0))
  })

  // 分页数据
  const paginatedPositions = computed(() => {
    const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
    const end = start + pagination.value.pageSize
    return filteredPositions.value.slice(start, end)
  })

  // 提取可用报告期
  const availableReportDates = computed(() => {
    const dates = [...new Set(stockPositions.value.map(p => p.report_date).filter(d => d))]
    return dates.sort((a, b) => new Date(b) - new Date(a))
  })

  // 同步持仓
  const syncPositions = async (targetFundId) => {
    try {
      const response = await syncFundStockPositions(targetFundId)
      if (response?.data?.success) {
        ElMessage.success(`成功同步 ${response.data.funds_updated} 条持仓记录`)
        return true
      } else {
        ElMessage.error(response?.data?.message || '同步失败')
        return false
      }
    } catch (error) {
      console.error('同步持仓失败:', error)
      const errorMsg = error.response?.data?.detail || error.message
      ElMessage.error('同步持仓失败: ' + errorMsg)
      return false
    }
  }

  // 检查数据质量
  const checkQuality = async (targetFundId) => {
    try {
      const response = await axios.get(`/api/stock-positions/funds/${targetFundId}/quality`)
      return response.data
    } catch (error) {
      console.error('检查数据质量失败:', error)
      ElMessage.error('检查数据质量失败')
      return null
    }
  }

  // 批量修复名称
  const fixNames = async (targetFundId) => {
    try {
      const response = await axios.post('/api/stock-positions/admin/fix-names', {
        fund_id: targetFundId
      })
      if (response.data?.success) {
        ElMessage.success(`成功修复 ${response.data.funds_updated} 条股票名称`)
        return true
      } else {
        ElMessage.error(response.data?.message || '修复失败')
        return false
      }
    } catch (error) {
      console.error('修复名称失败:', error)
      ElMessage.error('修复名称失败')
      return false
    }
  }

  return {
    fundsList,
    stockPositions,
    loading,
    availableReportDates,
    pagination,
    filteredPositions,
    paginatedPositions,
    fetchAllPositions,
    syncPositions,
    checkQuality,
    fixNames
  }
}
