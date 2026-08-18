import json
import logging
from langchain_core.documents import Document
from pipeline import process_all_pdfs
from chunker import finalize_documents

from config import  DATA_PATH, OUTPUT_DATA, CHUNK_DATA

logging.basicConfig(
    level= logging.INFO,
    format= ("%(asctime)s | "
        "%(levelname)s | "
        "%(message)s")
)

logger = logging.getLogger(__name__)

#处理所有的pdf
def process_pdfs () -> list[Document]:
    pdf_files = sorted(
        DATA_PATH.glob("*.pdf")  #找到所有的pdf， 并且进行排序，以便后面按顺序处理
    )

    print("DATA_PATH =", DATA_PATH)
    print("pdf_files =", pdf_files)

    if not pdf_files:
        raise FileNotFoundError(f"找不到任何的pdf{DATA_PATH}") 

    #创建一个列表，放处理好之后的chunks
    all_chunks: list[Document] = []
    for pdf_file in pdf_files:
        try:
            logger.info("开始处理：%s", pdf_file.name)

            pdf_type, chunks = process_all_pdfs(pdf_file)

            #将得到的chunks加入到all_chunks列表中
            all_chunks.extend(chunks)

            logger.info(
                "处理完成：%s | pdf类型:%s | Chunk:%d",
                pdf_file.name, pdf_type, len(chunks)
            )

        except Exception:
            logger.exception("处理失败：%s", pdf_file.name)
    return finalize_documents(all_chunks)

#把all_chunks储存起来
def save_chunk(documents: list[Document]) -> None:
    OUTPUT_DATA.mkdir(
        parents= True,
        exist_ok= True
    )

    data = [
        {
            "page_content" : document.page_content,
            "metadata": document.metadata
        }
        for document in documents
    ]
    with CHUNK_DATA.open("w", encoding='utf-8') as f:
        json.dump(
            data, f, ensure_ascii=False, indent=2
        )
    logger.info("已经全部完成: %s, 一共保存%d个chunk", OUTPUT_DATA, len(data))

#定义主程序
def main() -> None:
    documents = process_pdfs()
    save_chunk(documents)

if __name__ == "__main__":
    main()
