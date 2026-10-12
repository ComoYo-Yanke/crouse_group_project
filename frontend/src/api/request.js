import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

/**
 * axios 实例
 * 统一响应格式：{ code, msg, data }
 */
const request = axios.create({
  baseURL: '/',
  timeout: 30000 // AI 识别可能较慢
})

// 请求拦截器：附加 JWT
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一处理 { code, msg, data }
request.interceptors.response.use(
  (response) => {
    const res = response.data
    // 非统一格式（如文件流）直接返回
    if (res === null || res === undefined || res.code === undefined) {
      return res
    }
    if (res.code === 200) {
      return res.data
    }
    if (res.code === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('token')
      router.push('/login')
      return Promise.reject(new Error(res.msg || '未登录'))
    }
    ElMessage.error(res.msg || '请求失败')
    return Promise.reject(new Error(res.msg || '请求失败'))
  },
  (error) => {
    // HTTP 层错误
    const status = error.response?.status
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('token')
      router.push('/login')
    } else {
      ElMessage.error(error.response?.data?.msg || error.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

export default request
