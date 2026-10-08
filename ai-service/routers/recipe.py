# -*- coding: utf-8 -*-
"""菜谱生成：POST /ai/recipe"""
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from services import llm

router = APIRouter()


class RecipeReq(BaseModel):
    goal: str = "维持"
    budget: float = 50
    ingredients: str = ""
    avoid: str = ""


class Meal(BaseModel):
    name: str
    ingredients: List[str]
    calories: int


class RecipeResp(BaseModel):
    breakfast: Meal
    lunch: Meal
    dinner: Meal
    shoppingList: List[str]


@router.post("/ai/recipe", response_model=RecipeResp)
def recipe(req: RecipeReq):
    try:
        raw = llm.chat(
            f"为用户生成一日三餐菜谱。目标：{req.goal}；每日预算：{int(req.budget)} 元；"
            f"现有食材：{req.ingredients or '无'}；忌口：{req.avoid or '无'}。\n"
            "返回 JSON：{\"breakfast\":{\"name\":\"\",\"ingredients\":[],\"calories\":0},"
            "\"lunch\":{...},\"dinner\":{...},\"shoppingList\":[]}。只返回 JSON。",
            json_mode=True,
        )
        return llm.parse_json(raw)
    except Exception:
        return _local_recipe(req)


def _local_recipe(req: RecipeReq) -> dict:
    """本地模板菜谱（LLM 未配置时）"""
    goal = req.goal

    menus = {
        "减脂": {
            "breakfast": ("燕麦牛奶杯 + 水煮蛋", ["燕麦片", "牛奶", "鸡蛋", "蓝莓"], 320),
            "lunch": ("香煎鸡胸肉蔬菜沙拉", ["鸡胸肉", "生菜", "番茄", "黄瓜", "橄榄油"], 420),
            "dinner": ("清蒸鱼 + 西兰花 + 杂粮饭", ["鲈鱼", "西兰花", "糙米"], 380),
        },
        "增肌": {
            "breakfast": ("全麦三明治 + 牛奶 + 鸡蛋x2", ["全麦面包", "鸡蛋", "牛奶", "生菜", "鸡胸肉"], 520),
            "lunch": ("牛肉炒饭 + 豆腐汤", ["牛肉", "米饭", "豆腐", "青菜"], 680),
            "dinner": ("三文鱼 + 意面 + 沙拉", ["三文鱼", "意大利面", "生菜", "橄榄油"], 620),
        },
        "控糖": {
            "breakfast": ("杂粮粥 + 鸡蛋 + 凉拌黄瓜", ["燕麦", "糙米", "鸡蛋", "黄瓜"], 300),
            "lunch": ("清炒虾仁 + 荞麦面 + 时蔬", ["虾仁", "荞麦面", "西兰花", "胡萝卜"], 450),
            "dinner": ("豆腐蔬菜煲 + 玉米", ["豆腐", "白菜", "香菇", "玉米"], 350),
        },
    }
    menu = menus.get(goal, {
        "breakfast": ("牛奶燕麦 + 鸡蛋 + 苹果", ["燕麦片", "牛奶", "鸡蛋", "苹果"], 380),
        "lunch": ("番茄牛肉面 + 烫青菜", ["面条", "牛肉", "番茄", "青菜"], 560),
        "dinner": ("鸡肉炒饭 + 紫菜蛋花汤", ["米饭", "鸡肉", "鸡蛋", "紫菜", "胡萝卜"], 520),
    })

    # 利用现有食材提示
    have = [i.strip() for i in (req.ingredients or "").replace("，", ",").split(",") if i.strip()]
    shopping = []
    for _, (_, ingredients, _) in menu.items():
        for ing in ingredients:
            if ing not in have and ing not in shopping:
                shopping.append(ing)

    def to_meal(t):
        return {"name": t[0], "ingredients": t[1], "calories": t[2]}

    return {
        "breakfast": to_meal(menu["breakfast"]),
        "lunch": to_meal(menu["lunch"]),
        "dinner": to_meal(menu["dinner"]),
        "shoppingList": shopping,
    }
