# modules/recommender/cold_start.py
def recommend_by_profile(user_profile, item_pool, top_k=5):
    if not user_profile:
        return []

    interests = user_profile["tags"]
    scored = []

    for item_id, item_info in item_pool.items():
        score = 0
        for tag in item_info.get("tags", []):
            if tag in interests.values():
                score += 1
        scored.append((item_id, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [item for item, _ in scored[:top_k]]


def recommend_popular(behavior_logs, top_k=5):
    from collections import Counter
    counter = Counter()
    for b in behavior_logs:
        counter[b["item_id"]] += b["score"]
    return [item for item, _ in counter.most_common(top_k)]