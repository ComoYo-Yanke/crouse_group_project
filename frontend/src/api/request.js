import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

/**
 * axios 实例
 * 统一响应格式：{ code, msg, data }
 */

// 业务接口（SpringBoot，8080）：普通请求 30 秒足够
const request = axios.create({
  baseURL: '/',
  timeout: 30000
})

// AI 接口（FastAPI 8000 → 局域网 Ollama）：
// 8B 模型推理通常要几十秒，30 秒会超时失败，这里给足 180 秒。
// 该值需与 ai-service/.env 里的 LLM_TIMEOUT 保持一致。
const aiRequest = axios.create({
  baseURL: '/',
  timeout: 180000
})

function attachInterceptors(instance) {
  // 请求拦截器：附加 JWT
  instance.interceptors.request.use(
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
  instance.interceptors.response.use(
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
      // 用户主动取消（点「停止生成」）：静默处理，不弹错误提示，由调用方决定
      if (axios.isCancel(error)) {
        return Promise.reject(error)
      }
      // HTTP 层错误
      const status = error.response?.status
      if (status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        localStorage.removeItem('token')
        router.push('/login')
      } else if (error.code === 'ECONNABORTED') {
        ElMessage.error('AI 响应超时，请稍后重试（模型推理较慢属正常现象）')
      } else {
        ElMessage.error(error.response?.data?.msg || error.message || '网络错误')
      }
      return Promise.reject(error)
    }
  )
}

attachInterceptors(request)
attachInterceptors(aiRequest)

export default request
export { aiRequest }
