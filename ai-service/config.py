# -*- coding: utf-8 -*-
"""全局配置

支持三种 LLM 后端：
  1. ollama  —— 局域网内另一台机器上的 Ollama（默认，如 qwen3:8b）
  2. internai —— 书生·端砚科研平台（OpenAI 兼容，如 deepseek-v4.1-flash-1017）
  3. openai  —— 其他 OpenAI 兼容接口（智谱 / DeepSeek / 通义 等）

配置优先级：系统环境变量 > ai-service/.env
切换提供方：编辑 ai-service/.env 里的 LLM_PROVIDER，然后重启 AI 服务。
"""
import os
from pathlib import Path


def _load_dotenv(path: Path):
    """极简 .env 解析：不覆盖已存在的环境变量（环境变量优先级更高）"""
    try:
        if not path.exists():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k:
                os.environ.setdefault(k, v)
    except Exception:
        pass


_load_dotenv(Path(__file__).parent / ".env")

# ---- 提供方：ollama / internai / openai ----
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

# ---- OpenAI 兼容接口（通用）----
LLM_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# ---- 书生·端砚科研平台（OpenAI 兼容）----
INTERNAI_BASE_URL = os.getenv(
    "INTERNAI_BASE_URL", "https://discovery-api.intern-ai.org.cn/v1"
).rstrip("/")
INTERNAI_API_KEY = os.getenv("INTERNAI_API_KEY", "")
INTERNAI_MODEL = os.getenv("INTERNAI_MODEL", "deepseek-v4.1-flash-1017")

# ---- Ollama（局域网）----
# 例如 http://192.168.1.100:11434 ；Ollama 默认端口 11434
OLLAMA_HOST = os.getenv("OLLAMA_HOST", ""
"").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")

# 视觉模型（图片识别需要）。qwen3:8b 是纯文本模型，不支持图片；
# 若要用拍照识别，请在 Ollama 机器上再拉取一个视觉模型（如 qwen2.5vl:7b / llava）
# 并在此填写，留空则图片识别自动降级。
VISION_MODEL = os.getenv("VISION_MODEL", "")

# 超时（秒）：局域网 + 8B 模型推理较慢，默认给足 180 秒
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "180"))


def active() -> dict:
    """返回当前生效的 LLM 连接参数"""
    if LLM_PROVIDER == "ollama":
        return {
            "provider": "ollama",
            "base_url": OLLAMA_HOST + "/v1",
            "model": OLLAMA_MODEL,
            # Ollama 不校验 key，但 OpenAI SDK 要求非空
            "api_key": "ollama",
            "vision_model": VISION_MODEL,
        }
    if LLM_PROVIDER == "internai":
        return {
            "provider": "internai",
            "base_url": INTERNAI_BASE_URL,
            "model": INTERNAI_MODEL,
            "api_key": INTERNAI_API_KEY,
            # 书生平台未配置视觉模型前留空，识图自动降级
            "vision_model": VISION_MODEL,
        }
    return {
        "provider": "openai",
        "base_url": LLM_BASE_URL,
        "model": LLM_MODEL,
        "api_key": LLM_API_KEY,
        "vision_model": VISION_MODEL,
    }


# Ollama 不需要 API Key，只要选定了提供方就认为启用；
# openai / internai 需要 API Key（interai 未填 key 时保持本地引擎，不报错）。
# 真正不可达时由调用方捕获异常并降级到本地规则引擎。
LLM_ENABLED = (
    True
    if LLM_PROVIDER == "ollama"
    else bool(INTERNAI_API_KEY if LLM_PROVIDER == "internai" else LLM_API_KEY)
)
