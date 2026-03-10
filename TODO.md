# Hướng dẫn sử dụng Hệ thống Tìm kiếm Thông minh HUFLIT (TODO List)

Dưới đây là thứ tự các bước cần thực thi để cài đặt và vận hành hệ thống.

## 1. Thiết lập môi trường

# Tạo và kích hoạt môi trường ảo
python -m venv IR_HUFLIT
.\IR_HUFLIT\Scripts\activate

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# Tạo file cấu hình từ bản mẫu
copy .env.example .env

## 2. Thu thập dữ liệu (Crawl Data)

```powershell
# Bước 2.1: Chạy crawler để lấy HTML thô
python crawler/spider.py --start-url https://portal.huflit.edu.vn --max-pages 500

# Bước 2.2: Trích xuất thông tin từ HTML
python crawler/parser.py --input data/raw/ --output data/processed/corpus_raw.json

# Bước 2.3: Làm sạch và chuẩn hóa dữ liệu
python crawler/cleaner.py --input data/processed/corpus_raw.json --output data/processed/corpus.json
```

## 3. Xây dựng bộ chỉ mục (Build Index)
**Tại sao:** Chuyển đổi văn bản thô thành cấu trúc dữ liệu toán học (vector, inverted index) để tìm kiếm nhanh.

```powershell
python indexer/build_index.py --corpus data/processed/corpus.json --output data/index/
```

## 4. Khởi chạy Backend API
**Tại sao: để Frontend có thể gửi câu hỏi và nhận kết quả.**

```powershell
uvicorn api.main:app --reload --port 8000
```
*Kiểm tra tại: http://localhost:8000/docs*

## 5. Khởi chạy Giao diện (Frontend)

```powershell
cd frontend
python -m http.server 3000
```
*Truy cập: http://localhost:3000*

---

## Tích hợp model LLM (Phase 2)
**Tại sao:** Để hệ thống không chỉ trả về link mà còn tự viết câu trả lời thông minh.

1. Mở file `.env`, đặt `LLM_ENABLED=true` và thêm `API_KEY`. -> khúc này sẽ bàn bạc chọn model xử lí sau
2. Chạy index cho vector store (Semantic Search):
```powershell
python indexer/vector_store.py --corpus data/processed/corpus.json
```

---
**Lưu ý:** Nếu dữ liệu (corpus.json) thay đổi, bạn **bắt buộc** phải chạy lại Bước 3 (Build Index).
