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

LLM 模式（见 .env 配置）：
  - LLM_PROVIDER=ollama → 调用局域网内另一台机器上的 Ollama（默认 qwen3:8b）
  - LLM_PROVIDER=openai → 调用 OpenAI 兼容接口（需 OPENAI_API_KEY）
  - 未配置 / 调用失败 → 自动降级为本地规则引擎（保证系统可演示）

排障：GET /ai/llm-status?ping=true 可查看当前配置并探测 Ollama 连通性。
"""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

import config
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
    cfg = config.active()
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "service": "nutritionist-ai",
            "llm_mode": "llm" if config.LLM_ENABLED else "local",
            "provider": cfg["provider"],
            "model": cfg["model"],
        },
    }


@app.get("/health")
def health():
    return {"code": 200, "msg": "success", "data": {"status": "up"}}


@app.get("/ai/llm-status")
def llm_status(ping: bool = False):
    """
    查看当前 LLM 配置。
    ping=true 时额外探测后端是否可达，并列出可用模型（便于核对 qwen3:8b 是否已拉取）。
    """
    cfg = config.active()
    info = {
        "provider": cfg["provider"],
        "base_url": cfg["base_url"],
        "model": cfg["model"],
        "vision_model": cfg["vision_model"] or None,
        "timeout_sec": config.LLM_TIMEOUT,
        "enabled": config.LLM_ENABLED,
        "config_file": str(Path(__file__).parent / ".env"),
    }

    if ping:
        try:
            if cfg["provider"] == "ollama":
                url = config.OLLAMA_HOST + "/api/tags"
                headers = {}
            else:
                # OpenAI 兼容端点（书生等）必须带 Bearer Key，否则 401 误报
                url = cfg["base_url"].rstrip("/") + "/models"
                headers = {"Authorization": f"Bearer {cfg['api_key']}"} if cfg["api_key"] else {}
            req = Request(url, headers=headers)
            with urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("name") or m.get("id")
                      for m in (data.get("models") or data.get("data") or [])]
            info["ping"] = "ok"
            info["available_models"] = models

            info["model_ready"] = cfg["model"] in models
        except Exception as e:
            info["ping"] = "failed"
            info["error"] = str(e)
            if cfg["provider"] == "ollama":
                info["hint"] = ("请确认：① .env 里 OLLAMA_HOST 的 IP 是否正确 "
                                "② 对方机器已启动 ollama serve "
                                "③ 对方防火墙放行 11434 端口")
            else:
                info["hint"] = ("请确认：① .env 里 INTERNAI_API_KEY（或其他 KEY）"
                                "是否正确且有效 ② 平台是否已开通该模型权限")

    return {"code": 200, "msg": "success", "data": info}
