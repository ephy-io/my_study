
#清洗数据的总体思路：
# 1、确定出标题和每一页的样式
# 2、将文本标准化，找出页眉页脚，判断是不是标题，将清晰好的文本进行拼接
# 3、清晰每一页的内容，清晰pdf的所有页
# 4、清洗表格中的一格，再清洗每一个表格，清洗全部表格

import math
import re
import unicodedata
from collections import Counter

from models import PageRecord, TableRecord, TabelRowsRecord
from config import CONFIG

#确定出标题的样式
HEADING_PATTERN =re.compile(
    r"^("     #从这一行开始
    r"第[一二三四五六七八九十百0-9]+[章节条]"     #第一章
    r"|[一二三四五六七八九十0-9]+、"            #1、
    r"|[（(]+[一二三四五六七八九十百0-9]+[）)]"     #（1）
    r"|\d+[.、]"        #23.  23、
    r"|附件\s*\d*"      # 附件 1
    r"|表\s*\d"         #表 1
    r")"        #结束
) 

#确定每一页的样式
PAGE_NUMBER_PATTERN = re.compile(
    r"^[—\-–]?\s*\d+\s*[—\-–]?$"
    r"|^第\s*\d+\s*页$"
)

#将每一句文本进行归一化
def normalize_unicode(text:str) -> str:
    text = unicodedata.normalize(
        "NFKC",
        text
    )
    text = text.replace("\u00a0"," ")
    text = text.replace("\u00ad", "")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    return text

#找出页眉页脚
def find_repeat_boundary_line(pages:list[PageRecord]) -> set[str]:

    #如果pdf页数小于三，判断不了
    if len(pages)<3:
        return set()

    counter : Counter[str] = Counter()  #counter是一个字典
    #遍历每一页的行
    for page in pages:
        lines = [
            line.strip()
            for line in normalize_unicode(page.text).splitlines()   #将每一页的内容进行统一标准化，然后按行分开
            if line.strip()     #将不为空的行加入
        ]

        count = CONFIG.boundary_line_count
        #取出前后的boundary_line_count行来判断页眉页脚
        boundary_lines = (lines[:count]+ lines[-count:])

        for line in set(boundary_lines):    #set()将重复的行去除
            if len(line) < 100:     #若果字数太多则不被判断为页眉页脚
                counter[line] += 1

        #计算阈值
    threshold = max(
            2,
            math.ceil(
                len(pages) * CONFIG.repeated_line_ratio   # math.ceil 是向上取整的意思
            )
        )

    return { 
        line
        for line , count in counter.items()
        if count >= threshold
    }

#判断是不是标题
def is_heading_line(line: str) -> bool:
    return bool(
        HEADING_PATTERN.match(line)
    )

#将文本重新拼接完整
def reflow_lines(lines:list[str]) -> str:

    #判断lines中是否有内容
    if not lines:
        return ""
    #创建一个空列表来放整理好的内容
    previous_lines = []
    
    #遍历每一个句子
    for line in lines:
        #判断列表是不是空，为空则直接加入到列表中
        if not previous_lines:
            previous_lines.append(line)
            continue

        #判断是不是标题
        if is_heading_line(line):
            previous_lines.append(line)
            continue

        #如果不是标题，则取出列表中的最后一个元素
        previous = previous_lines[-1]

        #再判断上一个元素是不是标题，是标题则直接将新的line加入到列表中
        if is_heading_line(previous):
            previous_lines.append(line)
            continue

        #判断列表中红的最后一个元素中是否带有结束的符号
        if re.search(
            r"[。！？；：.!?;:]$",
            previous
        ):
            previous_lines.append(line)
            continue
        #不是标题，且上一句没有结束标志，则认为跟上一句是同一句话，直接拼接在上一句的后面
        previous_lines[-1] = previous + line

    return "\n".join(previous_lines)

#清洗每一页的pdf内容
def clean_page_text(text:str, repeat_line:set[str]) -> str:
    #将text的文本先进行格式化
    text = normalize_unicode(text)

    #创建一个空的列表装清洗干净的文本
    clean_text : list[str] = []

    #遍历text文本中的每一行
    for line in text.splitlines():
        line = re.sub(
                    r"[ \t]+",
                    " ",
                    line
                ).strip()
        #判断空行
        if not line:
            continue
        #判断是不是标题
        if line in repeat_line:
            continue
        #判断是不是页码
        if PAGE_NUMBER_PATTERN.match(line):
            continue
       
        clean_text.append(line)

    return reflow_lines(clean_text).strip()

#清洗每一页内容
def clean_pages(pages:list[PageRecord]) -> list[PageRecord]:
    #找出每一页的页眉页脚
    repeat_line = find_repeat_boundary_line(pages)

    clean_pages : list[PageRecord] = []

    for page in pages:
        clean_page = clean_page_text(
            page.text,
            repeat_line
        )

        if not clean_page:
            continue

        clean_pages.append(
            PageRecord(
                page=page.page,
                text=clean_page,
                extraction_method=page.extraction_method
            )
        )
    return clean_pages

#清洗表格中的格子内容
def clean_tabel_cell(cell:str) -> str:
    text = normalize_unicode(cell)

    text = re.sub(
        r"\s+",
        " ",
        text
    )
    return text.strip()

#清洗整个表格
def clean_tabel(table:TableRecord) -> list[TabelRowsRecord]:
    #先清洗表格中的每一个格子
    rows = [
        [
            clean_tabel_cell(cell)
            for cell in row
        ]
        for row in table.rows
    ]

    #保存有内容的行
    rows = [
        row
        for row in rows
        if any(row)
    ]

    if len(rows) < 2:
        return []
    
    records : list[TabelRowsRecord] = []
    heads = rows[0]

    #清洗每一行
    for row_index, row in enumerate(rows[1:]):
        part: list[str] = []

        for clum_index, value in enumerate(row):
            if not value:
                continue
            if clum_index < len(heads) and heads[clum_index]:
                head = heads[clum_index]

            else:
                head = f"字段{clum_index + 1}"
            #将有内容的加入
            part.append( f"{head}: {value}")
        if not part:
            continue

        records.append(
            TabelRowsRecord(
                page= table.page,
                tabel_index=table.tabel_index,
                row_id=row_index,
                text=";".join(part)
            )
         )
    return records

#遍历清洗所有表格
def clean_tabls(tabels:list[TableRecord]) -> list[TabelRowsRecord]:
    rows = []

    previous_heads = None
    previous_page = None
    previous_tabel_index = None

    for tabel in tabels:

        first_row = (
            [clean_tabel_cell(cell) for cell in tabel.rows[0]]
            if tabel.rows else []
        )

        first_cell = first_row[0] if first_row else ""

        is_continuation = (
            previous_heads is not None
            and tabel.page == previous_page + 1
            and tabel.tabel_index == previous_tabel_index
            and re.fullmatch(r"\d+", first_cell)
            and len(first_row) == len(previous_heads)
        )

        if is_continuation:
            temp_tabel = TableRecord(
                page=tabel.page,
                tabel_index=tabel.tabel_index,
                rows=[previous_heads, *tabel.rows]
            )

            rows.extend(clean_tabel(temp_tabel))

        else:
            rows.extend(clean_tabel(tabel))

            if first_row:
                previous_heads = first_row

        previous_page = tabel.page
        previous_tabel_index = tabel.tabel_index

    return rows
 
                




    
