#自动转换成document类型

# from pathlib import Path
# from langchain_community.document_loaders import TextLoader

# txt_path = Path(r".\LangChain_文档处理练习数据\设备故障上报与交接班规范.txt")

# #创建Textloader对象

# loader = TextLoader(file_path=txt_path, encoding="utf-8")

# #执行

# documents = loader.load()

# print(type(documents))
# print(documents)

#手动转换成为document类型
import json
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

txt_path = Path(r".\LangChain_文档处理练习数据\设备故障上报与交接班规范.txt")

#加载txt内容
with txt_path.open("r", encoding="utf-8") as f:
    text = f.read()

#判断text是否为字符串
if not isinstance(text,str):
    raise TypeError("text不是字符串类型")

#消除前后空格，制表符等
text = text.strip()

if text:
    documents = [
        Document(
            page_content= text,
            metadata = {
                "source":txt_path.name,
                "type": "handmake"
            }
        )
    ]

print(type(documents))
print(documents[0].page_content)


#切分document

#创建RecursiveCharacterTextSplitter对象

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 200,
    chunk_overlap =30,
    length_function = len,
    separators = ["\n\n", "\n", "。", "！", "？", "，", " ", ""],
    is_separator_regex = False,
    add_start_index = True
)

#切分chunk
chunks = splitter.split_documents(documents)

print(chunks[0])
print(type(chunks[0]))

#给chunk编号
for paper_num, chunk in enumerate(chunks, start=1):
    chunk.metadata["paper_num"] = paper_num
    chunk.metadata["id"] = f"{paper_num:03d}"

#转换为字典类型
record_chunk = []
for chunk in chunks:
    record_chunk.append(
        {
            "page_content": chunk.page_content,
            "metadata": chunk.metadata
        }
    )

#将chunk存为json文件
json_path = txt_path.with_suffix(".json")

with json_path.open("w", encoding="utf-8") as f:
    json.dump(record_chunk, f, ensure_ascii=True, indent=2)
    print(f"成功存为json文件：{json_path}")

#检查是否存成功
with json_path.open("r", encoding="utf-8") as f:
    loader = json.load(f)
    print(type(loader))
    print(type(loader[0]))
    print(loader[0]["metadata"])
