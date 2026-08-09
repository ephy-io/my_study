from rag_core import answer_question

question = input("问题：").strip()
result = answer_question(question, 3)

print("\n回答：")
print(result["answer"])

print("\n来源：")
for source in result["sources"]:
    print(
        source["source"],
        source["chunk_id"],
    )
