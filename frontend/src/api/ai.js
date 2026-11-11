// 使用 AI 专用实例：超时 180 秒（本地大模型推理较慢，普通 30 秒会超时）
import { aiRequest as request } from './request'

/**
 * AI 微服务 API（Python FastAPI）
 * 文档：doc/api.md 六、AI微服务接口
 * 注意：走 /ai 前缀，vite 代理到 8000 端口
 */

// 食物识别（图片 Base64 或 文字描述）
export function recognizeFood(data) {
  // data: { imageBase64 } 或 { textDescription }
  return request.post('/ai/recognize', data)
}

// RAG 检索（纯本地检索，很快）
export function ragSearch(query) {
  return request.post('/ai/rag', { query })
}

// 建议生成
// config 可传 { signal } 用于中途取消（AbortController）
export function generateAdvice(data, config = {}) {
  // data: { profile, todayIntake, gap }
  return request.post('/ai/advice', data, config)
}

// 菜谱生成
export function generateRecipe(data, config = {}) {
  // data: { goal, budget, ingredients, avoid }
  return request.post('/ai/recipe', data, config)
}

// 安全拦截检查（纯规则校验，很快）
export function safetyCheck(advice) {
  return request.post('/ai/safety-check', { advice })
}

// 查看 LLM 配置与连通性（排障用）
export function llmStatus(ping = true) {
  return request.get('/ai/llm-status', { params: { ping } })
}
