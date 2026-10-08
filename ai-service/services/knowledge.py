# -*- coding: utf-8 -*-
"""
膳食指南知识库（RAG 的本地简化版）

正式版：将《中国居民膳食指南（2022）》分块向量化入库，检索 top-k。
演示版：内置条目 + 关键词匹配，返回 {content, source} 结构与正式版一致。
"""

GUIDELINES = [
    {"content": "成人每日膳食应包含谷薯类、蔬菜水果、畜禽鱼蛋奶、大豆坚果四类食物，平均每天摄入12种以上食物，每周25种以上。",
     "source": "中国居民膳食指南（2022）准则1", "keywords": ["均衡", "搭配", "种类", "多样"]},
    {"content": "坚持谷类为主的平衡膳食模式，每天摄入谷薯类食物200~300g，其中全谷物和杂豆类50~150g，薯类50~100g。",
     "source": "中国居民膳食指南（2022）准则1", "keywords": ["主食", "谷物", "碳水", "粗粮", "全谷"]},
    {"content": "餐餐有蔬菜，保证每天摄入不少于300g新鲜蔬菜，深色蔬菜应占一半；天天吃水果，保证每天摄入200~350g新鲜水果。",
     "source": "中国居民膳食指南（2022）准则3", "keywords": ["蔬菜", "水果", "纤维", "维生素"]},
    {"content": "吃各种各样的奶制品，摄入量相当于每天300ml以上液态奶；经常摄入全谷物、大豆制品。",
     "source": "中国居民膳食指南（2022）准则3", "keywords": ["奶", "钙", "蛋白", "大豆"]},
    {"content": "鱼、禽、蛋类和瘦肉摄入要适量，平均每天120~200g。优先选择鱼和禽类。吃鸡蛋不弃蛋黄。",
     "source": "中国居民膳食指南（2022）准则4", "keywords": ["肉", "蛋白", "鸡蛋", "鱼"]},
    {"content": "培养清淡饮食习惯，成年人每天食盐不超过5g，烹调油25~30g。少吃高盐和油炸食品。",
     "source": "中国居民膳食指南（2022）准则5", "keywords": ["盐", "钠", "油", "清淡", "油炸"]},
    {"content": "控制添加糖的摄入量，每天不超过50g，最好控制在25g以下，不喝或少喝含糖饮料。",
     "source": "中国居民膳食指南（2022）准则5", "keywords": ["糖", "饮料", "控糖", "甜"]},
    {"content": "足量饮水，成年人每天7~8杯（1500~1700ml），提倡饮用白开水和茶水，不喝或少喝含糖饮料。",
     "source": "中国居民膳食指南（2022）准则6", "keywords": ["水", "饮水", "喝水"]},
    {"content": "各年龄段人群都应天天进行身体活动，坚持日常身体活动，每周至少进行5天中等强度身体活动，累计150分钟以上。",
     "source": "中国居民膳食指南（2022）准则2", "keywords": ["运动", "锻炼", "活动", "久坐"]},
    {"content": "规律进餐，定时定量；不暴饮暴食、不偏食挑食、不过度节食，保持能量摄入与消耗的平衡。",
     "source": "中国居民膳食指南（2022）准则6", "keywords": ["节食", "规律", "三餐", "暴食"]},
]

DEFAULT_CHUNKS = [
    GUIDELINES[0], GUIDELINES[2], GUIDELINES[4], GUIDELINES[6],
]


def search(query: str, top_k: int = 4) -> list:
    """关键词匹配检索，返回 [{content, source}]"""
    if not query:
        return [{"content": g["content"], "source": g["source"]} for g in DEFAULT_CHUNKS]

    scored = []
    for g in GUIDELINES:
        score = sum(1 for kw in g["keywords"] if kw in query)
        if g["content"] and any(ch in query for ch in g["content"][:50]):
            score += 0.5
        scored.append((score, g))
    scored.sort(key=lambda x: -x[0])

    hits = [g for s, g in scored[:top_k] if s > 0]
    if not hits:
        hits = DEFAULT_CHUNKS
    return [{"content": g["content"], "source": g["source"]} for g in hits]
