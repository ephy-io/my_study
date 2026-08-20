
import json
from qdrant_client import  models
from src.clients import get_qdrant_client
from src.config import CONFIG, CHUNK_DATA
from src.embedder import embed_text
from src.vector_store import reset_collection, get_collection_count

def build_vector_store() -> None:

    #加载chunks
    with CHUNK_DATA.open("r", encoding='utf-8') as f:
        chunks = json.load(f)

    #加载创建数据库对象
    reset_collection()

    client = get_qdrant_client()

    batch_size = CONFIG.embedding_batch_size

    for start in range(0, len(chunks), batch_size):
        #加载出每一批次的chunks
        batch_chunks = chunks[start: start + batch_size]

        texts = [
            chunk["page_content"]
            for chunk in batch_chunks
        ]
        #对这一批次text进行向量化
        vectors = embed_text(texts)

        #创建空的数据点空列表
        points = []

        #使用zip将chunks和vector进行配对
        for offset, (chunk, vector) in enumerate(zip(batch_chunks, vectors)):

            #整理metadata信息,把key中value为空的键值对删除，避免把无意义的空字段存入 Qdrant
            metadata = {
                key : value
                for key, value in chunk["metadata"].items()
                if value is not None
            }
            #创建数据点的id
            point_id = start + offset 
            #把一条数据包装成 Qdrant 能存储的格式Point
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "page_content": chunk["page_content"],
                        "metadata": metadata
                    }
                )
            )
            #将points数据写入Qdrant数据库
            client.upsert(
                collection_name=CONFIG.qdrant_collection,
                points=points,
                wait=True   #写完之后再返回
            )
            #显示写入的进度
            print(
                f"已写入："
                f"{min(start+batch_size, len(chunks))}"
                f"/{len(chunks)}"
            )
    print("向量库chunk数量: ", get_collection_count())


# 当该文件被直接运行时，执行build_vector_store()函数；
# 如果该文件被其他模块import，则不会自动执行。
if __name__ == "__main__":
    build_vector_store()
