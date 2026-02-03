import dayjs from 'dayjs'

/**
 * 格式化数字，保留指定小数位，添加千分位分隔符
 * @param {number|string} num - 要格式化的数字
 * @param {number} decimals - 小数位数，默认2位
 * @returns {string} 格式化后的数字字符串
 *
 * @example
 * formatNumber(1234.567) => "1,234.57"
 * formatNumber(1234.567, 3) => "1,234.567"
 * formatNumber(null) => "0.00"
 */
export function formatNumber(num, decimals = 2) {
  if (num === null || num === undefined || isNaN(num)) return '0.00'
  return Number(num).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 格式化日期
 * @param {string|Date} date - 日期对象或字符串
 * @param {string} format - 日期格式，默认 'YYYY-MM-DD'
 * @returns {string} 格式化后的日期字符串
 *
 * @example
 * formatDate('2025-02-02') => "2025-02-02"
 * formatDate('2025-02-02', 'YYYY-MM-DD HH:mm:ss') => "2025-02-02 00:00:00"
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return '-'
  return dayjs(date).format(format)
}

/**
 * 格式化日期时间（完整格式）
 * @param {string|Date} datetime - 日期时间对象或字符串
 * @returns {string} 格式化后的日期时间字符串 (YYYY-MM-DD HH:mm:ss)
 */
export function formatDateTime(datetime) {
  return formatDate(datetime, 'YYYY-MM-DD HH:mm:ss')
}

/**
 * 对数组进行排序
 * @param {Array} array - 要排序的数组
 * @param {String} key - 排序键名（支持嵌套，如 'holdings.amount'）
 * @param {String} order - 'asc' | 'desc'
 * @param {String} type - 'number' | 'string' | 'date'
 * @returns {Array} 排序后的数组
 *
 * @example
 * sortArray(funds, 'amount', 'desc', 'number')
 * sortArray(funds, 'holdings.amount', 'asc', 'number')
 */
export function sortArray(array, key, order = 'desc', type = 'number') {
  if (!array || !Array.isArray(array)) return []

  return [...array].sort((a, b) => {
    // 支持嵌套属性访问
    const getNestedValue = (obj, path) => {
      return path.split('.').reduce((current, prop) => current?.[prop], obj)
    }

    let aVal = getNestedValue(a, key)
    let bVal = getNestedValue(b, key)

    // 处理 null/undefined
    if (aVal == null) aVal = type === 'number' ? 0 : ''
    if (bVal == null) bVal = type === 'number' ? 0 : ''

    let comparison = 0
    if (type === 'number') {
      comparison = Number(aVal) - Number(bVal)
    } else if (type === 'string') {
      comparison = String(aVal).localeCompare(String(bVal), 'zh-CN')
    } else if (type === 'date') {
      comparison = new Date(aVal) - new Date(bVal)
    }

    return order === 'desc' ? -comparison : comparison
  })
}
