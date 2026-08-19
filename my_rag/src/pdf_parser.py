
# 提取pdf中的文本整体思路：
# 1、确保计算有效字符数的函数，确定判断pdf类型时需要的具体页码函数， 判断pdf类型
# 2、创建ocr的文本提取器， 确定ocr提取文本的函数
# 3、确定提取pdf每一页内容的函数， 确定提取表格内容的函数

from pathlib import Path
import easyocr 
import numpy as np
import pdfplumber
import pymupdf

from config import CONFIG
from models import  PdfType, PageRecord, TableRecord

_ocr_loader:easyocr.Reader | None = None

#计算有效的字符数,接受text的str，返回字符数int
def count_effective_charact(text:str) -> int:
    return len("".join(text.strip()))

#确定出需要检查的页码,输入全部的页数，返回需要检查的具体页码
def sample_page_indices(total_pages:int) -> list[int]:

    #判断pdf的总页数，少于指定的页码数，pdf的每一页都要检查
    if total_pages <= CONFIG.detect_sample_pages:
        return list(range(total_pages))

    #计算出挑选页码的步数step
    step = (
        (total_pages - 1) / (CONFIG.detect_sample_pages)
    )
    return sorted(
        {
            round(index * step)   #round()：取最接近的整数；如果刚好是 .5，则取左右两个整数中的偶数
            for index in range(CONFIG.detect_sample_pages)
        }   #使用{}作用是去重，删掉重复的页码
    )

#判断pdf的类型
def detect_pdf_type( pdf_path: Path) -> PdfType:

    #打开文件，确定出需要检查的页码
    with pymupdf.open(pdf_path) as doc:
        page_indices = sample_page_indices(doc.page_count)
        if not page_indices:
            return "scan_pdf"

        vaild_text_pages = 0
        for page_index in page_indices:

            #读取page_index这一页
            page = doc.load_page(page_index)

            #提取这一页的文本text
            text = page.get_text("text").strip()  #text是设定的参数，按照纯文本模式提取文字

            #计算这一页的字数
            char_count = count_effective_charact(text)

            if char_count >= CONFIG.text_pages_min_charact:
                vaild_text_pages += 1
    text_radio = vaild_text_pages / len(page_indices)

    if text_radio >= CONFIG.text_pdf_ratio:
        return "text_pdf"
    if text_radio <= CONFIG.scan_pdf_ratio:
        return "scan_pdf"

    return "mix_pdf"

#创建一个可复用的easyocr.reader文本提取器
def get_ocr_reader() -> easyocr.Reader:
    global _ocr_loader

    if _ocr_loader is None:
        _ocr_loader = easyocr.Reader(
            ["ch_sim", "en"],
            gpu = CONFIG.ocr_gpu
        )
    return _ocr_loader

#使用OCR提取扫描版pdf的文本
#思路：把一页扫描 PDF 转成图片 → 用 EasyOCR 识别文字 → 过滤低质量结果 → 按阅读顺序排序 → 拼成最终文本。
def ocr_page(page: pymupdf.Page) -> str:    #接受一页pdf，返回text内容

    #将pdf放大
    matrix = pymupdf.Matrix(
        CONFIG.ocr_zoom,
        CONFIG.ocr_zoom
    )

    #将pdf转换为图片, page.get_pixmap()将pdf页渲染成图片
    pixmap = page.get_pixmap(   
        matrix = matrix,
        alpha= False, #不要透明通道
    )

    #把 PyMuPDF 的图片数据，转换成 EasyOCR 能读取的 NumPy 图片数组。
    image = np.frombuffer(
        pixmap.samples,    #图片原始像素数据
        dtype= np.uint8,    #每个像素数值使用 0～255 的整数格式
    ).reshape(           #重新整理成 高度 × 宽度 × 通道数
        pixmap.height,
        pixmap.width,
        pixmap.n
    )

    #获取get_ocr_reader模型,获取 EasyOCR 识别器
    ocr_reader = get_ocr_reader()

    #识别图片里的文字
    results = ocr_reader.readtext(
        image= image,
        detail = 1,  #返回文字，文字位置，文字置信度等详细信息
        paragraph= False    #不让 EasyOCR 自动把内容合并成大段落
    )
    #去除置信度低的结果
    vaild_results = [
        result
        for result in results
        if result[2] >= CONFIG.ocr_min_confidence
    ]

    #对有效的结果进行排序
    # lambda 参数: 返回值
#     result = [
#     [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],  # 文字框坐标
#     "识别出的文字",
#     0.95]

    vaild_results.sort(
        key = lambda result: (
            result[0][0][1],  #取出y1
            result[0][0][0],    #取出x1
        )
    )

    lines = [
        result[1].strip()    # result[位置 , 文字 , 置信度]中result[1]是提取文字
        for result in vaild_results
        if result[1].strip()
    ]
    return "\n".join(lines)  #将内容拼在一起并返回

#提取pdf中每一页的内容
def extract_pages(pdf_path:Path, pdf_type:PdfType) -> list[PageRecord]:

    pages: list[PageRecord] = []

    #打开pdf文件
    with pymupdf.open(pdf_path) as doc:
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)

            #获取这一页pdf的文本
            direct_text = page.get_text('text').strip()

            #判断pdf类型，以使用不同方法提取文字
            if pdf_type == "scan_pdf":
                use_ocr = True

            elif pdf_type == "mix_pdf":
                use_ocr = (
                    count_effective_charact(direct_text) < CONFIG.text_pages_min_charact
                )
            else:
               use_ocr = False

            if use_ocr:
                text = ocr_page(page)
                extract_methond = "ocr"
            else:
                text = direct_text
                extract_methond = "text"
            #把pdf处理方法做一个记录，放到一个列表中
            pages.append(
                PageRecord(
                    page = page_index + 1,
                    text = text,
                    extraction_method= extract_methond
                )
            )
    return pages

#提取表格内容
def extract_tabel(pdf_path:Path, pdf_type:PdfType) -> list[TableRecord]:
    if PdfType == "scan_pdf":
        return []
    records: list[TableRecord] = []

    #打开pdf文件
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_index, page in enumerate(pdf.pages):
            tabels = page.extract_tables()

            #处理这一页中的所有表格
            for tabel_index, tabel in enumerate(tabels):
                if not tabel:
                    continue
                rows = [
                    [
                        cell if cell is not None else ""
                        for cell in row
                    ]
                    for row in tabel
                    if row
                ]
                records.append(
                    TableRecord(
                        page= page_index + 1,
                        tabel_index= tabel_index,
                        rows= rows
                    )
                )
    return records

                