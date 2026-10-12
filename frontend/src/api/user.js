import request from './request'

/**
 * 用户模块 API
 * 文档：doc/api.md 二、用户模块
 */

// 注册
export function register(data) {
  // data: { username, password, height, weight, age, gender, goal, avoid, allergy }
  return request.post('/api/user/register', data)
}

// 登录
export function login(data) {
  // data: { username, password }
  return request.post('/api/user/login', data)
}

// 获取画像
export function getProfile() {
  return request.get('/api/user/profile')
}

// 更新画像
export function updateProfile(data) {
  return request.put('/api/user/profile', data)
}

// 个人主页
export function getUserHome(userId) {
  return request.get(`/api/user/${userId}/home`)
}
