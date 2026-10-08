# -*- coding: utf-8 -*-
"""
私人营养师系统 - AI 微服务（Python FastAPI）

接口（doc/api.md 六）：
  POST /ai/recognize      食物识别（图片/文字）
  POST /ai/rag            RAG 检索膳食指南
  POST /ai/advice         建议生成
  POST /ai/recipe         菜谱生成
  POST /ai/safety-check   安全拦截

运行：uvicorn main:app --port 8000 --reload

LLM 模式：
  - 配置环境变量 OPENAI_API_KEY（及可选 OPENAI_BASE_URL）→ 调用真实 LLM
  - 未配置 → 自动降级为本地规则/知识库模式（保证系统可演示）
"""
import os

from fastapi import FastAPI

from routers import recognize, advice, recipe, safety

app = FastAPI(title="私人营养师 AI 微服务", version="0.1.0")

app.include_router(recognize.router)
app.include_router(advice.router)
app.include_router(recipe.router)
app.include_router(safety.router)


@app.get("/")
def root():
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "service": "nutritionist-ai",
            "llm_mode": "llm" if os.getenv("OPENAI_API_KEY") else "local",
        },
    }


@app.get("/health")
def health():
    return {"code": 200, "msg": "success", "data": {"status": "up"}}
