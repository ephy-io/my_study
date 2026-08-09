# #自动将pdf转换
# from pathlib import Path
# from langchain_community.document_loaders import PyPDFLoader

# pdf_path = Path(r".\LangChain_文档处理练习数据\汽车零部件加工设备预测性维护手册.pdf")

# #创建PyPDFLoader对象
# loader = PyPDFLoader(file_path=pdf_path, mode= "page")

# documents = loader.load()

# print(type(documents[0]))
# print(documents[0])


#手动转换
import json
from pathlib import Path 
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

pdf_path = Path(r".\LangChain_文档处理练习数据\汽车零部件加工设备预测性维护手册.pdf")

#加载pdf文件
reader = PdfReader(pdf_path)

#遍历pages
documents= []
for paper_num, page in enumerate(reader.pages, start=1):
    text = page.extract_text() or ""

    text = text.strip()
    if text :
         documents.append(
            Document(
                 page_content= text,
                 metadata= {
                      "source": pdf_path.name,
                      "type": "handmake"
                 }
            )
         )
print(type(documents[0]))
print(documents[0].metadata)

#切分,创建RecursiveCharacterTextSplitter对象
spliter = RecursiveCharacterTextSplitter(
     chunk_size = 200,
     chunk_overlap = 30,
     length_function = len,
     separators = ["\n\n", "\n", "。", "？", "！", " ", ""],
     is_separator_regex = False,
     add_start_index = True

)

#正式切分
chunks = spliter.split_documents(documents)

#给chunk编号
for paper_num, chunk in enumerate(chunks, start=1):
     chunk.metadata["paper_num"] = paper_num
     chunk.metadata["id"] = f"{paper_num:03d}"

#转为字典格式
record_chunk = []
for chunk in chunks:
     record_chunk.append(
          {
               "page_content": chunk.page_content,
               "metadata": chunk.metadata
          }
     )

#存为json文件
json_path = pdf_path.with_suffix(".json")
with json_path.open("w", encoding="utf-8") as f:
     json.dump(record_chunk, f, ensure_ascii=True, indent= 2)
     print(f"成功存为json文件：{json_path}")

#检验json文件
with json_path.open("r", encoding="utf-8") as f:
     loader = json.load(f)
     print(type(loader))
     print(loader[0]["page_content"])
     print(loader[0]["metadata"])
