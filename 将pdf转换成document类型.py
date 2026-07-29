# #手动处理pdf文件转换成document文件     思路：路径 → 创建PdfReader对象  → 循环罗列reader.pages，并且把text转换成Document对象

# from pathlib import Path
# from pypdf import PdfReader
# from langchain_core.documents import Document


# #pdf路径
# pdf_path = Path(r".\汽车零部件加工设备预测性维护手册.pdf")

# #创建PdfReader对象
# reader = PdfReader(pdf_path)

# documents = []

# for paper_num, page in enumerate(reader.pages, start=1):
#     extract_text = page.extract_text()

#     #判断extract_text是否为空
#     if extract_text is None:
#         continue

#     text = extract_text.strip()

#     documents.append(
#         Document(
#             page_content = text,
#             metadata={
#                 "source": pdf_path.name,
#                 "file_type": "pdf",
#                 "paper_num": paper_num
#             }
#         )
#     )

# print(type(reader))
# print(type(text))
# print(type(documents))
# print(type(documents[0]))
# print(documents[0])


#自动版pdf转换成document类型
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

pdf_path = Path(r".\汽车零部件加工设备预测性维护手册.pdf")

#创建pyPDFLoader
loader = PyPDFLoader(
    pdf_path,
    mode="page"     #mode="page" 的作用是：按页加载 PDF。默认情况下就是mode="page"
    )

documents = loader.load()

print(type(loader))
print(type(documents))
print((type(documents[0])))
print(documents[0])