import request from './request'

/**
 * 记录模块 API
 * 文档：doc/api.md 三、记录模块
 */

// 新增记录（拍照/文字录入确认后保存）
export function createRecord(data) {
  // data: { foodName, portion, mealType, imageUrl, nutrition: {...}, visibility }
  return request.post('/api/record', data)
}

// 查询记录
export function getRecords(params) {
  // params: { date, mealType }
  return request.get('/api/record', { params })
}

// 删除记录
export function deleteRecord(recordId) {
  return request.delete(`/api/record/${recordId}`)
}

// 修改可见性
export function updateVisibility(recordId, visibility) {
  return request.put(`/api/record/${recordId}/visibility`, { visibility })
}

// 手动修正
export function updateRecord(recordId, data) {
  // data: { foodName, portion, nutrition }
  return request.put(`/api/record/${recordId}`, data)
}
