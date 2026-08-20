
from src.retriever import retriever
from src.llm import generate_answer

#封装rag
def ask_rag(question) -> dict:

    contexts = retriever(question)

    answer = generate_answer(question, contexts)

    sources = []
    seen = set()

    for item in contexts:

        metadata = item["metadata"]
        source = metadata.get("source", "未知文件")
        page = metadata.get("page", "未知页码")

        key = (source, page)
        #检查来源和页码是否已经存在，存在则不加入，相同的来源和页码只要一个即可
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            {
                "source":source,
                "page":page,
                "score":item["score"]
            }
        )
    return {
        "answer":answer,
        "source": sources
    }






