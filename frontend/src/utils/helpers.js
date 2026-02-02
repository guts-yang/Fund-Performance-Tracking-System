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
