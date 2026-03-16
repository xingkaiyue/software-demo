# modules/recommender/collaborative_filter.py
from typing import List, Dict

def recommend_cf(user_id: str, user_data: Dict, item_pool: List[Dict] = None, top_n: int = 5):
    """
    简单协同过滤示例：
    - user_data['behaviors'] 包含用户行为
    - item_pool 是图书列表，每本书有 tags 和 popularity
    """
    if item_pool is None:
        item_pool = []

    # 简单计算每本书的分数
    scores = []
    for item in item_pool:
        score = 0
        # 标签匹配
        if 'tags' in item and 'tags' in user_data:
            score += len(set(item['tags']).intersection(set(user_data.get('tags', []))))
        # 简单加上用户行为权重
        for b in user_data.get('behaviors', []):
            if b['item_id'] == item['item_id']:
                score += 1 + b.get('duration', 0)/60  # 点击+浏览时间分
        # 加上受欢迎度
        score += item.get('popularity', 0)/100
        scores.append((item['item_id'], score))

    # 按分数排序取 top_n
    scores.sort(key=lambda x: x[1], reverse=True)
    top_items = [x[0] for x in scores[:top_n]]
    return top_items

# 测试用
if __name__ == "__main__":
    user_data = {
        "user_id": "u1001",
        "tags": ["计算机", "数学"],
        "behaviors": [
            {"item_id": "book001", "action": "click", "duration": 120},
            {"item_id": "book002", "action": "view", "duration": 60}
        ]
    }

    item_pool = [
        {"item_id": "book001", "tags": ["计算机"], "popularity": 100},
        {"item_id": "book002", "tags": ["数学"], "popularity": 80},
        {"item_id": "book003", "tags": ["文学"], "popularity": 50},
    ]

    recs = recommend_cf(user_id="u1001", user_data=user_data, item_pool=item_pool, top_n=5)
    print("推荐结果:", recs)