
from dataclasses import dataclass
from typing import Literal

PdfType = [
    "text_pdf",
    "scan_pdf",
    "mix_pdf"
]


#每一页的记录
@dataclass
class PageRecord:
    page : int   #页码
    text : str   #内容
    ectraction_method : Literal["text", "orc"]   #提取内容的方法

#每一个表格的记录
@dataclass
class TableRecord:
    page: int  #表格在哪一页
    tabel_index: int  #这一页的第几个表格
    rows: list[list[str]] #整张表的行和列的记录

#每一个表中买一行的记录  
@dataclass
class TabelRowsRecord:
    page: int
    tabel_index:int
    row_id : int   #第几行
    text : str
    
    