
import json
from src.config import  CHUNK_DATA
from src.embedder import embed_text, embed_ques


#加载chunk.json文件
with CHUNK_DATA.open("r", encoding='utf-8') as f:
    chunks = json.load(f)

texts = [
    chunks[0]["page_content"],
    chunks[1]["page_content"]
]

vector = embed_text(texts)

print(vector)
print("chunks的数量:", len(vector))
print("向量维度:", len(vector[0]))

quest = "计算机学会有哪些期刊分类？"

quest_vector = embed_ques(quest)
print(quest_vector)
print("问题的维度为：", len(quest_vector))
