# -*- coding: utf-8 -*-
"""LLM 客户端：统一调用入口（Ollama / 书生·端砚 / 其他 OpenAI 兼容接口）

三种提供方都走 OpenAI SDK（Ollama 与书生均提供 OpenAI 兼容端点），
区别只在 config.active() 返回的连接参数。
调用失败会抛异常，由各 router 降级到本地规则引擎。
"""
import json
import re

from openai import OpenAI

import config


def _client() -> OpenAI:
    cfg = config.active()
    return OpenAI(
        api_key=cfg["api_key"],
        base_url=cfg["base_url"],
        timeout=config.LLM_TIMEOUT,
    )


def clean(text: str) -> str:
    """
    清洗模型输出：
      - 去掉 qwen3 等推理模型的 <think>...</think> 推理过程
      - 去掉 ```json 代码块包裹
    否则后续 json.loads 会失败。
    """
    t = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S)
    t = re.sub(r"<\|.*?\|>", "", t, flags=re.S)  # 部分模型的特殊 token
    t = re.sub(r"^```(?:json)?|```$", "", t.strip(), flags=re.MULTILINE).strip()
    return t


def _extra_body(cfg: dict) -> dict:
    """
    提供方专属的额外请求参数。
    书生 deepseek-v4.1 是推理模型，默认每次回答都先「思考」（reasoning_content），
    一句你好都要 15s；实测通过 vLLM 风格参数可关闭推理，耗时降一半以上。
    """
    if cfg["provider"] == "internai":
        return {"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}}
    return {}


def chat(prompt: str, system: str = "你是一名专业营养师。",
         json_mode: bool = False, model: str = None) -> str:
    """调用 LLM，返回清洗后的文本。失败抛异常，由调用方降级到本地模式。"""
    if not config.LLM_ENABLED:
        raise RuntimeError("LLM 未配置")

    cfg = config.active()
    sys_msg = system
    user_msg = prompt
    if json_mode:
        sys_msg = (system + " 必须只输出合法 JSON 对象，不要输出任何解释文字、"
                           "推理过程或代码块标记。")
    resp = _client().chat.completions.create(
        model=model or cfg["model"],
        temperature=0.3,
        messages=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_msg},
        ],
        **_extra_body(cfg),
    )
    return clean(resp.choices[0].message.content or "")


def chat_image(prompt: str, image_b64: str, model: str = None) -> str:
    """
    多模态识图。需要支持视觉的模型（qwen2.5vl / llava / gpt-4o 等）。
    qwen3:8b 是纯文本模型，调用会失败，由调用方降级。
    """
    if not config.LLM_ENABLED:
        raise RuntimeError("LLM 未配置")

    cfg = config.active()
    model_name = model or cfg["vision_model"] or cfg["model"]
    resp = _client().chat.completions.create(
        model=model_name,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            ],
        }],
        **_extra_body(cfg),
    )
    return clean(resp.choices[0].message.content or "")


def parse_json(text: str) -> dict:
    """从 LLM 回复中提取 JSON（容忍 ```json 代码块包裹与推理标签）"""
    cleaned = clean(text)
    try:
        return json.loads(cleaned)
    except Exception:
        # 退化：截取第一个 { 到最后一个 } 之间
        s, e = cleaned.find("{"), cleaned.rfind("}")
        if s >= 0 and e > s:
            return json.loads(cleaned[s:e + 1])
        raise
