# -*- coding: utf-8 -*-
"""RAG 检索 + 建议生成：POST /ai/rag、POST /ai/advice"""
from typing import Optional, List

from fastapi import APIRouter
from pydantic import BaseModel

from services import knowledge, llm, safety

router = APIRouter()


class RagReq(BaseModel):
    query: str


class Chunk(BaseModel):
    content: str
    source: str


class RagResp(BaseModel):
    chunks: List[Chunk]


class Profile(BaseModel):
    goal: str = "维持"
    bmr: int = 1500
    targetCalories: int = 2000
    avoid: str = ""
    allergy: str = ""


class Intake(BaseModel):
    calories: float = 0
    protein: float = 0
    fat: float = 0
    carbs: float = 0


class AdviceReq(BaseModel):
    profile: Profile
    todayIntake: Intake
    gap: Intake


class AdviceResp(BaseModel):
    advice: str
    basedOn: List[str]
    safe: bool


@router.post("/ai/rag", response_model=RagResp)
def rag(req: RagReq):
    return {"chunks": knowledge.search(req.query)}


@router.post("/ai/advice", response_model=AdviceResp)
def advice(req: AdviceReq):
    p = req.profile
    intake = req.todayIntake

    # RAG 检索
    query = f"{p.goal} 摄入 {int(intake.calories)} kcal 蛋白质 {intake.protein}g 碳水 {intake.carbs}g"
    chunks = knowledge.search(query)
    based_on = [c["content"] for c in chunks]

    # 尝试 LLM 生成
    advice_text = None
    try:
        guide_text = "\n".join(f"- {c['content']}（{c['source']}）" for c in chunks)
        advice_text = llm.chat(
            f"用户画像：目标={p.goal}，BMR={p.bmr} kcal，目标摄入={p.targetCalories} kcal，"
            f"忌口={p.avoid or '无'}，过敏原={p.allergy or '无'}。\n"
            f"今日已摄入：热量 {intake.calories} kcal、蛋白质 {intake.protein}g、"
            f"脂肪 {intake.fat}g、碳水 {intake.carbs}g。\n"
            f"膳食指南依据：\n{guide_text}\n\n"
            "请给出 3 条具体、可执行的下一餐建议，不涉及过敏原和忌口，"
            "不要建议低于基础代谢的热量摄入。用中文简洁输出。"
        )
    except Exception:
        advice_text = _local_advice(p, intake, req.gap)

    # 安全拦截（need.md 3.6.3）
    check = safety.check(advice_text, allergy=p.allergy or "", bmr=p.bmr)

    return {
        "advice": advice_text,
        "basedOn": [f"{c['content']}（{c['source']}）" for c in chunks],
        "safe": check["safe"],
    }


def _local_advice(p: Profile, intake: Intake, gap: Intake) -> str:
    """LLM 未配置时的本地模板建议"""
    lines = []
    g = gap or Intake()

    if g.calories and g.calories > 0:
        lines.append(f"今日还可摄入约 {int(g.calories)} kcal。建议下一餐选择优质蛋白（鱼禽蛋豆）+ 大量蔬菜 + 适量全谷物主食。")
    elif g.calories and g.calories < 0:
        lines.append(f"今日已超出目标约 {int(-g.calories)} kcal。下一餐建议以蔬菜和高纤维食物为主，减少精制碳水。")

    if g.protein and g.protein > 0:
        lines.append(f"蛋白质还差 {int(g.protein)}g，推荐：水煮蛋、鸡胸肉、豆腐或一杯牛奶。")

    if p.goal == "减脂":
        lines.append("减脂期建议保持热量缺口不超过 500 kcal，避免极端节食；每周进行 150 分钟以上中等强度运动。")
    elif p.goal == "增肌":
        lines.append("增肌期保证每公斤体重 1.5g 以上蛋白质摄入，训练后及时补充碳水+蛋白。")
    elif p.goal == "控糖":
        lines.append("控糖期建议选择低 GI 主食（燕麦、糙米），避免含糖饮料与精制糖，每天添加糖控制在 25g 以内。")
    else:
        lines.append("维持期保持三餐规律，每天 12 种以上食物，蔬菜不少于 300g。")

    if p.avoid:
        lines.append(f"注意避免忌口食物：{p.avoid}。")

    lines.append("每天饮水 1500~1700ml，规律作息有助于体重管理。")
    return "\n".join(lines)
