from src.rag_service import ask_rag

result = ask_rag("研究生国家奖学金申请条件是什么？")

print("\n回答:")
print(result["answer"])

print("\n来源:")
for source in result["source"]:
    print(
        source["source"],
        source["page"],
        source["score"]
    )
