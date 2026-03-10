""" 
Chứa: danh sách URL seed ban đầu, URL blacklist pattern (tránh crawl file PDF/ảnh/login), User-Agent header, CRAWL_DELAY, MAX_PAGES, MAX_DEPTH, timeout settings.
"""

from pathlib import Path

# ==============================
# BASE SETTINGS
# ==============================

BASE_URL = "https://portal.huflit.edu.vn"

USER_AGENT = "HUFLIT-Crawler/1.0 (Educational Purpose)"

CRAWL_DELAY = 2  # seconds
TIMEOUT = 15

MAX_PAGES = 500
MAX_DEPTH = 3


# ==============================
# DATA PATHS
# ==============================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ==============================
# CATEGORY CONFIG
# ==============================

CATEGORIES = {
    "thong_bao_chung": 1,
    "ke_hoach_nam_hoc": 1012,
    "quy_dinh_quy_che": 1013,
    "thong_bao_phong_dao_tao": 1014,
    "thong_bao_ctsv": 1015,
}


# ==============================
# URL FILTERS
# ==============================

BLACKLIST_PATTERNS = [
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".jpg",
    ".png",
]


# ==============================
# HEADERS
# ==============================

HEADERS = {
    "User-Agent": USER_AGENT
}