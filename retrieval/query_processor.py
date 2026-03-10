import sys
from pathlib import Path

# Fix import path to access indexer/tokenizer.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from indexer.tokenizer import tokenize

# Danh sách từ đồng nghĩa cơ bản
SYNONYMS = {
    "tiền học": "học phí",
    "lịch thi": "lịch kiểm tra",
    "bài thi": "lịch thi",
    "đăng ký": "đk",
    "thanh toán": "đóng tiền"
}

def process_query(query):
    """
    Tiền xử lý query:
    1. Chuẩn hóa & mở rộng từ đồng nghĩa
    2. Tokenize (dùng chung logic với indexer)
    """
    if not query:
        return []
    
    # 1. Lowercase
    q = query.lower()
    
    # 2. Xử lý từ đồng nghĩa đơn giản
    for syn, target in SYNONYMS.items():
        if syn in q:
            q = q.replace(syn, target)
    
    # 3. Tokenize
    tokens = tokenize(q)
    
    return tokens

if __name__ == "__main__":
    test_q = "Tiền học học kỳ 2 năm 2024"
    print(f"Query: {test_q}")
    print(f"Processed: {process_query(test_q)}")
