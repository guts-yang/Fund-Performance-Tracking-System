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
export const updateHolding = (fundId, data) => api.put(`/holdings/${fundId}`, data)
export const deleteHolding = (fundId) => api.delete(`/holdings/${fundId}`)

// NAV APIs
export const getLatestNav = (fundCode) => api.get(`/nav/${fundCode}`)
export const getNavHistory = (fundCode, params = {}) => api.get(`/nav/${fundCode}/history`, { params })
export const syncAllNav = () => api.post('/nav/sync-all')
export const getRealtimeValuation = (fundCode) => api.get(`/nav/${fundCode}/realtime`)
// 批量获取基金实时估值（基于股票持仓）
export const getBatchRealtimeValuation = (fundCodes) => api.post('/nav/realtime/batch-stock', fundCodes)

// PnL APIs
export const getPortfolioSummary = () => api.get('/pnl/summary')
export const getDailyPnL = (fundId, params = {}) => api.get(`/pnl/daily/${fundId}`, { params })
export const getPnLChartData = (fundId, params = {}) => api.get(`/pnl/chart/${fundId}`, { params })

// Transaction APIs
export const buyFund = (data) => api.post('/transactions/buy', data)
export const sellFund = (data) => api.post('/transactions/sell', data)
export const getTransactions = (fundId, params = {}) => api.get(`/transactions/${fundId}`, { params })

// Stock Position APIs
export const getFundStockPositions = (fundId, params = {}) => api.get(`/stock-positions/funds/${fundId}`, { params })
export const syncFundStockPositions = (fundId) => api.post(`/stock-positions/funds/${fundId}/sync`)
export const getStockRealtimeNav = (fundCode) => api.get(`/nav/${fundCode}/realtime-stock`)
