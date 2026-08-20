
from src.retriever import retriever

query = "研究生国家奖学金申请条件是什么？"

result = retriever(query)

for index, item in enumerate(result, start=1):
    metadata = item["metadata"]

    print(f"\n--- 结果 {index} ---")

    print(
        "来源：",
        metadata.get("source")
    )

    print(
        "页码：",
        metadata.get("page")
    )

    print(
        "相似度：",
        item["score"]
    )

    print(
        item["page_content"]
    )

