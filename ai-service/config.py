# -*- coding: utf-8 -*-
"""全局配置"""
import os

# LLM 配置（OpenAI 兼容接口：智谱/DeepSeek/通义等均可）
LLM_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# 是否启用真实 LLM
LLM_ENABLED = bool(LLM_API_KEY)
