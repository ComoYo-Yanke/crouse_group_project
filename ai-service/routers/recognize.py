# -*- coding: utf-8 -*-
"""食物识别：POST /ai/recognize"""
import base64

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from services import food_db, llm

router = APIRouter()


class RecognizeReq(BaseModel):
    imageBase64: Optional[str] = None
    textDescription: Optional[str] = None


class FoodItem(BaseModel):
    name: str
    portion: str
    calories: float
    protein: float
    fat: float
    carbs: float
    fiber: float
    sodium: float
    confidence: float


class RecognizeResp(BaseModel):
    foods: List[FoodItem]


@router.post("/ai/recognize", response_model=RecognizeResp)
def recognize(req: RecognizeReq):
    # 文字描述
    if req.textDescription:
        return {"foods": _recognize_text(req.textDescription)}
    # 图片：需要 LLM 多模态能力；未配置时返回占位结果并提示低置信度
    if req.imageBase64:
        return {"foods": _recognize_image(req.imageBase64, req.textDescription)}
    return {"foods": []}


def _recognize_text(text: str) -> list:
    # 优先 LLM
    try:
        raw = llm.chat(
            f"识别以下饮食描述中的食物并估算营养（每项含份量）：\"{text}\"。"
            "返回 JSON：{\"foods\":[{{\"name\":\"\",\"portion\":\"\",\"calories\":0,"
            "\"protein\":0,\"fat\":0,\"carbs\":0,\"fiber\":0,\"sodium\":0,\"confidence\":0.0}}]}，"
            "置信度 0-1。只返回 JSON。",
            json_mode=True,
        )
        data = llm.parse_json(raw)
        return data.get("foods", [])
    except Exception:
        # 降级：本地食物表
        return food_db.recognize_text(text)


def _recognize_image(image_b64: str, text_hint: str = None) -> list:
    """
    图片识别：需要支持视觉的模型（qwen2.5vl / llava / gpt-4o 等）。
    在 .env 里配置 VISION_MODEL 即可启用；
    qwen3:8b 是纯文本模型，调用会失败并自动降级。
    """
    try:
        prompt = ("识别图中所有食物，估算份量与营养。返回 JSON："
                  '{"foods":[{"name":"","portion":"","calories":0,"protein":0,'
                  '"fat":0,"carbs":0,"fiber":0,"sodium":0,"confidence":0.0}]} 只返回 JSON。')
        if text_hint:
            prompt += f" 用户补充说明：{text_hint}"
        raw = llm.chat_image(prompt, image_b64)
        foods = llm.parse_json(raw).get("foods", [])
        if foods:
            return foods
        raise RuntimeError("模型未返回食物列表")
    except Exception:
        # 降级：无法识图，返回提示性结果（低置信度，提醒用户手动核对）
        return [{
            "name": text_hint or "图片食物（当前未配置视觉模型，请手动填写）",
            "portion": "1 份",
            "calories": 500, "protein": 18.0, "fat": 15.0,
            "carbs": 70.0, "fiber": 3.0, "sodium": 600,
            "confidence": 0.2,
        }]
