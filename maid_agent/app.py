# -*- coding: utf-8 -*-
"""
app.py —— FastAPI 后端

职责：
  - 复用 my_first_agent.py 的 run_agent_events 核心逻辑（多轮记忆 + 工具循环 + 流式）
  - 对外提供聊天接口 /api/chat（SSE 流式）
  - 根路径 / 直接返回内置的女仆主题 HTML 聊天页

【需求8】对话记忆全部放在服务端内存里（SESSIONS 字典），不用任何数据库。
"""

import json
import os
import threading

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

# 复用原有 Agent 内核，不重写
from my_first_agent import (
    MODEL,
    OLLAMA_BASE_URL,
    build_initial_messages,
    client,
    run_agent_events,
    trim_history,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML = os.path.join(BASE_DIR, "static", "index.html")

app = FastAPI(title="贴身女仆 铃兰", version="1.0.0")


# ==================== 服务端内存记忆 ====================
# 【需求8】不用数据库，对话历史就放在这个进程内存里，重启即清空。
# 注意：这里刻意不写 dict[str, list] 这种注解，Python 3.8 下内置泛型下标会直接报
# TypeError。用 typing.Dict 或干脆不注解，兼容性最好。
SESSIONS = {}   # session_id -> messages 列表（含 system）
_LOCKS = {}     # session_id -> 锁，防止同一会话并发请求把历史写乱


def get_session_lock(session_id: str) -> threading.Lock:
    return _LOCKS.setdefault(session_id, threading.Lock())


def get_session(session_id: str) -> list:
    """取出会话历史，没有就新建一个（带女仆 system 提示词）。"""
    return SESSIONS.setdefault(session_id, build_initial_messages())


# ==================== 请求模型 ====================
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ResetRequest(BaseModel):
    session_id: str = "default"


# ==================== SSE 工具函数 ====================
def sse(payload: dict) -> str:
    """把事件打包成 SSE 格式的一帧。"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # 关掉 nginx 缓冲，保证逐字推送
}


# ==================== 路由 ====================

@app.get("/", response_class=HTMLResponse)
def index():
    """【需求4】访问根路径直接返回内置的聊天页面。"""
    try:
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        return HTMLResponse(
            "<h1>找不到 static/index.html</h1><p>请确认它和 app.py 在同一个项目目录下。</p>",
            status_code=500,
        )
    # 开发时改完 HTML 刷新即生效
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})


@app.post("/api/chat")
def chat(req: ChatRequest):
    """
    聊天接口，SSE 流式返回。

    注意：这里用的是普通（同步）生成器，Starlette 会把它丢到线程池里迭代，
    所以同步的 OpenAI SDK 调用不会阻塞事件循环。
    """
    user_text = (req.message or "").strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="message 不能为空")

    session_id = req.session_id or "default"
    lock = get_session_lock(session_id)
    history = get_session(session_id)

    def event_stream():
        # 同一会话串行处理，避免并发把 messages 写乱
        with lock:
            trim_history(history)  # 先裁剪，控制上下文长度
            history.append({"role": "user", "content": user_text})

            try:
                # 直接复用 Agent 内核：工具循环 + 流式生成都在里面
                for event in run_agent_events(history):
                    yield sse(event)
            except Exception as e:
                # 出错就把本轮 user 消息撤回，别污染记忆
                if history and history[-1].get("role") == "user":
                    history.pop()
                yield sse({
                    "type": "error",
                    "message": f"{type(e).__name__}: {e}",
                    "hint": "请确认 Ollama 已启动（ollama serve），且模型已拉取。",
                })

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


@app.post("/api/reset")
def reset(req: ResetRequest):
    """清空某个会话的记忆。"""
    session_id = req.session_id or "default"
    SESSIONS[session_id] = build_initial_messages()
    return {"ok": True, "session_id": session_id}


@app.get("/api/health")
def health():
    """自检：Ollama 是否可达、模型是否已拉取。"""
    info = {"ollama": OLLAMA_BASE_URL, "model": MODEL, "ready": False, "models": []}
    try:
        models = [m.id for m in client.models.list().data]
        info["models"] = models
        # Ollama 返回的 id 一般形如 "qwen3:8b"，做一次宽松匹配
        info["ready"] = any(MODEL in m or m in MODEL for m in models)
        if not info["ready"]:
            info["hint"] = f"未找到模型 {MODEL}，请先执行：ollama pull {MODEL}"
    except Exception as e:
        info["error"] = f"{type(e).__name__}: {e}"
        info["hint"] = "连不上 Ollama，请先执行：ollama serve"
    return JSONResponse(info)


# ==================== 启动入口 ====================
if __name__ == "__main__":
    import uvicorn

    print("=" * 56)
    print(f"  贴身女仆 铃兰 已启动")
    print(f"  模型    : {MODEL}")
    print(f"  Ollama  : {OLLAMA_BASE_URL}")
    print(f"  访问地址: http://127.0.0.1:8000")
    print("=" * 56)

    uvicorn.run(app, host="127.0.0.1", port=8000)
