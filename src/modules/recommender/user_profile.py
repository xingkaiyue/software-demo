# modules/recommender/user_profile.py
from collections import Counter

USER_PROFILES = {}

def init_user_profile(user_id: str, tags: dict):
    USER_PROFILES[user_id] = {
        "tags": tags,
        "interests": Counter()
    }


def update_user_profile(user_id: str, item_tags: list):
    if user_id not in USER_PROFILES:
        return
    USER_PROFILES[user_id]["interests"].update(item_tags)


def get_user_profile(user_id: str):
    return USER_PROFILES.get(user_id)