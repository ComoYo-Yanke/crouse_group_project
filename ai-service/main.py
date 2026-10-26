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
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from routers import recognize, advice, recipe, safety

app = FastAPI(
    title="私人营养师 AI 微服务",
    version="0.1.0",
    # 使用本地静态资源渲染文档：
    # FastAPI 默认 /docs 从 cdn.jsdelivr.net 拉取 Swagger UI，
    # 该 CDN 在国内常不可达，会导致页面白屏。此处改为本地托管。
    docs_url=None,
)

app.include_router(recognize.router)
app.include_router(advice.router)
app.include_router(recipe.router)
app.include_router(safety.router)

# 挂载本地 Swagger UI 资源
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static/swagger", StaticFiles(directory=str(STATIC_DIR)), name="swagger-static")


@app.get("/docs", include_in_schema=False)
def swagger_ui_html():
    """本地资源版 Swagger UI，离线可用"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
    )


@app.get("/", include_in_schema=False)
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
