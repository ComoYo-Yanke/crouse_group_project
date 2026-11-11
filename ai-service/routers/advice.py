# -*- coding: utf-8 -*-
"""RAG 检索 + 建议生成：POST /ai/rag、POST /ai/advice"""
import random
import re
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter
from pydantic import BaseModel

from services import knowledge, llm, safety

router = APIRouter()


# ---------------------------------------------------------------------------
# 本地食物库：按《中国居民膳食指南（2022）》四类食物组织
# 每项：{name 名称, portion 份量, kcal 热量, protein 蛋白质(g), note 要点}
# ---------------------------------------------------------------------------
FOOD_LIBRARY = {
    "主食（谷薯类）": [
        {"name": "杂粮饭", "portion": "1 碗（约150g）", "kcal": 180, "protein": 4, "note": "含全谷物"},
        {"name": "糙米饭", "portion": "1 碗（约150g）", "kcal": 170, "protein": 4, "note": "低 GI"},
        {"name": "燕麦粥", "portion": "1 碗（约250g）", "kcal": 150, "protein": 6, "note": "富含β-葡聚糖"},
        {"name": "全麦面包", "portion": "2 片（约70g）", "kcal": 170, "protein": 6, "note": "全谷物"},
        {"name": "蒸红薯", "portion": "1 个（约150g）", "kcal": 130, "protein": 2, "note": "薯类"},
        {"name": "水煮玉米", "portion": "1 根（约200g）", "kcal": 200, "protein": 5, "note": "薯类"},
        {"name": "荞麦面", "portion": "1 碗（约200g）", "kcal": 220, "protein": 8, "note": "低 GI"},
        {"name": "山药", "portion": "150g", "kcal": 85, "protein": 2, "note": "薯类"},
        {"name": "藜麦饭", "portion": "1 碗（约150g）", "kcal": 180, "protein": 6, "note": "完全蛋白谷物"},
    ],
    "优质蛋白（鱼禽蛋豆）": [
        {"name": "鸡胸肉", "portion": "100g", "kcal": 165, "protein": 31, "note": "低脂高蛋白"},
        {"name": "三文鱼", "portion": "100g", "kcal": 200, "protein": 20, "note": "富含 Omega-3"},
        {"name": "虾仁", "portion": "100g", "kcal": 100, "protein": 24, "note": "低脂"},
        {"name": "鸡蛋", "portion": "2 个（约100g）", "kcal": 140, "protein": 13, "note": "不弃蛋黄"},
        {"name": "北豆腐", "portion": "150g", "kcal": 180, "protein": 18, "note": "大豆制品"},
        {"name": "瘦牛肉", "portion": "100g", "kcal": 180, "protein": 26, "note": "富含铁"},
        {"name": "无糖酸奶", "portion": "150g", "kcal": 90, "protein": 9, "note": "奶制品"},
        {"name": "牛奶", "portion": "250ml", "kcal": 135, "protein": 8, "note": "奶制品"},
        {"name": "去皮鸡腿肉", "portion": "120g", "kcal": 190, "protein": 25, "note": "口感更好"},
        {"name": "鳕鱼", "portion": "120g", "kcal": 100, "protein": 21, "note": "低脂低汞"},
        {"name": "毛豆", "portion": "100g", "kcal": 130, "protein": 13, "note": "植物蛋白"},
    ],
    "蔬菜（深色优先）": [
        {"name": "西兰花", "portion": "150g", "kcal": 50, "protein": 4, "note": "深色蔬菜"},
        {"name": "菠菜", "portion": "200g", "kcal": 50, "protein": 6, "note": "深色蔬菜"},
        {"name": "紫甘蓝", "portion": "100g", "kcal": 30, "protein": 1, "note": "深色蔬菜"},
        {"name": "胡萝卜", "portion": "100g", "kcal": 40, "protein": 1, "note": "富含胡萝卜素"},
        {"name": "番茄", "portion": "150g", "kcal": 30, "protein": 2, "note": "生熟皆可"},
        {"name": "黄瓜", "portion": "200g", "kcal": 30, "protein": 2, "note": "低热量"},
        {"name": "香菇", "portion": "100g", "kcal": 30, "protein": 3, "note": "菌菇类"},
        {"name": "芦笋", "portion": "150g", "kcal": 30, "protein": 3, "note": "高纤维"},
        {"name": "生菜", "portion": "150g", "kcal": 20, "protein": 2, "note": "低热量"},
        {"name": "青椒", "portion": "100g", "kcal": 25, "protein": 1, "note": "富含维C"},
    ],
    "水果": [
        {"name": "苹果", "portion": "1 个（约200g）", "kcal": 105, "protein": 1, "note": "带皮吃"},
        {"name": "蓝莓", "portion": "100g", "kcal": 60, "protein": 1, "note": "低 GI"},
        {"name": "橙子", "portion": "1 个（约200g）", "kcal": 95, "protein": 2, "note": "富含维C"},
        {"name": "香蕉", "portion": "1 根（约120g）", "kcal": 110, "protein": 1, "note": "运动前后适宜"},
        {"name": "猕猴桃", "portion": "1 个（约100g）", "kcal": 60, "protein": 1, "note": "维C之王"},
        {"name": "草莓", "portion": "150g", "kcal": 50, "protein": 1, "note": "低糖水果"},
        {"name": "柚子", "portion": "2 瓣（约150g）", "kcal": 60, "protein": 1, "note": "低 GI"},
        {"name": "梨", "portion": "1 个（约200g）", "kcal": 100, "protein": 1, "note": "润燥"},
    ],
}

GOAL_TIPS = {
    "减脂": [
        "减脂期建议每日热量缺口控制在 300~500 kcal，不低于基础代谢，避免极端节食。",
        "优先选择高饱腹感食物（蔬菜、豆制品、粗粮），减少精制碳水与油炸食品。",
        "每周进行 150 分钟以上中等强度有氧运动，配合 2 次力量训练以保留肌肉。",
        "细嚼慢咽、先吃蔬菜再吃主食，有助于提升饱腹感、减少总摄入。",
        "警惕「隐形热量」：含糖饮料、酱料、坚果零食，少量就可能抵消热量缺口。",
        "体重下降速度以每周 0.5~1kg 为宜，过快多为水分和肌肉流失。",
    ],
    "增肌": [
        "增肌期建议每公斤体重摄入 1.5~2.0g 蛋白质，并保证总热量盈余 200~300 kcal。",
        "训练后 1 小时内补充「碳水+蛋白」（如香蕉+牛奶），有助于肌肉合成。",
        "蛋白质分摊到三餐，每餐 25~35g 吸收利用率更高。",
        "力量训练以复合动作为主（深蹲、硬拉、卧推），每周每肌群训练 2 次。",
        "碳水不是敌人：训练日可适当提高主食比例，为训练提供能量。",
        "保证每晚 7~9 小时睡眠，睡眠不足会显著影响肌肉合成与恢复。",
    ],
    "控糖": [
        "控糖期主食选择低 GI 谷物（燕麦、糙米、荞麦），避免精制米面。",
        "每天添加糖控制在 25g 以内，不喝含糖饮料，水果安排在两餐之间。",
        "进餐顺序建议：蔬菜 → 蛋白 → 主食，有助于平缓餐后血糖。",
        "餐后散步 10~15 分钟，可明显降低餐后血糖峰值。",
        "注意「无糖」标签陷阱：无蔗糖不等于无碳水，仍要看营养成分表。",
        "规律三餐、避免长时间空腹后暴食，有助于血糖稳定。",
    ],
    "维持": [
        "维持期保持三餐规律、定时定量，每天摄入 12 种以上食物、每周 25 种以上。",
        "蔬菜每天不少于 300g（深色占一半），水果 200~350g，奶制品相当于 300ml 液态奶。",
        "保持能量摄入与消耗平衡，避免暴饮暴食与过度节食。",
        "每周称重 1~2 次（固定时间、空腹），波动 1~2kg 属正常范围。",
        "多在家做饭、少点外卖，更容易控制油盐糖用量。",
    ],
}

GUIDELINE_TARGETS = [
    "谷薯类 200~300g/天（其中全谷物、杂豆 50~150g）",
    "蔬菜 ≥300g/天（深色蔬菜占一半）",
    "水果 200~350g/天",
    "鱼禽蛋瘦肉 120~200g/天",
    "奶制品 ≥300ml 液态奶/天",
    "大豆及坚果 25~35g/天",
    "食盐 <5g/天、烹调油 25~30g/天",
    "添加糖 <25g/天（最好 <50g）",
    "饮水 1500~1700ml/天",
    "每天 12 种以上食物，每周 25 种以上",
]

# ---------------------------------------------------------------------------
# 可选板块池：每次随机抽取若干，保证「结构」也不重复
# ---------------------------------------------------------------------------
COOKING_TIPS = [
    "优先蒸、煮、炖、凉拌，少用煎炸；炒菜用不粘锅可减少一半用油。",
    "肉类先焯水去浮沫再烹饪，可减少部分脂肪与嘌呤。",
    "蔬菜急火快炒或焯水后凉拌，能更好地保留维生素 C。",
    "用柠檬汁、醋、香辛料替代部分盐，既提味又能减少钠摄入。",
    "主食放凉后再加热可增加抗性淀粉，升糖指数更低。",
    "肉类提前用葱姜蒜、料酒腌制，可减少烹饪时的用盐量。",
]

SNACK_TIPS = [
    "上午或下午加餐可选：无糖酸奶 150g + 一小把原味坚果（约 10g）。",
    "加餐优先选低热量高纤维：小番茄、黄瓜条、无糖豆浆。",
    "两餐之间饥饿感明显时，先喝一杯水，等待 10 分钟再判断是否真饿。",
    "避免用饼干、蛋糕当加餐，可用水果 + 奶制品替代。",
    "运动后 30 分钟内可加餐一次（蛋白 + 碳水），帮助恢复。",
]

HYDRATION_TIPS = [
    "每天饮水 1500~1700ml（约 7~8 杯），少量多次，不要等到口渴才喝。",
    "晨起先喝一杯温水，有助于唤醒代谢、补充夜间流失的水分。",
    "餐前 30 分钟喝一杯水，可增强饱腹感、帮助控制食量。",
    "用白开水或淡茶替代含糖饮料，一杯奶茶的糖分可能超过一天上限。",
]

EXERCISE_TIPS = [
    "每周至少 5 天中等强度运动，累计 150 分钟以上（如快走、骑车、游泳）。",
    "减少久坐：每坐 1 小时起身活动 3~5 分钟。",
    "有氧 + 力量结合效果最好：有氧减脂，力量训练保留肌肉。",
    "运动强度以「能说话但不能唱歌」为宜，即中等强度。",
    "运动后补充水分与适量蛋白质，避免立即大量进食高油高糖食物。",
]

MYTH_TIPS = [
    "误区：不吃晚饭能减肥。长期空腹易导致暴食与代谢下降，建议清淡少量而非不吃。",
    "误区：只吃水果减肥。水果含果糖，过量同样会转化为脂肪，且缺乏蛋白质。",
    "误区：零脂肪食品更健康。去脂常靠加糖改善口感，热量未必更低。",
    "误区：出汗越多减脂越多。出汗主要是水分流失，与脂肪消耗无直接关系。",
    "误区：局部减脂。脂肪消耗是全身性的，无法只减某个部位。",
]

SWAP_TIPS = [
    "替换方案：白米饭 → 杂粮饭/糙米饭，膳食纤维与 B 族维生素更高。",
    "替换方案：油炸鸡排 → 香煎/空气炸鸡胸肉，可减少约一半脂肪。",
    "替换方案：含糖饮料 → 无糖气泡水/淡茶，直接省下 100~150 kcal。",
    "替换方案：精制面包 → 全麦面包，饱腹感更强、升糖更慢。",
    "替换方案：沙拉酱 → 油醋汁/柠檬汁，热量可降低 60% 以上。",
    "替换方案：猪肉馅 → 鸡肉馅/豆腐，饱和脂肪更低。",
]

TAKEOUT_TIPS = [
    "外卖优先选「蒸/煮/炖」做法，避开「干锅、水煮、香酥、糖醋」等高油高糖菜式。",
    "点餐时主食减半、蔬菜加一份，汤和酱料单独放，可显著降低油盐摄入。",
    "麻辣烫/火锅优先清汤锅底，多选菌菇、豆制品与绿叶菜，少选丸滑与内脏。",
    "套餐类可要求「少油少盐、酱汁单放」，米饭可换成杂粮饭（部分商家支持）。",
    "避免边看屏幕边吃，容易在不知不觉中多吃 15%~20%。",
]

WEEKLY_TIPS = [
    "建议提前规划 3 天菜单，按「主食 + 蛋白 + 蔬菜」三格法备餐，减少临时点外卖。",
    "周末可一次备好杂粮饭、卤鸡胸、焯蔬菜，分装冷藏，工作日加热即食。",
    "本周可尝试新增 2 种没吃过的食材，帮助达成「每周 25 种以上食物」的目标。",
    "记录饮食 7 天，找出最容易超标的一餐（通常是晚餐或加餐），针对性调整。",
]

PROGRESS_TIPS = [
    "建议固定每周同一时间（晨起空腹、排便后）称重，单次波动不代表趋势。",
    "除体重外，同时记录腰围与体脂，更能反映减脂效果。",
    "平台期超过 2 周可调整：增加日常活动量或重新核算热量目标。",
    "用照片记录体型变化，比体重数字更能反映身体成分的改善。",
]


def _meal_slot() -> str:
    """根据当前时间判断下一餐"""
    h = datetime.now().hour
    if h < 10:
        return "早餐"
    if h < 15:
        return "午餐"
    if h < 21:
        return "晚餐"
    return "加餐"


def _filter_foods(foods: list, allergy: str, avoid: str) -> list:
    """排除与过敏原/忌口冲突的食物"""
    def conflict(name: str) -> bool:
        for kw in [avoid, allergy]:
            for token in [t.strip() for t in re.split(r"[、,，\s]+", kw or "") if t.strip()]:
                for hint in safety.ALLERGY_HINTS.get(token, [token]):
                    if hint and hint in name:
                        return True
        return False

    safe = [f for f in foods if not conflict(f["name"])]
    return safe or foods


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
    # 安全拦截原因：safe=False 时为具体原因，safe=True 时为空字符串
    reason: str = ""


@router.post("/ai/rag", response_model=RagResp)
def rag(req: RagReq):
    return {"chunks": knowledge.search(req.query)}


@router.post("/ai/advice", response_model=AdviceResp)
def advice(req: AdviceReq):
    p = req.profile
    intake = req.todayIntake

    # RAG 检索（带上餐次与缺口，使检索结果更贴合当前情境）
    slot = _meal_slot()
    query = (f"{p.goal} {slot} 摄入 {int(intake.calories)} kcal "
             f"蛋白质 {intake.protein}g 碳水 {intake.carbs}g "
             f"缺口 {int(req.gap.calories if req.gap else 0)} kcal")
    chunks = knowledge.search(query)
    based_on = [c["content"] for c in chunks]

    # 尝试 LLM 生成
    advice_text = None
    meal_kcal = None
    try:
        guide_text = "\n".join(f"- {c['content']}（{c['source']}）" for c in chunks)
        advice_text = llm.chat(
            f"用户画像：目标={p.goal}，基础代谢 BMR={p.bmr} kcal，全天目标摄入={p.targetCalories} kcal，"
            f"忌口={p.avoid or '无'}，过敏原={p.allergy or '无'}。\n"
            f"今日已摄入：热量 {intake.calories} kcal、蛋白质 {intake.protein}g、"
            f"脂肪 {intake.fat}g、碳水 {intake.carbs}g。\n"
            f"当前需要安排的餐次：{_meal_slot()}。\n"
            f"可参考的膳食指南依据：\n{guide_text}\n\n"
            "请给出该餐次的营养建议，用中文输出，并按以下板块组织（用【】作标题）：\n"
            "【下一餐推荐】列出 3~5 种具体食物，每种注明份量、热量(kcal)与蛋白质(g)，并给出本餐合计\n"
            "【营养分析】结合今日已摄入数据，评价热量进度与三大营养素供能比是否合理\n"
            f"【{p.goal}期建议】给出 3~4 条具体、可执行的建议\n"
            "【注意事项】2~3 条提醒\n"
            "硬性要求：\n"
            f"1. 严禁出现过敏原（{p.allergy or '无'}）与忌口（{p.avoid or '无'}）相关食材\n"
            f"2. 全天总摄入不得低于基础代谢 {p.bmr} kcal，禁止极端节食方案\n"
            "3. 量化到克数与千卡，可引用《中国居民膳食指南（2022）》\n"
            "4. 直接给出结论，不要输出推理过程",
            system="你是一名专业营养师，擅长依据《中国居民膳食指南（2022）》给出量化、可执行的饮食建议。",
        )
        if not advice_text or not advice_text.strip():
            raise RuntimeError("LLM 返回空内容")
    except Exception:
        advice_text, meal_kcal = _local_advice(p, intake, req.gap)

    # 安全拦截（need.md 3.6.3）
    # 本地模式给出结构化「全天建议总摄入」，避免文本正则把剩余额度误判为极端节食。
    # 取「全天目标」与「已摄入+本餐」的较大值：后者只是当前进度，若还有后续餐次会低估全天总量。
    if meal_kcal is not None:
        recommended_total = max(float(p.targetCalories or 0), float(intake.calories) + meal_kcal)
    else:
        # LLM 模式：无法从文本可靠反推全天总量，直接用用户全天目标。
        # 若传 None，safety 会退回文本正则，把「本餐 400 kcal」误判成全天极端节食。
        recommended_total = float(p.targetCalories or 0) or None
    check = safety.check(advice_text, allergy=p.allergy or "", bmr=p.bmr,
                         recommended_total=recommended_total)

    return {
        "advice": advice_text,
        "basedOn": [f"{c['content']}（{c['source']}）" for c in chunks],
        "safe": check["safe"],
        "reason": check.get("reason", ""),
    }


def _local_advice(p: Profile, intake: Intake, gap: Intake) -> str:
    """
    LLM 未配置时的本地建议引擎。

    特点：
      1. 餐次感知 —— 按当前时间判断下一餐（早/午/晚/加餐）
      2. 多样化   —— 从食物库随机组合，同一输入每次给出不同搭配
      3. 有依据   —— 量化到克数/热量，并标注《中国居民膳食指南（2022）》对应标准
      4. 安全     —— 自动排除与过敏原/忌口冲突的食材
    """
    g = gap or Intake()
    slot = _meal_slot()
    remaining = float(g.calories or 0)
    protein_gap = float(g.protein or 0)
    allergy, avoid = p.allergy or "", p.avoid or ""

    pool = {k: _filter_foods(v, allergy, avoid) for k, v in FOOD_LIBRARY.items()}

    lines = []
    picked = []

    # ---- 1. 热量状态与餐次 ----
    if remaining > 0:
        lines.append(f"【下一餐 · {slot}】今日剩余额度约 {int(remaining)} kcal，"
                     f"本餐建议摄入 {int(min(remaining, max(remaining * 0.6, 250)))} kcal 左右，其余留给后续餐次。")
    else:
        lines.append(f"【下一餐 · {slot}】今日已超出目标约 {int(-remaining)} kcal，"
                     f"本餐建议控制在 {int(max(150, 300 + remaining * 0.3))} kcal 以内，以蔬菜和高纤维食物为主。")

    # ---- 2. 组合本餐搭配 ----
    if remaining > 0:
        # 主食
        staple = random.choice(pool["主食（谷薯类）"])
        picked.append((staple, "主食"))

        # 蛋白质：缺口大时优先高蛋白
        protein_pool = pool["优质蛋白（鱼禽蛋豆）"]
        if protein_gap > 15:
            protein_pool = sorted(protein_pool, key=lambda f: -f["protein"])[:4] or protein_pool
        protein_food = random.choice(protein_pool)
        picked.append((protein_food, "优质蛋白"))

        # 蔬菜
        veg = random.sample(pool["蔬菜（深色优先）"], k=min(2, len(pool["蔬菜（深色优先）"])))
        for v in veg:
            picked.append((v, "蔬菜"))

        # 热量富余时补充水果
        subtotal = sum(f["kcal"] for f, _ in picked)
        if remaining - subtotal > 180:
            picked.append((random.choice(pool["水果"]), "水果"))
    else:
        # 已超标：只给低热量高纤维搭配
        veg = random.sample(pool["蔬菜（深色优先）"], k=min(2, len(pool["蔬菜（深色优先）"])))
        for v in veg:
            picked.append((v, "蔬菜"))
        picked.append((random.choice(pool["优质蛋白（鱼禽蛋豆）"]), "优质蛋白"))

    # ---- 3. 输出搭配明细 ----
    lines.append("")
    lines.append("推荐搭配：")
    for idx, (food, category) in enumerate(picked, 1):
        lines.append(f"  {idx}. 【{category}】{food['name']} {food['portion']}"
                     f" ≈ {food['kcal']} kcal，蛋白质 {food['protein']}g（{food['note']}）")

    total_kcal = sum(f["kcal"] for f, _ in picked)
    total_protein = sum(f["protein"] for f, _ in picked)
    lines.append("  " + "─" * 46)
    lines.append(f"  本餐合计 ≈ {int(total_kcal)} kcal，蛋白质 ≈ {int(total_protein)}g")

    # ---- 4. 今日营养进度 ----
    lines.append("")
    lines.append("【今日营养进度】")
    lines.append(f"  · 热量：已摄入 {int(intake.calories)} / 目标 {int(p.targetCalories)} kcal"
                 f"（{'剩余 ' + str(int(remaining)) if remaining > 0 else '超出 ' + str(int(-remaining))}）")
    protein_target = max(int(p.targetCalories * 0.15 / 4), 40)
    lines.append(f"  · 蛋白质：已摄入 {int(intake.protein)}g / 建议约 {protein_target}g"
                 f"（{'还差 ' + str(int(protein_gap)) + 'g' if protein_gap > 0 else '已达标'}）")
    lines.append(f"  · 脂肪 {int(intake.fat)}g、碳水 {int(intake.carbs)}g")

    # ---- 5. 供能比分析（按指南标准真实计算） ----
    lines.append("")
    lines.append("【营养素供能比评估】")
    for item in _macro_balance(intake):
        lines.append(f"  · {item}")

    # ---- 6. 目标专属建议（随机 2 条） ----
    lines.append("")
    lines.append(f"【{p.goal}期专属建议】")
    for t in random.sample(GOAL_TIPS.get(p.goal, GOAL_TIPS["维持"]), k=2):
        lines.append(f"  · {t}")

    # ---- 7. 随机抽取 4 个拓展板块（保证每次结构也不同） ----
    panels = [
        ("烹饪方式建议", random.sample(COOKING_TIPS, k=2)),
        ("加餐与零食选择", random.sample(SNACK_TIPS, k=2)),
        ("饮水与作息", random.sample(HYDRATION_TIPS, k=2)),
        ("运动建议", random.sample(EXERCISE_TIPS, k=2)),
        ("常见误区提醒", random.sample(MYTH_TIPS, k=2)),
        ("食材替换方案", random.sample(SWAP_TIPS, k=2)),
        ("外卖与外食建议", random.sample(TAKEOUT_TIPS, k=2)),
        ("一周饮食规划", random.sample(WEEKLY_TIPS, k=2)),
        ("体重与进度管理", random.sample(PROGRESS_TIPS, k=2)),
        ("膳食指南参考量（每天）", random.sample(GUIDELINE_TARGETS, k=3)),
    ]
    for title, tips in random.sample(panels, k=4):
        lines.append("")
        lines.append(f"【{title}】")
        for t in tips:
            lines.append(f"  · {t}")

    # ---- 8. 注意事项 ----
    lines.append("")
    lines.append("【注意事项】")
    if avoid:
        lines.append(f"  · 已避开忌口：{avoid}")
    if allergy:
        lines.append(f"  · 已排除过敏原：{allergy}")
    lines.append("  · 以上建议基于《中国居民膳食指南（2022）》，仅供参考，不能替代专业医疗意见")

    # 返回 (文本, 本餐建议热量)，后者供 safety 做结构化校验
    return "\n".join(lines), total_kcal


def _macro_balance(intake: Intake) -> list:
    """按《中国居民膳食指南（2022）》供能比标准评估三大营养素"""
    kcal = float(intake.calories or 0)
    if kcal <= 0:
        return ["今日暂无摄入记录，先记录一餐后才能评估供能比。"]

    p_ratio = float(intake.protein or 0) * 4 / kcal * 100
    f_ratio = float(intake.fat or 0) * 9 / kcal * 100
    c_ratio = float(intake.carbs or 0) * 4 / kcal * 100

    out = [f"蛋白质 {p_ratio:.0f}%（推荐 10%~15%）｜脂肪 {f_ratio:.0f}%（推荐 20%~30%）"
           f"｜碳水 {c_ratio:.0f}%（推荐 50%~65%）"]

    issues = []

    if p_ratio < 10:
        issues.append("蛋白质占比偏低，建议增加鱼禽蛋豆等优质蛋白，每餐至少一个掌心大小的蛋白食物。")
    elif p_ratio > 20:
        issues.append("蛋白质占比偏高，注意搭配足量蔬菜与主食，减轻肾脏代谢负担。")

    if f_ratio > 30:
        issues.append("脂肪占比偏高，建议减少油炸与肥肉，改用蒸、煮、炖的烹调方式。")
    elif f_ratio < 20:
        issues.append("脂肪占比偏低，可适量补充坚果、深海鱼等健康脂肪，有助于脂溶性维生素吸收。")

    if c_ratio < 50:
        issues.append("碳水占比偏低，长期可能影响体力与情绪，可适量增加全谷物主食。")
    elif c_ratio > 65:
        issues.append("碳水占比偏高，建议用杂粮饭、糙米替换部分精制主食，并增加蔬菜比例。")

    # 有问题时报问题；完全没问题时才给正面评价（避免「偏低」与「基本合理」同时出现）
    out.extend(issues if issues else ["三大营养素供能比处于推荐区间，继续保持当前饮食结构。"])
    return out
