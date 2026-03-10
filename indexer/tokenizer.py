import re
from underthesea import word_tokenize

# Danh sách stopword cơ bản (có thể mở rộng sau)
STOPWORDS = {
    "và", "của", "là", "các", "những", "cho", "trong", "được", "có", "với", 
    "một", "theo", "tại", "này", "về", "cũng", "đã", "đang", "sẽ", "đó", 
    "khi", "như", "này", "với", "từ", "lại", "thì", "mà", "nhưng", "nếu", 
    "thế", "cái", "con", "mình", "nên", "vậy", "rằng", "bởi", "vì", "qua"
}

def tokenize(text):
    """
    Tiền xử lý văn bản:
    1. Lowercase
    2. Tách từ bằng underthesea
    3. Loại bỏ ký tự đặc biệt
    4. Loại bỏ stopwords
    """
    if not text:
        return []

    # Lowercase
    text = text.lower()

    # Xóa ký tự đặc biệt (giữ lại khoảng trắng)
    text = re.sub(r'[^\w\s]', ' ', text)

    # Tách từ
    tokens = word_tokenize(text)

    # Làm sạch: bỏ khoảng trắng thừa, bỏ stopwords, bỏ token quá ngắn
    # Chú ý: underthesea tách từ có thể chứa dấu gạch dưới (vd: đại_học)
    clean_tokens = [
        t.replace(' ', '_') for t in tokens 
        if t.strip() and t.strip() not in STOPWORDS and len(t.strip()) > 1
    ]

    return clean_tokens

if __name__ == "__main__":
    test_text = "Trường Đại học Ngoại ngữ - Tin học TP.HCM thông báo tuyển sinh năm 2024."
    print(f"Original: {test_text}")
    print(f"Tokens: {tokenize(test_text)}")
