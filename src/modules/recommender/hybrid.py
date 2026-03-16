# modules/recommender/hybrid.py
from modules.recommender.behavior_logger import get_behavior_logs
from modules.recommender.collaborative_filter import recommend_cf
from modules.recommender.cold_start import (
    recommend_by_profile,
    recommend_popular
)
from modules.recommender.user_profile import get_user_profile

def hybrid_recommend(user_id, item_pool, top_k=5):
    behavior_logs = get_behavior_logs()
    user_logs = [b for b in behavior_logs if b["user_id"] == user_id]
    profile = get_user_profile(user_id)

    # 冷启动：完全无行为
    if not user_logs:
        return recommend_by_profile(profile, item_pool, top_k)

    # 行为很少
    if len(user_logs) < 5:
        popular = recommend_popular(behavior_logs, top_k)
        profile_rec = recommend_by_profile(profile, item_pool, top_k)
        return list(dict.fromkeys(popular + profile_rec))[:top_k]

    # 正常协同过滤
    return recommend_cf(user_id, behavior_logs, top_k)