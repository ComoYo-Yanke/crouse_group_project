import request from './request'

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

// RAG 检索
export function ragSearch(query) {
  return request.post('/ai/rag', { query })
}

// 建议生成
export function generateAdvice(data) {
  // data: { profile, todayIntake, gap }
  return request.post('/ai/advice', data)
}

// 菜谱生成
export function generateRecipe(data) {
  // data: { goal, budget, ingredients, avoid }
  return request.post('/ai/recipe', data)
}

// 安全拦截检查
export function safetyCheck(advice) {
  return request.post('/ai/safety-check', { advice })
}
