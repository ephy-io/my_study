
import hashlib
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CONFIG
from models import PageRecord, TabelRowsRecord,  PdfType

#创建字符切割器
def creat_text_spliter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size = CONFIG.chunk_size,
        chunk_overlap = CONFIG.chunk_overlap,
        separators = [
            r"\n(?=第[一二三四五六七八九十百0-9]+[章节条])",
            r"\n(?=[一二三四五六七八九十百0-9]+)",
            r"\n(?=[（(][一二三四五六七八九十百0-9]+[）)])",
            r"\n(?=\d+.、)",
            r"\n\n",
            r"\n",
            r"。",
            r"？",
            r"！",
            r"：",
            r"；",
            r"，",
            r""
        ],
        is_separator_regex = True
    )

#创建文本切割方法
def text_chunks(pages:list[PageRecord], source: str, pdf_typ:PdfType) -> list[Document]:
    #将文本转为Document类型
    pages_doucuments = [
        
            Document(
                page_content=page.text,
                metadata = {
                    "source":source,
                    "page":page.page,
                    "type": "text",
                    "pdf_type": pdf_typ,
                    "extract_method" : page.extraction_method
                    }
            )
        
        for page in pages
    ]

    #加载文本分割器
    spliter = creat_text_spliter()
    chunks = spliter.split_documents(pages_doucuments)

    return [
        chunk
        for chunk in chunks
        if chunk.page_content.strip()
    ]

#创建表格分割器
def tabel_chunks(rows:list[TabelRowsRecord], source: str, pdf_type:PdfType) -> list[Document]:
    return [ 
        Document(
            page_content= row.text,
            metadata = {
                "source":source,
                "type": "table",
                "pdf_type": pdf_type,
                "page": row.page,
                "table_index":row.tabel_index,
                "row_index":row.row_id
            }
        )
        for row in rows
        if row.text.strip() 
        ]
#创建chunk_id
def creat_chunk_id(doucument:Document) -> str:
    raw = "|".join(
        [
        str(
            doucument.metadata.get("source", "")
        ),
        str(
            doucument.metadata.get("page", "")
        ),
        str(
            doucument.metadata.get("type", "")
        ),
        doucument.page_content
        ]
    )
    return hashlib.sha256(
        raw.encode('utf-8')
    ).hexdigest()[:16]  #现将文本编码成utf-8，再使用sha256进行编码，再使用hexdigest将编码转换成人可以看见的编码，最后保留16位数

#最后再处理每一个document
def finalize_documents(documents: list[Document]) -> list[Document]:

    #定义一个空列表，放整理好的documents
    results : list[Document] = []

    #定义一个空集合，来去除重复的ids的documents
    seed_ids : set[str] = set()

    #遍历document列表
    for document in documents :
        seed_id = creat_chunk_id(document)

        if seed_id in seed_ids:
            continue

        seed_ids.add(seed_id)
        document.metadata["seed_id"] = seed_id

        document.metadata["chunk_len"] = len(document.page_content)

        results.append(document)

    return results


   
