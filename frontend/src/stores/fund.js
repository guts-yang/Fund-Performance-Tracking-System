import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getPortfolioSummary } from '@/api/fund'

export const useFundStore = defineStore('fund', () => {
  const summary = ref(null)
  const loading = ref(false)

  const fetchSummary = async () => {
    loading.value = true
    try {
      summary.value = await getPortfolioSummary()
    } finally {
      loading.value = false
    }
  }

  return {
    summary,
    loading,
    fetchSummary
  }
})
