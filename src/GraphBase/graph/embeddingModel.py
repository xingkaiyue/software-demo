import os
import json
import requests
import asyncio
from zhipuai import ZhipuAI
import config
from src.GraphBase.graph.config_logging.config_logging import logger
from config_logging import hashstr, get_docker_safe_url

class BaseEmbeddingModel:
    embed_state = {}

    def get_dimension(self):
        if hasattr(self, "dimension"):
            return self.dimension

        if hasattr(self, "embed_model_fullname"):
            return config.embed_model_names[self.embed_model_fullname].get("dimension", None)

        return config.embed_model_names[self.model].get("dimension", None)

    def encode(self, message):
        return self.predict(message)

    def encode_queries(self, queries):
        return self.predict(queries)

    async def aencode(self, message):
        return await asyncio.to_thread(self.encode, message)

    async def aencode_queries(self, queries):
        return await asyncio.to_thread(self.encode_queries, queries)

    async def abatch_encode(self, messages, batch_size=20):
        return await asyncio.to_thread(self.batch_encode, messages, batch_size)

    def batch_encode(self, messages, batch_size=20):
        logger.info(f"Batch encoding {len(messages)} messages")
        data = []

        if len(messages) > batch_size:
            task_id = hashstr(messages)
            self.embed_state[task_id] = {
                'status': 'in-progress',
                'total': len(messages),
                'progress': 0
            }

        for i in range(0, len(messages), batch_size):
            group_msg = messages[i:i+batch_size]
            logger.info(f"Encoding {i} to {i+batch_size} with {len(messages)} messages")
            response = self.encode(group_msg)
            logger.debug(f"Response: {len(response)=}, {len(group_msg)=}, {len(response[0])=}")
            data.extend(response)

        if len(messages) > batch_size:
            self.embed_state[task_id]['progress'] = len(messages)
            self.embed_state[task_id]['status'] = 'completed'

        return data


class ZhipuEmbedding(BaseEmbeddingModel):

    def __init__(self, config) -> None:
        self.config = config
        self.model = config.embed_model_names[config.embed_model]["name"]
        self.dimension = config.embed_model_names[config.embed_model]["dimension"]
        self.client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))
        self.embed_model_fullname = config.embed_model

    def predict(self, message):
        response = self.client.embeddings.create(
            model=self.model,
            input=message,
        )
        data = [a.embedding for a in response.data]
        return data


def get_embedding_model(config):
    if not config.enable_knowledge_base:
        return None

    provider, model_name = config.embed_model.split('/', 1)
    assert config.embed_model in config.embed_model_names.keys(), f"Unsupported embed model: {config.embed_model}, only support {config.embed_model_names.keys()}"
    logger.debug(f"Loading embedding model {config.embed_model}")

    if provider == "zhipu":
        model = ZhipuEmbedding(config)

    return model

def handle_local_model(paths, model_name, default_path):
    model_path = paths.get(model_name, default_path)
    return model_path