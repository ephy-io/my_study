
import os
from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass


#给定项目的路径
#config.py是在src文件中，parents[1]是返回两层文件夹，也就是返回到my_rag文件夹的路径
PROJECT_PATH = Path(__file__).resolve().parents[1] 
DATA_PATH = PROJECT_PATH / "data"
OUTPUT_DATA = PROJECT_PATH / "output"
CHUNK_DATA = OUTPUT_DATA / "chunks.json"

load_dotenv(dotenv_path=PROJECT_PATH / ".env")

@dataclass(frozen= True)
class Config:
    #PDF类型识别
    text_pages_min_charact : int = 50  #去除空格后有 50 个字符说明是正常的页
    detect_sample_pages : int=8    #每一份pdf检查8页
    text_pdf_ratio : float = 0.7  #有大于70%的页里是可以提取文字的就是文字型PDF
    scan_pdf_ratio : float = 0.2  #有小于20%的是扫描型PDF

    #OCR
    ocr_zoom : float=2.0 #扫描型pdf提取文字时，要把pdf放大2倍
    ocr_min_confidence : float = 0.3  #最低置信度，低于30%说明不是文字，是噪声
    ocr_gpu : bool = False

    #数据清晰
    repeated_line_ratio : float = 0.6 #有60%的页 都出现重复，定义为页眉或页脚
    boundary_line_count : int=2 #检查前后两行是否重复

    #数据切分
    chunk_size : int=800
    chunk_overlap : int=120

    dashscope_api_key : str = os.getenv("DASHSCOPE_API_KEY", "")
    dashscope_base_url : str = os.getenv("DASHSCOPE_BASE_URL", "")
    embedding_model : str = os.getenv("DASHSCOPE_EMBEDDING_MODEL", "")
    chat_model : str = os.getenv("DASHSCOPE_CHAT_MODEL", "")

    #embedding的最大维度,一次处理多少条chunks
    embedding_dimension :int = 1024
    embedding_batch_size : int = 20

    qdrant_url : str = os.getenv("QDRANT_ URL", "http//localhost:6333")
    qdrant_key : str = os.getenv("QDRANT_KEY", "")

    qdrant_collection : str = "rag_chunks"

    retrieval_top_k : int = 5

    cros_origins : str = os.getenv("CROS_ORIGINS", "http//localhost:8501")
    

CONFIG = Config()

