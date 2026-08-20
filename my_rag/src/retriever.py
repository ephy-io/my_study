
from src.config import CONFIG
from src.embedder import embed_ques
from src.clients import get_qdrant_client

#创建检索函数
def retriever(query:str) -> list[dict]:
    #对query进行向量化
    query_vector = embed_ques(query)

    #加载qdrant_client对象
    client = get_qdrant_client()

    response = client.query_points(
        collection_name=CONFIG.qdrant_collection,
        query= query_vector,
        limit=CONFIG.retrieval_top_k,
        with_payload=True   #让 Qdrant 返回匹配结果里的 payload 信息
    )
    results = []
    for point in response.points:

        payload = point.payload or {}

        results.append(
            {
                "page_content": payload.get("page_content", ""),
                "metadata": payload.get("metadata", {}),
                "score": point.score
            }
        )
    return results

    