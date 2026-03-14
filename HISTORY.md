# Lịch sử cập nhật dự án (Update History)

Dưới đây là nhật ký chi tiết các thay đổi và tiến độ triển khai của hệ thống HUFLIT IR.

## [2026-01-10] - Cài đặt cơ bản & Hoàn tất Phase 1

### 🕒 09:37 - Khởi tạo Hướng dẫn sử dụng
- **File mới:** `TODO.md`
- **Nội dung:** Viết hướng dẫn 6 bước triển khai hệ thống từ cài đặt môi trường đến chạy API/Frontend.

### 🕒 18:22 - Cấu hình Git & GitHub
- **File mới:** `.gitignore`
- **Nội dung:** Loại bỏ các file rác, môi trường ảo (`IR_HUFLIT/`), dữ liệu thô (`data/raw/`), và các file chỉ mục nhị phân.

### 🕒 18:30 -> 21:00 - Triển khai Crawler & Xử lý dữ liệu
- **File cập nhật/mới:**
    - `requirements.txt`: Thêm các thư viện `requests`, `beautifulsoup4`, `lxml`, `underthesea`, `scikit-learn`, `rank-bm25`.
    - `crawler/config.py`, `spider.py`, `parser.py`, `cleaner.py`.
- **Kết quả:** Thu thập thành công **211 file HTML** và xử lý ra **193 tài liệu sạch** tại `data/processed/corpus.json`.

### 🕒 21:40 -> 22:14 - Triển khai Indexer (Core IR)
- **File mới:** `tokenizer.py`, `inverted_index.py`, `tfidf.py`, `bm25.py`, `build_index.py`.
- **Kết quả:** Xuất các file chỉ mục tại `data/index/`.

### 🕒 22:30 -> 22:45 - Triển khai Retrieval (Bộ não Phase 1)
- **File mới:** `query_processor.py`, `ranked_retrieval.py`, `hybrid_ranker.py`, `test_search.py`.
- **Kết quả:** Hệ thống có khả năng tìm kiếm cơ bản.

---

## [2026-03-14] - Triển khai hoàn chỉnh Advanced RAG Pipeline (Local Models)

### 🕒 08:08 - Sắp xếp lại Cây Thư Mục & Pipeline làm việc

### 🕒 08:15 → 08:45 - Phase 1: Lexical Retrieval Refactoring
- **Cập nhật:** Tối ưu hóa Lexical Scorer để trả về top-K candidates phục vụ RRF merge.

### 🕒 08:45 → 09:10 - Phase 2: Hybrid Retrieval & Re-ranking
- **Mới:** Triển khai Dense Retrieval (BGE-M3 + FAISS), RRF Merger, và Cross-encoder Reranker.
- **Kết quả:** Pipeline Phase 2 hoàn chỉnh (Dense + Sparse).

### 🕒 09:10 → 09:25 - Phase 3: RAG (Retrieval-Augmented Generation)
- **Mới:** Triển khai Local LLM (Qwen2.5-7B GGUF) qua `llama-cpp-python`.
- **Kết quả:** Hệ thống sinh câu trả lời tự động từ dữ liệu nội bộ.

### 🕒 09:25 → 09:40 - API Backend & Frontend
- **Mới:** FastAPI Backend endpoint và giao diện người dùng SPA hiện đại.
- **Kết quả:** Người dùng có thể tìm kiếm qua giao diện web tại `http://localhost:3000`.

### 🕒 09:45 → 10:00 - Chuyển đổi sang Local Models (Offline 100%)
- **Thay đổi:** Loại bỏ hoàn toàn Cloud API (Gemini), chuyển sang chạy thuần local với BGE-M3 và Qwen2.5.
- **Kết quả:** Đảm bảo bảo mật dữ liệu và không phụ thuộc internet.

### 🕒 10:00 → 10:50 - Xử lý lỗi Windows HF Cache (Broken Symlinks)
- **Giải pháp:** Viết `repair_hf_cache.py` để sửa lỗi pointer file của HuggingFace trên Windows.
- **Kết quả:** Rebuild FAISS index thành công. Hệ thống chạy 100% Offline.

---
*Cập nhật lần cuối: 11:10, 14/03/2026*
