# -*- coding: utf-8 -*-
"""菜谱生成：POST /ai/recipe"""
import random
import re
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from services import llm, safety

router = APIRouter()


# ---------------------------------------------------------------------------
# 本地菜品库（LLM 未配置时随机组合使用）
# 字段：name 菜名、ingredients 食材、calories 热量、cost 估算成本(元)、tags 适用目标
# 热量参考《中国居民膳食指南（2022）》三餐分配：早 3 : 午 4 : 晚 3
# ---------------------------------------------------------------------------
BREAKFAST = [
    {"name": "燕麦牛奶杯 + 水煮蛋", "ingredients": ["燕麦片", "牛奶", "鸡蛋", "蓝莓"], "calories": 320, "cost": 8, "tags": ["减脂", "控糖", "维持"]},
    {"name": "全麦三明治 + 牛奶 + 鸡蛋x2", "ingredients": ["全麦面包", "鸡蛋", "牛奶", "生菜", "鸡胸肉"], "calories": 520, "cost": 12, "tags": ["增肌", "维持"]},
    {"name": "杂粮粥 + 鸡蛋 + 凉拌黄瓜", "ingredients": ["燕麦", "糙米", "鸡蛋", "黄瓜"], "calories": 300, "cost": 6, "tags": ["控糖", "减脂"]},
    {"name": "牛奶燕麦 + 鸡蛋 + 苹果", "ingredients": ["燕麦片", "牛奶", "鸡蛋", "苹果"], "calories": 380, "cost": 9, "tags": ["维持", "减脂"]},
    {"name": "鸡蛋蔬菜卷饼", "ingredients": ["全麦饼", "鸡蛋", "生菜", "胡萝卜"], "calories": 350, "cost": 7, "tags": ["减脂", "维持"]},
    {"name": "无糖豆浆 + 全麦馒头 + 水煮蛋", "ingredients": ["黄豆", "全麦面粉", "鸡蛋"], "calories": 400, "cost": 6, "tags": ["维持", "增肌", "控糖"]},
    {"name": "希腊酸奶 + 坚果 + 蓝莓", "ingredients": ["无糖酸奶", "混合坚果", "蓝莓"], "calories": 330, "cost": 15, "tags": ["减脂", "控糖"]},
    {"name": "牛肉粥 + 凉拌小菜", "ingredients": ["牛肉", "大米", "青菜"], "calories": 420, "cost": 14, "tags": ["增肌", "维持"]},
    {"name": "蒸红薯 + 鸡蛋 + 牛奶", "ingredients": ["红薯", "鸡蛋", "牛奶"], "calories": 380, "cost": 7, "tags": ["减脂", "增肌", "维持"]},
    {"name": "荞麦面 + 煎蛋 + 青菜", "ingredients": ["荞麦面", "鸡蛋", "青菜"], "calories": 400, "cost": 8, "tags": ["控糖", "减脂"]},
    {"name": "香蕉蛋白奶昔 + 全麦面包", "ingredients": ["香蕉", "牛奶", "蛋白粉", "全麦面包"], "calories": 480, "cost": 16, "tags": ["增肌"]},
    {"name": "蒸南瓜 + 无糖豆浆 + 鸡蛋", "ingredients": ["南瓜", "黄豆", "鸡蛋"], "calories": 300, "cost": 5, "tags": ["控糖", "减脂"]},
    # 以下为不含蛋奶的选项，保证忌口蛋奶时仍有选择余地
    {"name": "蔬菜瘦肉粥 + 全麦馒头", "ingredients": ["瘦肉", "青菜", "大米", "全麦面粉"], "calories": 380, "cost": 8, "tags": ["维持", "减脂", "增肌"]},
    {"name": "小米粥 + 凉拌豆腐丝 + 蒸紫薯", "ingredients": ["小米", "豆腐丝", "紫薯"], "calories": 340, "cost": 7, "tags": ["控糖", "减脂", "维持"]},
    {"name": "虾仁蔬菜面", "ingredients": ["虾仁", "面条", "青菜", "胡萝卜"], "calories": 400, "cost": 13, "tags": ["增肌", "维持", "控糖"]},
    {"name": "金枪鱼杂粮饭团 + 无糖豆浆", "ingredients": ["金枪鱼", "糙米", "黄豆"], "calories": 420, "cost": 12, "tags": ["增肌", "减脂"]},
]

LUNCH = [
    {"name": "香煎鸡胸肉蔬菜沙拉", "ingredients": ["鸡胸肉", "生菜", "番茄", "黄瓜", "橄榄油"], "calories": 420, "cost": 15, "tags": ["减脂"]},
    {"name": "牛肉炒饭 + 豆腐汤", "ingredients": ["牛肉", "米饭", "豆腐", "青菜"], "calories": 680, "cost": 20, "tags": ["增肌"]},
    {"name": "清炒虾仁 + 荞麦面 + 时蔬", "ingredients": ["虾仁", "荞麦面", "西兰花", "胡萝卜"], "calories": 450, "cost": 22, "tags": ["控糖", "减脂"]},
    {"name": "番茄牛肉面 + 烫青菜", "ingredients": ["面条", "牛肉", "番茄", "青菜"], "calories": 560, "cost": 18, "tags": ["维持", "增肌"]},
    {"name": "杂粮饭 + 清蒸鲈鱼 + 炒时蔬", "ingredients": ["糙米", "鲈鱼", "西兰花", "胡萝卜"], "calories": 500, "cost": 25, "tags": ["减脂", "控糖", "维持"]},
    {"name": "鸡腿饭 + 蒜蓉西兰花", "ingredients": ["鸡腿", "米饭", "西兰花"], "calories": 620, "cost": 17, "tags": ["增肌", "维持"]},
    {"name": "三文鱼藜麦碗", "ingredients": ["三文鱼", "藜麦", "生菜", "番茄"], "calories": 550, "cost": 35, "tags": ["增肌", "控糖"]},
    {"name": "豆腐蔬菜煲 + 糙米饭", "ingredients": ["北豆腐", "白菜", "香菇", "糙米"], "calories": 420, "cost": 10, "tags": ["控糖", "减脂"]},
    {"name": "瘦肉炒河粉 + 青菜", "ingredients": ["猪里脊", "河粉", "青菜"], "calories": 580, "cost": 15, "tags": ["维持"]},
    {"name": "鸡胸肉意面 + 生菜沙拉", "ingredients": ["鸡胸肉", "意大利面", "生菜", "橄榄油"], "calories": 520, "cost": 16, "tags": ["增肌", "减脂"]},
    {"name": "咖喱鸡饭 + 清炒时蔬", "ingredients": ["鸡腿肉", "米饭", "土豆", "胡萝卜"], "calories": 600, "cost": 18, "tags": ["维持", "增肌"]},
    {"name": "虾仁蒸蛋 + 杂粮饭 + 西兰花", "ingredients": ["虾仁", "鸡蛋", "糙米", "西兰花"], "calories": 450, "cost": 19, "tags": ["减脂", "控糖"]},
]

DINNER = [
    {"name": "清蒸鱼 + 西兰花 + 杂粮饭", "ingredients": ["鲈鱼", "西兰花", "糙米"], "calories": 380, "cost": 22, "tags": ["减脂"]},
    {"name": "三文鱼 + 意面 + 沙拉", "ingredients": ["三文鱼", "意大利面", "生菜", "橄榄油"], "calories": 620, "cost": 35, "tags": ["增肌"]},
    {"name": "豆腐蔬菜煲 + 玉米", "ingredients": ["豆腐", "白菜", "香菇", "玉米"], "calories": 350, "cost": 9, "tags": ["控糖", "减脂"]},
    {"name": "鸡肉炒饭 + 紫菜蛋花汤", "ingredients": ["米饭", "鸡肉", "鸡蛋", "紫菜", "胡萝卜"], "calories": 520, "cost": 14, "tags": ["维持"]},
    {"name": "白灼虾 + 蒜蓉西兰花 + 小米粥", "ingredients": ["虾", "西兰花", "小米"], "calories": 400, "cost": 26, "tags": ["减脂", "控糖"]},
    {"name": "香菇滑鸡 + 糙米饭 + 青菜", "ingredients": ["鸡腿肉", "香菇", "糙米", "青菜"], "calories": 480, "cost": 16, "tags": ["维持", "减脂"]},
    {"name": "牛肉炖萝卜 + 杂粮饭", "ingredients": ["牛肉", "白萝卜", "糙米"], "calories": 520, "cost": 24, "tags": ["增肌", "维持"]},
    {"name": "番茄豆腐汤 + 蒸红薯 + 青菜", "ingredients": ["番茄", "豆腐", "红薯", "青菜"], "calories": 350, "cost": 8, "tags": ["控糖", "减脂"]},
    {"name": "煎鳕鱼 + 藜麦 + 芦笋", "ingredients": ["鳕鱼", "藜麦", "芦笋"], "calories": 450, "cost": 30, "tags": ["减脂", "增肌"]},
    {"name": "鸡蛋羹 + 炒时蔬 + 小米粥", "ingredients": ["鸡蛋", "青菜", "小米"], "calories": 330, "cost": 6, "tags": ["控糖", "维持"]},
    {"name": "鸡肉蔬菜卷 + 蒸紫薯", "ingredients": ["鸡胸肉", "生菜", "紫薯"], "calories": 420, "cost": 13, "tags": ["减脂", "维持"]},
    {"name": "猪里脊炒杂蔬 + 米饭", "ingredients": ["猪里脊", "青椒", "胡萝卜", "米饭"], "calories": 560, "cost": 16, "tags": ["增肌", "维持"]},
]


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
    """
    本地菜谱引擎（LLM 未配置时）。

    与固定模板不同，这里从菜品库随机组合：
      1. 按目标筛选（减脂/增肌/控糖/维持 分别有不同的适用菜品）
      2. 排除忌口食材
      3. 按预算筛选（每人每餐预算 = 总预算 / 3）
      4. 优先复用用户现有食材（70% 概率）
      5. 三餐不重复
    """
    goal = req.goal or "维持"
    raw_avoid = [t for t in re.split(r"[、,，\s]+", req.avoid or "") if t]
    # 忌口同义词扩展：「牛奶」应同时排除酸奶/奶酪/奶油等乳制品（复用安全模块的映射）
    avoid_tokens = []
    for t in raw_avoid:
        avoid_tokens.append(t)
        avoid_tokens += safety.ALLERGY_HINTS.get(t, [])
    avoid_tokens = [t for t in avoid_tokens if t]
    have = [i for i in re.split(r"[、,，\s]+", req.ingredients or "") if i]
    per_meal_budget = float(req.budget or 0) / 3 if req.budget else 0

    used = set()

    def pick(pool: list) -> dict:
        # 排除忌口
        cands = [d for d in pool
                 if not any(tok in (d["name"] + " ".join(d["ingredients"])) for tok in avoid_tokens)]
        if not cands:
            cands = pool

        # 按目标筛选；若因忌口过滤后符合目标的只剩 1 道，则放宽到全部安全候选，
        # 避免「每次都是同一道菜」
        matched = [d for d in cands if goal in d.get("tags", [])]
        if len(matched) >= 2:
            cands = matched
        elif matched:
            cands = matched + [d for d in cands if d not in matched]

        # 按预算筛选（留 1.5 倍弹性）
        if per_meal_budget > 0:
            affordable = [d for d in cands if d["cost"] <= per_meal_budget * 1.5]
            if affordable:
                cands = affordable

        # 优先复用现有食材；但仅在有多道可选时才启用，
        # 否则会导致每次都推荐同一道菜
        if have:
            preferred = [d for d in cands
                         if any(h in " ".join(d["ingredients"]) for h in have)]
            if len(preferred) >= 2 and random.random() < 0.6:
                cands = preferred

        # 三餐不重复
        fresh = [d for d in cands if d["name"] not in used] or cands
        return random.choice(fresh)

    breakfast, lunch, dinner = pick(BREAKFAST), pick(LUNCH), pick(DINNER)
    for d in (breakfast, lunch, dinner):
        used.add(d["name"])

    # 购物清单：三餐食材 - 现有食材（去重保序）
    shopping = []
    for dish in (breakfast, lunch, dinner):
        for ing in dish["ingredients"]:
            if ing in have or ing in shopping:
                continue
            shopping.append(ing)

    def to_meal(d: dict) -> dict:
        return {"name": d["name"], "ingredients": list(d["ingredients"]),
                "calories": d["calories"]}

    return {
        "breakfast": to_meal(breakfast),
        "lunch": to_meal(lunch),
        "dinner": to_meal(dinner),
        "shoppingList": shopping,
    }
