
from src.clients import get_qwen_client
from src.config import CONFIG

#将知识pdf进行向量化
def embed_text(texts: list[str]) -> list[list[float]]:
    #加载qwen_cilent对象
    qwen_cilent = get_qwen_client()

    all_embedding : list[list[float]] = []

    #把chunks分批次处理,每次处理CONFIG.embedding_batch_size个chunks
    for start in range(0, len(texts), CONFIG.embedding_batch_size):

        batch = texts[start:start+CONFIG.embedding_batch_size]

        response = qwen_cilent.embeddings.create(
            model= CONFIG.embedding_model,
            input=batch,
            dimensions=CONFIG.embedding_dimension,
            encoding_format="float"    
        )
        #对内容进行排序，按照key=item.index的顺序来排序
        result = sorted(
            response.data,
            key=lambda item: item.index
        )
        #把处理好的embedding加入到all_embedding列表中
        for item in result:
            all_embedding.append(item.embedding)

    return all_embedding

#将用户的问题也进行向量化
def embed_ques(ques:str) -> list[float]:
    if not isinstance(ques, str):
        raise ValueError("输入的问题不是str类型")

    if not ques.strip():
        raise ValueError("请输入有效的问题")

    return embed_text( [ques.strip()])[0]  #embed_text返回的是list[list[]],对于ques返回时，里面就一个元素，[0]要把这个元素提取出来

    