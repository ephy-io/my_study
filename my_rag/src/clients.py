


from openai import OpenAI
from qdrant_client import QdrantClient
from src.config import CONFIG

_qwen_client = None
_qdrant_client = None

#创建openai的对象
def get_qwen_client() -> OpenAI:
    global _qwen_client

    if _qwen_client is None:

        if not CONFIG.dashscope_api_key:
            raise ValueError("没有找到api_key")
        if not CONFIG.dashscope_base_url:
            raise ValueError("没有找到base_url")

        _qwen_client = OpenAI(
            api_key=CONFIG.dashscope_api_key,
            base_url=CONFIG.dashscope_base_url
        )
    return _qwen_client

#创建qdrant的对象
def get_qdrant_client() -> QdrantClient:
    global _qdrant_client

    if _qdrant_client is None:
        kwargs = {
            "url": CONFIG.qdrant_url,
            "timeout" : 30
        }
        if CONFIG.qdrant_key:
            kwargs["qdrant_key"] = CONFIG.qdrant_key

        _qdrant_client = QdrantClient( **kwargs)

    return _qdrant_client

