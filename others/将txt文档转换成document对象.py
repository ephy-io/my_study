
#手动版加载 思路：读取txt内容 → 判断提取的文本是否为空  → 将text转换成document对象

# from pathlib import Path
# from langchain_core.documents import Document

# txt_path = Path(r".\设备故障上报与交接班规范.txt")

# #读取txt文件，返回str
# text = txt_path.read_text(encoding="utf-8")
# text = text.strip()

# #判断text是否为空，若为空直接报错并且停止整个程序
# if not text :
#     raise   ValueError("txt文件没有有效的文本")

# print(type(text))
# #print(text)
# #把text转换成document类型
# documents = [
#     Document(
#         page_content= text,
#         metadata={
#             "source": txt_path.name,
#             "file_type": "txt"
#         }       
#     )
# ]

# print(type(documents))
# print(type(documents[0]))
# #print(documents)


# 自动加载版   思路：文件路径 → 创建loader对象 → 调用loader.load()得到documents
from pathlib import Path
from langchain_community.document_loaders import TextLoader

txt_path = Path(r".\设备故障上报与交接班规范.txt")

#创建TextLoader对象
loader = TextLoader(
    file_path = txt_path,
    encoding = "utf-8"
)

documents = loader.load()

print(type(loader))
print(type(documents[0]))
print(type(documents))
