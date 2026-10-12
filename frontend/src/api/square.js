import request from './request'

/**
 * 社交模块 API
 * 文档：doc/api.md 五、社交模块
 */

// 公开广场
export function getSquare(params) {
  // params: { page, size, sort: 'time'|'likes', mealType }
  return request.get('/api/square', { params })
}

// 点赞/取消点赞
export function toggleLike(recordId) {
  return request.post(`/api/like/${recordId}`)
}

// 评论列表（分楼）
export function getComments(recordId) {
  return request.get(`/api/comment/${recordId}`)
}

// 发表评论
export function postComment(data) {
  // data: { recordId, content, parentId }
  return request.post('/api/comment', data)
}

// 删除评论
export function deleteComment(commentId) {
  return request.delete(`/api/comment/${commentId}`)
}
