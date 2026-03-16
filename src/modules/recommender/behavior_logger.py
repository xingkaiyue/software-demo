# modules/recommender/behavior_logger.py
import time

# 简单内存存储
BEHAVIOR_LOGS = []

ACTION_SCORE = {
    "click": 1.0,
    "view": lambda t: min(t / 60, 3.0),
    "like": 4.0,
    "favorite": 5.0
}

def log_behavior(user_id: str, item_id: str, action: str, duration: int = 0):
    score = ACTION_SCORE.get(action, 0)
    if callable(score):
        score = score(duration)

    record = {
        "user_id": user_id,
        "item_id": item_id,
        "action": action,
        "score": score,
        "timestamp": time.time()
    }
    BEHAVIOR_LOGS.append(record)
    return record


def get_behavior_logs():
    return BEHAVIOR_LOGS