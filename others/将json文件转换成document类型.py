# # 手动处理json文件为document类型 

# #总体思路：
# #1、加载json文件内容
# #2、处理当json最外层是{}时的情况，判断records是不是列表类型
# #3、开始循环编列每一个record，做：判断记录是不是dict，再检查记录中是否有"text"，然后检查text是否为str，最后检查text是否为空
# #4、转换为document类型并加入到documents列表中

# import json 
# from pathlib import Path
# from langchain_core.documents import Document

# json_path = Path(r".\练习输入_documents.json")

# #加载json文件内容
# with open(json_path, "r", encoding="utf-8") as f:
#     records = json.load(f)

# #print(type(records))

# #处理当json外层是字典时，处理为列表
# if isinstance(records,dict):
#     records = [records]

# #判断record是否是列表
# if not isinstance(records,list):
#     raise TypeError(f"{records}不是列表类型")

# documents = []
# print(records[0])


# for index,record in enumerate(records, start=1):
#     #总体思路：先判断记录是不是dict，再检查记录中是否有"text"，然后检查text是否为str，最后检查text是否为空

#     #判断record是不是字典类型
#     if not isinstance(record,dict):
#         raise TypeError(f"第{index}数据不是字典类型")

#     #判断text是否为空，为空则跳过
#     if "text" not in record:
#         raise ValueError(f"第{index}条记录缺少必须字段text")

#     raw_text = record['text']
#     #判断text是不是字符类型
#     if not isinstance(raw_text, str) :
#         raise TypeError(f"第{index}条记录text不是字符类型")

#     text = raw_text.strip()   #strip()去掉首尾的空格、换行和制表符

#     if not text:
#         continue

#     documents.append(
#         Document(
#             page_content= text,
#             metadata= {
#                 "source": record.get("source"),
#                 "page_num":record.get("page_num"),
#                 "section": record.get("section")
#             }
#         )
#     )

# print(type(documents))
# print(type(documents[0]))
# print(documents[0])    



#自动处理json文件转换为document类型
from pathlib import Path
from langchain_community.document_loaders import JSONLoader

json_path = Path(r".\练习输入_documents.json")


def metadata_func(record:dict,metadata:dict) -> dict:
    source = record.get("source")
    paper_num = record.get("paper_num")
    section = record.get("section")

    if source:
        metadata["source"] = source
    if paper_num:
        metadata["paper_num"] = paper_num
    if section:
        metadata["section"] = section

    return metadata



#创建JSONLoader对象
loader = JSONLoader(
    json_path,
    jq_schema=".[]",      #表示遍历 JSON 顶层列表中的每一条记录
    content_key="text",
    metadata_func=metadata_func,
    text_content=True     #表示提取出来的 text 内容按照字符串文本处理
)

documents = loader.load()

print(type(documents))
print(type(documents[0]))
print(documents[0]) 

