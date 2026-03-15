# Hướng dẫn sử dụng Hệ thống Tìm kiếm Thông minh HUFLIT (TODO List)

Dưới đây là thứ tự các bước cần thực thi để cài đặt và vận hành hệ thống.

---

## Bước 1. Thiết lập môi trường

```powershell
# Tạo và kích hoạt môi trường ảo
python -m venv IR_HUFLIT
.\IR_HUFLIT\Scripts\activate

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# Tạo file cấu hình
copy .env.example .env
```

**Lưu ý:** Từ bây giờ mọi lệnh Python đều phải chạy trong môi trường ảo `IR_HUFLIT`. Mỗi khi mở terminal mới, nhớ chạy `.\IR_HUFLIT\Scripts\activate` trước.

---

## Bước 2. Crawl Data (Thu thập dữ liệu)

```powershell
# Bước 2.1: Chạy crawler để lấy HTML thô

Xem file CRAWL_AUTH_GUIDE.md

# Bước 2.2: Trích xuất thông tin từ HTML
python crawler/parser.py --input data/raw/ --output data/processed/corpus_raw.json

# Bước 2.3: Làm sạch và chuẩn hóa dữ liệu
python crawler/cleaner.py --input data/processed/corpus_raw.json --output data/processed/corpus.json
```

**Kết quả:** File `data/processed/corpus.json` chứa 193 tài liệu sạch.

---

## Bước 3. Xây dựng bộ chỉ mục (Build Index)

**Tại sao:** Chuyển đổi văn bản thô thành cấu trúc dữ liệu toán học (vector, inverted index) để tìm kiếm nhanh.

```powershell
# Bước 3.1: Build Sparse Index (TF-IDF, BM25, Inverted Index)
python indexer/build_index.py --corpus data/processed/corpus.json --output data/index/

# Bước 3.2: Build Dense Vector Index (FAISS + BGE-M3 embedding)
python indexer/vector_store.py --corpus data/processed/corpus.json
```

**Lưu ý quan trọng:** Bước 3.2 sử dụng model `BAAI/bge-m3` (2.27GB) nằm trong thư mục `models/bge_cache/`.
- Nếu lần đầu chạy trên Windows, hãy chạy `python repair_hf_cache.py` trước để sửa HuggingFace cache (do Windows không hỗ trợ symlink).
- Thời gian encoding: khoảng 5-6 phút (CPU). Sau khi xong, file `data/index/faiss_index.bin` sẽ được tạo.

---

## Bước 4. Kiểm tra bằng Terminal (Test Search)

**Tại sao:** Kiểm tra nhanh pipeline hoạt động đúng trước khi mở giao diện.

```powershell
# Chạy tìm kiếm KHÔNG có LLM (chỉ Phase 1 + Phase 2)
python test_search.py "Học phí HK2 khoá k29 là bao nhiêu?"

# Chạy tìm kiếm CÓ LLM (Phase 1 + Phase 2 + Phase 3 RAG)
python test_search.py "Học phí HK2 khoá k29 là bao nhiêu?" --use_llm
```

**Tham số tuỳ chỉnh:**
- `--top_k 5` : Số kết quả trả về (mặc định: 3)
- `--use_llm` : Bật sinh câu trả lời bằng Qwen2.5-7B Local

**Kết quả mong đợi:**
- Không `--use_llm`: Hiển thị danh sách tài liệu xếp hạng theo điểm.
- Có `--use_llm`: LLM tự động tổng hợp câu trả lời từ context + hiển thị nguồn tài liệu.

---

## Bước 5. Khởi chạy Backend API

**Tại sao:** Frontend cần gọi API backend để gửi câu hỏi và nhận kết quả.

```powershell
# Mở Terminal 1 (tại thư mục gốc dự án)
cd f:\huflit-ir-system
.\IR_HUFLIT\Scripts\activate
uvicorn api.main:app --reload --port 8000
```

⏳ **Quan trọng:** Đợi đến khi thấy `INFO: Application startup complete` (30-60 giây do nạp AI model vào RAM).

Kiểm tra API Swagger: http://localhost:8000/docs

---

## Bước 6. Khởi chạy Frontend (Giao diện Web)

```powershell
# Mở Terminal 2 (tại thư mục frontend)
cd f:\huflit-ir-system\frontend
python -m http.server 3000
```

🌐 Truy cập giao diện: **http://localhost:3000**

**Lưu ý:** Cả Backend (Bước 5) và Frontend (Bước 6) phải chạy **đồng thời** trên 2 terminal riêng biệt.

---

## Thông tin Model AI (Local - Offline 100%)

| Thành phần | Model | Kích thước | Vị trí |
|-----------|-------|-----------|--------|
| Embedding (Phase 2) | `BAAI/bge-m3` | 2.27 GB | `models/bge_cache/` |
| Cross-encoder (Phase 2) | `ms-marco-MiniLM-L-6-v2` | ~80 MB | `models/bge_cache/` |
| LLM sinh câu trả lời (Phase 3) | `Qwen2.5-7B-Instruct-Q4_K_M` | 4.3 GB | `models/Qwen2.5-7B-Instruct-Q4_K_M.gguf` |

**Toàn bộ model chạy Offline trên máy tính cá nhân, không cần API key hay internet.**

---

**Lưu ý:**
- Nếu dữ liệu (`corpus.json`) thay đổi, bạn **bắt buộc** phải chạy lại Bước 3 (Build cả Sparse + Dense Index).
- Trên Windows, nếu gặp lỗi model không load, chạy `python repair_hf_cache.py` để sửa HuggingFace cache trước.
- Lần đầu chạy `--use_llm`, hệ thống cần ~20-30 giây để nạp file GGUF 4.3GB vào RAM.
