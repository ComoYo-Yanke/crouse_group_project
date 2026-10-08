# -*- coding: utf-8 -*-
"""
安全拦截规则引擎（need.md 11.3 危险建议规则）：
  1. 建议热量 < 基础代谢
  2. 极端节食（< 800 kcal/天）
  3. 推荐违禁药物
  4. 与过敏原冲突
"""

BANNED_WORDS = [
    "减肥药", "瘦身药", "泻药", "利尿剂", "西布曲明", "芬氟拉明",
    "催吐", "断食", "绝食", "只喝水", "代餐完全替代", "辟谷",
    "三唑仑", "安非他命", "甲状腺素减肥",
]

ALLERGY_HINTS = {
    "花生": ["花生", "花生酱", "花生油"],
    "海鲜": ["虾", "蟹", "贝", "鱼", "海鲜", "鱿鱼", "生蚝"],
    "牛奶": ["牛奶", "酸奶", "奶酪", "奶油", "乳制品"],
    "鸡蛋": ["鸡蛋", "蛋清", "蛋黄", "蛋"],
    "大豆": ["大豆", "豆腐", "豆浆", "豆制品"],
    "麸质": ["小麦", "面包", "面条", "馒头", "面粉"],
}


def check(advice: str, allergy: str = "", bmr: int = 0) -> dict:
    """返回 {safe, reason}"""
    if not advice:
        return {"safe": True, "reason": ""}

    problems = []

    # 规则1/2：极端节食提示（文本中明确建议极低热量时）
    import re
    kcal_numbers = [int(n) for n in re.findall(r"(\d{3,4})\s*(?:kcal|千卡|大卡)", advice)]
    if kcal_numbers:
        if any(n < 800 for n in kcal_numbers):
            problems.append("建议中包含低于 800 kcal/天的极端节食方案")
        if bmr > 0 and any(n < bmr * 0.8 for n in kcal_numbers):
            problems.append("建议热量明显低于基础代谢，存在健康风险")

    # 规则3：违禁药物/极端手段
    for word in BANNED_WORDS:
        if word in advice:
            problems.append(f"建议中包含危险内容：「{word}」")

    # 规则4：过敏原冲突
    if allergy:
        for allergen in [a.strip() for a in re.split(r"[、,，\s]+", allergy) if a.strip()]:
            for hint in ALLERGY_HINTS.get(allergen, [allergen]):
                if hint in advice:
                    problems.append(f"建议包含过敏原「{allergen}」相关食材，与用户过敏史冲突")
                    break

    if problems:
        return {"safe": False, "reason": "；".join(problems)}
    return {"safe": True, "reason": ""}
