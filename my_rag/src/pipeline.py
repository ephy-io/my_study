from pathlib import Path
from langchain_core.documents import Document
from models import PdfType
from pdf_parser import detect_pdf_type, extract_pages, extract_tabel
from cleaner import clean_pages, clean_tabls
from chunker import text_chunks, tabel_chunks, finalize_documents

#把前面的解析pdf，清洗pdf，切块pdf这些程序链接在一起
def process_all_pdfs(path: Path) -> tuple[PdfType, list[Document]]:
    #判断pdf类型
    pdf_type = detect_pdf_type( path)

    #提取页文本内容和表格内容
    raw_texts_content = extract_pages(path, pdf_type)
    raws_tabels_content = extract_tabel(path, pdf_type)

    #清晰文本和表格内容
    clean_text_content = clean_pages(raw_texts_content)
    clean_tabel_content = clean_tabls(raws_tabels_content)

    #切块
    text_chunk = text_chunks(clean_text_content, path.name, pdf_type )
    tabel_chunk = tabel_chunks(clean_tabel_content, path.name, pdf_type)

    #整理最后的chunk
    final_chunk = finalize_documents(text_chunk + tabel_chunk)

    return pdf_type, final_chunk

