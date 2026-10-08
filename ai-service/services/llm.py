# -*- coding: utf-8 -*-
"""LLM 客户端：统一调用入口；未配置 Key 时抛出供调用方降级"""
import json
import re

from openai import OpenAI

import config


def chat(prompt: str, system: str = "你是一名专业营养师。", json_mode: bool = False) -> str:
    """调用 LLM，返回文本。失败抛异常，由调用方降级到本地模式。"""
    if not config.LLM_ENABLED:
        raise RuntimeError("LLM 未配置")

    client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
    resp = client.chat.completions.create(
        model=config.LLM_MODEL,
        temperature=0.3,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content or ""


def parse_json(text: str) -> dict:
    """从 LLM 回复中提取 JSON（容忍 ```json 代码块包裹）"""
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(text)
