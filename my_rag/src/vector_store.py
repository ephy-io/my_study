
from qdrant_client import models
from src.clients import get_qdrant_client
from src.config import CONFIG

#重新创建数据库
def reset_collection() -> None:
    #加载qdrant_client对象
    client = get_qdrant_client()

    #检查旧的数据在不在，存在就要删除
    if client.collection_exists( CONFIG.qdrant_collection):
        client.delete_collection(CONFIG.qdrant_collection)

    #创建新的数据库collection
    client.create_collection(
        collection_name=CONFIG.qdrant_collection,
        vectors_config=models.VectorParams(
            size=CONFIG.embedding_dimension,  #size的大小
            distance=models.Distance.COSINE     #使用余弦相似度来衡量
        )
    )


#统计chunks的数量
def get_collection_count() -> int:
    client = get_qdrant_client()

    result = client.count(
        collection_name=CONFIG.qdrant_collection,
        exact=True  #精确计算
    )

    return result
    