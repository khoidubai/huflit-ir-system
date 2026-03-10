# Lịch sử cập nhật dự án (Update History)

Dưới đây là nhật ký chi tiết các thay đổi và tiến độ triển khai của hệ thống HUFLIT IR.

## [2026-03-10] - Cài đặt cơ bản & Hoàn tất Phase 1

### 🕒 09:37 - Khởi tạo Hướng dẫn sử dụng
- **File mới:** `TODO.md`
- **Nội dung:** Viết hướng dẫn 6 bước triển khai hệ thống từ cài đặt môi trường đến chạy API/Frontend. Giải thích lý do ("Tại sao") cho từng bước.

### 🕒 18:22 - Cấu hình Git & GitHub
- **File mới:** `.gitignore`
- **Nội dung:** Loại bỏ các file rác, môi trường ảo (`IR_HUFLIT/`), dữ liệu thô (`data/raw/`), và các file chỉ mục nhị phân để chuẩn bị đẩy code lên GitHub.

### 🕒 18:30 -> 21:00 - Triển khai Crawler & Xử lý dữ liệu
- **File cập nhật/mới:**
    - `requirements.txt`: Thêm các thư viện `requests`, `beautifulsoup4`, `lxml`, `underthesea`, `scikit-learn`, `rank-bm25`.
    - `crawler/config.py`: Cấu hình URL seed, đường dẫn lưu data và các category.
    - `crawler/spider.py`: Script thu thập dữ liệu tự động.
    - `crawler/parser.py`: Trích xuất thông tin (title, content, url) từ HTML.
    - `crawler/cleaner.py`: Làm sạch text, chuẩn hóa và loại bỏ văn bản quá ngắn.
    - `STEP_BY_STEP.md`: Ghi lại các câu lệnh thực thi nhanh.
- **Kết quả:** Thu thập thành công **211 file HTML** và xử lý ra **193 tài liệu sạch** tại `data/processed/corpus.json`.

### 🕒 21:40 -> 22:14 - Triển khai Indexer (Core IR)
- **File mới:**
    - `indexer/tokenizer.py`: Bộ tách từ tiếng Việt dùng `underthesea`, hỗ trợ lọc stopword.
    - `indexer/inverted_index.py`: Xây dựng chỉ mục đảo ngược (Inverted Index) để tìm kiếm từ khóa.
    - `indexer/tfidf.py`: Tính toán ma trận TF-IDF (Vector Space Model).
    - `indexer/bm25.py`: Tính toán tham số xếp hạng BM25.
    - `indexer/build_index.py`: Script tổng hợp chạy toàn bộ quy trình đánh chỉ mục.
- **Kết quả:** 
    - Cài đặt thành công môi trường ảo `IR_HUFLIT`.
    - Chạy thành công Indexer cho 193 tài liệu.
    - Xuất các file chỉ mục tại `data/index/`: `inverted_index.pkl`, `tfidf_matrix.npz`, `bm25_params.json`, `vocab.json`.
    - Kích thước từ vựng đạt: **1957 từ**.

### 🕒 22:30 -> 22:45 - Triển khai Retrieval (Bộ não Phase 1)
- **File mới:**
    - `retrieval/query_processor.py`: Xử lý câu hỏi, hỗ trợ mở rộng từ đồng nghĩa (synonyms).
    - `retrieval/ranked_retrieval.py`: Nạp Index và thực hiện tính điểm theo TF-IDF Cosine Similarity và BM25.
    - `retrieval/hybrid_ranker.py`: Thuật toán xếp hạng lai (0.3 TF-IDF + 0.4 BM25).
    - `test_search.py`: Script kiểm tra tìm kiếm ngay trên terminal.
- **Cập nhật:**
    - `indexer/build_index.py`: Lưu thêm mapping `doc_ids.json` và `doc_lengths.json` để phục vụ việc truy xuất chính xác.
- **Kết quả:** Hệ thống đã có khả năng tìm kiếm cơ bản dựa trên bộ chỉ mục đã xây dựng.

---
*Cập nhật lần cuối: 22:45, 10/03/2026*
