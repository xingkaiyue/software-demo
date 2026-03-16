import time
import random
import os
from .config_logging import logger

def hashstr(input_string, length=8, with_salt=False):
    import hashlib
    # 添加时间戳作为干扰
    if with_salt:
        input_string += str(time.time() + random.random())

    hash = hashlib.md5(str(input_string).encode()).hexdigest()
    return hash[:length]


def get_docker_safe_url(base_url):
    if os.getenv("RUNNING_IN_DOCKER") == "true":
        # 替换所有可能的本地地址形式
        base_url = base_url.replace("http://localhost", "http://host.docker.internal")
        base_url = base_url.replace("http://127.0.0.1", "http://host.docker.internal")
        logger.info(f"Running in docker, using {base_url} as base url")
    return base_url