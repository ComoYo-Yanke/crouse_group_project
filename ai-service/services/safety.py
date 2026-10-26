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


def check(advice: str, allergy: str = "", bmr: int = 0, recommended_total: float = None) -> dict:
    """
    返回 {safe, reason}

    recommended_total：本引擎计算出的「全天建议总摄入」(kcal)。
    传入时按结构化数值校验规则1/2（最可靠），避免仅凭文本正则误判。
    """
    import re

    if not advice:
        return {"safe": True, "reason": ""}

    problems = []

    # 规则1/2 优先用结构化数值判断
    if recommended_total is not None and recommended_total > 0:
        if recommended_total < 800:
            problems.append(f"建议的全天总摄入 {int(recommended_total)} kcal 低于 800 kcal/天，属极端节食")
        if bmr > 0 and recommended_total < bmr * 0.8:
            problems.append(f"建议的全天总摄入 {int(recommended_total)} kcal 明显低于基础代谢 {bmr} kcal，存在健康风险")
    else:
        # 无结构化数值时，退回文本正则：
        # 只校验「全天摄入总量」语境的数字，跳过剩余额度/缺口/单餐等语境，
        # 否则「今日还可摄入 727 kcal」会被误判成「全天只吃 727 kcal」。
        skip_keywords = [
            "还可摄入", "还能摄入", "尚可摄入", "剩余", "还差", "缺口",
            "已超出", "超出", "本餐", "下一餐", "这一餐", "加餐",
            "早餐", "午餐", "晚餐", "单餐", "本顿",
        ]
        kcal_numbers = []
        for sentence in re.split(r"[。；;\n]", advice):
            if any(kw in sentence for kw in skip_keywords):
                continue
            kcal_numbers += [int(n) for n in re.findall(r"(\d{3,4})\s*(?:kcal|千卡|大卡)", sentence)]

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
    # 仅检查「推荐/包含食材」的语境；「已排除过敏原：花生」这类说明性、否定性表述不算冲突，
    # 否则提及过敏原本身就会被拦截。
    if allergy:
        negation_keywords = ["已排除", "已避开", "已过滤", "避免", "避开", "不含", "忌口", "过敏史", "过敏原"]
        check_text = "\n".join(
            s for s in re.split(r"[。；;\n]", advice)
            if not any(kw in s for kw in negation_keywords)
        )
        for allergen in [a.strip() for a in re.split(r"[、,，\s]+", allergy) if a.strip()]:
            for hint in ALLERGY_HINTS.get(allergen, [allergen]):
                if hint in check_text:
                    problems.append(f"建议包含过敏原「{allergen}」相关食材，与用户过敏史冲突")
                    break

    if problems:
        return {"safe": False, "reason": "；".join(problems)}
    return {"safe": True, "reason": ""}
