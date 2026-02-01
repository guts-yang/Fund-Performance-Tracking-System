import api from './index'

// Fund APIs
export const getFunds = (params = {}) => api.get('/funds', { params })
export const getFund = (id) => api.get(`/funds/${id}`)
export const getFundInfoByCode = (fundCode) => api.get(`/funds/info/${fundCode}`)
export const createFund = (data) => api.post('/funds', data)
export const updateFund = (id, data) => api.put(`/funds/${id}`, data)
export const deleteFund = (id) => api.delete(`/funds/${id}`)
export const syncFund = (id) => api.post(`/funds/${id}/sync`)

// Holding APIs
export const getHoldings = (params = {}) => api.get('/holdings', { params })
export const getHolding = (fundId) => api.get(`/holdings/${fundId}`)
export const createOrUpdateHolding = (data) => api.post('/holdings', data)
export const createHolding = (data) => api.post('/holdings', data)
export const updateHolding = (fundId, data) => api.put(`/holdings/${fundId}`, data)
export const deleteHolding = (fundId) => api.delete(`/holdings/${fundId}`)

// NAV APIs
export const getLatestNav = (fundCode) => api.get(`/nav/${fundCode}`)
export const getNavHistory = (fundCode, params = {}) => api.get(`/nav/${fundCode}/history`, { params })
export const syncAllNav = () => api.post('/nav/sync-all')

// PnL APIs
export const getPortfolioSummary = () => api.get('/pnl/summary')
export const getDailyPnL = (fundId, params = {}) => api.get(`/pnl/daily/${fundId}`, { params })
export const getPnLChartData = (fundId, params = {}) => api.get(`/pnl/chart/${fundId}`, { params })
