import json
import os
from pathlib import Path
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv


#文件地址
BASE_DIR = Path(__file__).resolve().parent  #当前文件所在的文件夹的地址
DATA_DIR = BASE_DIR / "data"   #数据所在地址

CHUNK_PATH = DATA_DIR / "chunks.example.json"  #chunks_json文件地址
CHROMA_DIR = BASE_DIR / "chroma_db"         # Chroma 本地数据库的保存目录
COLLECTION_NAME = "equipment_knowledge"      # 将文档、元数据、向量和文档 ID 存入 Chroma 的 equipment_knowledge 集合

#加载环境变量
ENV_DIR = BASE_DIR / ".env"
load_dotenv(dotenv_path= ENV_DIR)


def load_chunk_document (path: str| Path) -> list[Document]:
    path = Path(path)

    #检查路径是否存在
    if not path.is_file():
        raise FileNotFoundError(f"json文件路径不存在：{path.resolve()}")

    #加载json内容
    with path.open("r", encoding="utf-8") as f:
        records = json.load(f)
    
    #检查顶层是不是列表
    if not isinstance(records, list):
        raise TypeError("顶层不是列表")

    #创建一个空的列表documents
    documents: list[Document] = []

    for index, record in enumerate(records, start=1):
        #检查每一条记录是不是字典
        if not isinstance(record, dict):
            raise TypeError(f"第{index}条不是字典类型")

        if 'text' not in record:
            raise ValueError(f"第{index}条中不存在text")

        raw_text = record.get("text")
        if not isinstance(raw_text, str):
            raise TypeError(f"第{index}条中text不是str类型")

        text = str(raw_text)
        if not text.strip():
            continue

        raw_metadata = record.get("metadata",{})
        if not isinstance(raw_metadata, dict):
            raise TypeError(f"第{index}条的metadata不是字典类型")

        metadata = dict(raw_metadata)
        metadata.setdefault("source", "unknown")
        metadata.setdefault("chunk_id", f"{index:03d}")

        documents.append(
            Document(
                page_content=text,
                metadata =metadata
            )
        )

    if not documents:
        raise ValueError("没有输出任何有效的documents")

    chunk_ids = [str(document.metadata["chunk_id"]) for document in documents]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("chunk_id存在重复")

    return documents


#为向量数据库准备稳定 ID, 不同来源的文件会有001这样的chunk——id，因此将ID转成source + chunk_id来区别
def make_document_id(document:Document) -> str:
    source = str(document.metadata.get("source", "unknown"))
    chunk_id = str(document.metadata.get("chunk_id", "unknown"))
    return f"{source}::{chunk_id}"


#创建OpenAIEmbeddings对象
def create_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        #读取环境变量中的DASHSCOPE_EMBEDDING_MODEL，环境变量中没有时，默认为"qwen3.7-text-embedding"
        model=os.getenv(
            "DASHSCOPE_EMBEDDING_MODEL",
            "qwen3.7-text-embedding"
        ), 

        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_BASE_URL"),
        check_embedding_ctx_length=False,

    )

#创建chroma
def build_index() -> None:
    #加载documents
    documents = load_chunk_document(CHUNK_PATH)

    #创建id
    document_id = [
        make_document_id(document)
        for document in documents
    ]

    #embedding模型
    embeddings = create_embeddings()

    #创建chroma
    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        ids=document_id,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR)   #持久化chroma，退出之后embeddings数据还存在
    )

#加载chroma
def load_vector_store() -> Chroma:
    if not CHROMA_DIR.exists():
        raise FileNotFoundError("数据库不存在，请先保存数据库")

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=create_embeddings(), #用户问题还是普通字符串,因此需要传入embedding
        persist_directory=str(CHROMA_DIR)
    )

#创建检索retrivere
def retrieve_documents (ques:str, k:int=4 ) -> list[Document]:

    #根据用户的问题进行检索
    question = ques.strip()
    if not question:
        raise ValueError("问题不能为空")

    #加载之前创建好的chroma
    vector_store = load_vector_store()

    #包装成retrieve，vector_store是chroma对象，需要包装成retrieve
    retriever = vector_store.as_retriever(
        search_type = "similarity", #相似度检索
        search_kwargs = {"k":k}
    )
    return retriever.invoke(question)

#整理正下文
def format_documents(documents:list[Document]) -> str:
    sections : list[str] =[]

    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "unknown")
        chunk_id = document.metadata.get("chunk_id", "unknown")

        sections.append(
            f"[资料：{index}]\n"
            f"来源：{source}\n"
            f"文档块：{chunk_id}\n"
            f"内容：{document.page_content}"
        )
    return "\n\n".join(sections)

#创建回答提示词模板
# ChatPromptTemplate.from_messages()用于创建多条、带角色的消息模板
# ChatPromptTemplate.from_template()用于创建单条消息模板,默认把整段模板包装成一条 human 消息
ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个知识库问答助手。
只能依据参考资料回答。
资料不足时，明确说明知识库信息不足。
不得编造资料之外的信息。""".strip(),
        ),
        (
            "human",
            """
            参考资料：{context}
            
            用户问题：{question}
            """.strip(),
        ),
    ]
)

#创建聊天模型
def create_chat_model() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("DASHSCOPE_CHAT_MODEL"),
            api_key= os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL"),
            temperature=0

    )


#
def build_sources(documents:list[Document]) -> list[dict]:
    return [
        {
            "rank":rank,
            "source":document.metadata.get("source", "unknown"),
            "chunk_id":document.metadata.get("chunk_id", "unknown"),
            "content":document.page_content
        }
        for rank, document in enumerate(documents, start=1) 
    ]


#将步骤连接起来
def answer_question(question:str, k:int = 4) -> dict:
    question = question.strip()
    if not question:
        raise ValueError("输入不能为空")

    #第一步，从数据库中检索资料
    documents = retrieve_documents(question, k=k)
    if not documents:
        return {
            "question": question,
            "answer": "当前数据库没有检索到相关资料",
            "sources":[]

        }
    #第二步，把documents整理为当前字符串
    context = format_documents(documents)

    #第三步，把question，context填入prompt
    prompt_value = ANSWER_PROMPT.invoke({
        "question":question,
        "context": context
    })

    #第四步，调用Chat Model生成答案
    response = create_chat_model().invoke(prompt_value)

    #第五步，返回答案和检索来源
    return {
        "question":question,
        "answer":str(response.content),
        "sources":build_sources(documents)
    }



    








