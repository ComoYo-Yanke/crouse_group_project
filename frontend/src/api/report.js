import request from './request'

/**
 * 报告模块 API
 * 文档：doc/api.md 四、报告模块
 */

// 每日报告
export function getDailyReport(date) {
  return request.get('/api/report/daily', { params: { date } })
}

// 一周报告
export function getWeeklyReport(startDate) {
  return request.get('/api/report/weekly', { params: { start: startDate } })
}
