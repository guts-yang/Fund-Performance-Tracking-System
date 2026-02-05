/**
 * 交易时间判断工具
 * 用于判断当前是否是股市交易时间，并动态调整刷新间隔
 */

/**
 * 判断当前是否是交易时间
 * @returns {boolean} 是否是交易时间
 *
 * 交易时间：
 * - 工作日（周一到周五）
 * - 9:30-15:00
 */
export function isTradingTime() {
  const now = new Date()

  // 判断是否是工作日（周一到周五，0=周日, 6=周六）
  const dayOfWeek = now.getDay()
  if (dayOfWeek === 0 || dayOfWeek === 6) {
    return false
  }

  // 判断时间是否在 9:30-15:00
  const currentHour = now.getHours()
  const currentMinute = now.getMinutes()

  // 9:30 开始
  if (currentHour < 9 || (currentHour === 9 && currentMinute < 30)) {
    return false
  }

  // 15:00 结束
  if (currentHour >= 15) {
    return false
  }

  return true
}

/**
 * 获取动态刷新间隔
 * @returns {number} 刷新间隔（毫秒）
 *
 * 交易时间：1分钟
 * 非交易时间：5分钟
 */
export function getDynamicRefreshInterval() {
  return isTradingTime() ? 60000 : 300000 // 交易时间 1min，非交易时间 5min
}
