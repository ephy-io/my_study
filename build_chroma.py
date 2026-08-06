from rag_core import build_index , retrivere_document

build_index()
print("数据库创建成功")

documents = retrivere_document(
    "设备出现异常振动时应该检查什么？",
    k=3,
)

for rank, document in enumerate(documents, start=1):
    print("=" * 60)
    print(f"排名：{rank}")
    print(f"source：{document.metadata.get('source')}")
    print(f"chunk_id：{document.metadata.get('chunk_id')}")
    print(document.page_content)