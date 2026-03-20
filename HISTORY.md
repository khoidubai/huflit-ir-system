# Lịch sử cập nhật dự án (Update History)

Dưới đây là nhật ký chi tiết các thay đổi và tiến độ triển khai của hệ thống HUFLIT IR.

## [2026-01-10] - Cài đặt cơ bản & Triển khai Phase 1

### 09:37 - Khởi tạo Hướng dẫn sử dụng
- **File mới:** `TODO.md`
- **Nội dung:** Viết hướng dẫn 6 bước triển khai hệ thống từ cài đặt môi trường đến chạy API/Frontend.

### 18:22 - Cấu hình Git & GitHub
- **File mới:** `.gitignore`
- **Nội dung:** Loại bỏ các file rác, môi trường ảo (`IR_HUFLIT/`), dữ liệu thô (`data/raw/`), và các file chỉ mục nhị phân.

### 18:30 -> 21:00 - Triển khai Crawler & Xử lý dữ liệu
- **File cập nhật/mới:**
    - `requirements.txt`: Thêm các thư viện `requests`, `beautifulsoup4`, `lxml`, `underthesea`, `scikit-learn`, `rank-bm25`.
    - `crawler/config.py`, `spider.py`, `parser.py`, `cleaner.py`.
- **Kết quả:** Thu thập thành công **211 file HTML** và xử lý ra **193 tài liệu sạch** tại `data/processed/corpus.json`.

---

## [2026-03-06] - Đánh index và triển khai phase 1

### 21:40 -> 22:14 - Triển khai Indexer (Core IR)
- **File mới:** `tokenizer.py`, `inverted_index.py`, `tfidf.py`, `bm25.py`, `build_index.py`.
- **Kết quả:** Xuất các file chỉ mục tại `data/index/`.

### 22:30 -> 22:45 - Triển khai Retrieval (Bộ não Phase 1)
- **File mới:** `query_processor.py`, `ranked_retrieval.py`, `hybrid_ranker.py`, `test_search.py`.
- **Kết quả:** Hệ thống có khả năng tìm kiếm cơ bản.

---

## [2026-03-10] - Triển khai Advanced RAG Pipeline (Local Models)

### 08:08 - Sắp xếp lại Cây Thư Mục & Pipeline làm việc

### 08:15 → 22:45 - Phase 1: Lexical Retrieval Refactoring
- **Cập nhật:** Tối ưu hóa Lexical Scorer để trả về top-K candidates phục vụ RRF merge.

---

## [2026-03-14] - Tiếp tục triển khai Phase 2
### 08:45 → 09:10 - Phase 2: Hybrid Retrieval & Re-ranking
- **Mới:** Triển khai Dense Retrieval (BGE-M3 + FAISS), RRF Merger, và Cross-encoder Reranker.
- **Kết quả:** Pipeline Phase 2 hoàn chỉnh (Dense + Sparse).

### 09:10 → 11:25 - Phase 3: RAG (Retrieval-Augmented Generation)
- **Mới:** Triển khai Local LLM (Qwen2.5-7B GGUF) qua `llama-cpp-python`.
- **Kết quả:** Hệ thống sinh câu trả lời tự động từ dữ liệu nội bộ.

### 13:10 → 13:40 - API Backend & Frontend
- **Mới:** FastAPI Backend endpoint và giao diện người dùng SPA hiện đại.
- **Kết quả:** Người dùng có thể tìm kiếm qua giao diện web tại `http://localhost:3000`.

### 13:45 → 20:00 - Chuyển đổi sang Local Models (Offline 100%)
- **Thay đổi:** Loại bỏ hoàn toàn Cloud API (Gemini), chuyển sang chạy thuần local với BGE-M3 và Qwen2.5.
- **Kết quả:** Đảm bảo bảo mật dữ liệu và không phụ thuộc internet.

### 20:00 → 20:50 - Xử lý lỗi Windows HF Cache (Broken Symlinks)
- **Giải pháp:** Viết `repair_hf_cache.py` để sửa lỗi pointer file của HuggingFace trên Windows.
- **Kết quả:** Rebuild FAISS index thành công. Hệ thống chạy 100% Offline.

---

## [2026-03-15] - Fix Search Quality: Tokenization + Title Boosting + Dense ID Mapping

### 07:37 → 10:15 - Sửa 3 lỗi ảnh hưởng chất lượng tìm kiếm

#### Bug 1 (Critical): `dense_doc_ids.json` toàn giá trị `null`
- **File:** `indexer/vector_store.py` (dòng 37)
- **Nguyên nhân:** Khi build FAISS vector index, code dùng `doc.get('url')` làm doc_id nhưng trả về `null` cho toàn bộ 193 tài liệu. Trong khi đó, Lexical Retrieval (`build_index.py`) và `test_search.py` đều dùng format `huflit_XXXX`.
- **Hậu quả:**
  - Dense Retrieval (semantic search bằng BGE-M3) trả về 20 kết quả nhưng tất cả đều có `doc_id = null`.
  - RRF Merger không thể fuse kết quả giữa Lexical và Dense vì cùng 1 tài liệu có 2 ID khác nhau (`huflit_0001` vs `null`).
  - Cross-Encoder Reranker gọi `corpus_metadata.get(null)` → trả về `None` → **toàn bộ kết quả semantic bị drop âm thầm**, chỉ còn lexical results sống sót.
- **Fix:** Đổi `doc.get('url', f'doc_{idx}')` → `doc.get('id', f"huflit_{idx+1:04d}")` để đồng bộ format ID với toàn bộ pipeline. Regenerate file `data/index/dense_doc_ids.json` với 193 ID đúng format.

#### Bug 2 (High): Tokenization mismatch giữa query và document
- **File:** `indexer/tokenizer.py` (dòng 34-47)
- **Nguyên nhân:** Thư viện `underthesea` tách từ tiếng Việt theo ngữ cảnh, dẫn đến cùng một cụm từ nhưng bị tách khác nhau:
  - Query `"tích điểm rèn luyện"` → tokens: `tích_điểm`, `rèn_luyện`
  - Document title `"[Điểm rèn luyện]"` → tokens: `điểm`, `rèn_luyện`
  - Token `tích_điểm` ≠ `điểm` → **BM25 và TF-IDF không match được**, chỉ có `rèn_luyện` là khớp.
- **Hậu quả:** Các tài liệu có title chứa "[Điểm rèn luyện]" bị xếp hạng thấp do thiếu token match, dù nội dung hoàn toàn liên quan.
- **Fix:** Thêm **Unigram Fallback** — khi tokenizer tạo compound token (chứa `_`), tự động tách thêm các từ đơn. VD: `tích_điểm` → giữ nguyên `tích_điểm` + thêm `tích` và `điểm`. Áp dụng cho cả indexing lẫn query processing (vì dùng chung hàm `tokenize()`).

#### Bug 3 (Medium): Không ưu tiên kết quả match title
- **File:** `indexer/build_index.py` (dòng 43-48)
- **Nguyên nhân:** Khi build index, title và content được nối thành 1 chuỗi rồi tokenize chung (`f"{title} {content}"`). Không có cơ chế trọng số → 1 lần xuất hiện từ khóa trong title có cùng trọng số với 1 lần trong content.
- **Hậu quả:** Tài liệu có title "[Điểm rèn luyện]" bị xếp ngang hàng với tài liệu chỉ nhắc thoáng qua "điểm rèn luyện" trong nội dung dài.
- **Fix:** **Title Boosting** — tokenize title riêng, lặp lại 3 lần rồi nối với content tokens: `title_tokens * 3 + content_tokens`. Cách này tự nhiên tăng TF (term frequency) của title tokens trong BM25/TF-IDF mà không cần thay đổi công thức ranking hay cấu trúc index.

### Kết quả sau khi fix

| Trước fix | Sau fix |
|-----------|---------|
| Top 1: "Thông báo kết quả xét tốt nghiệp đợt 1 năm 2023" (score: 0.91) | Top 1: "[Điểm rèn luyện] Hoạt động Tư vấn nghề nghiệp - HUFLIT Career Bootcamp 01/2026" (score: 4.34) |
| Top 2: "GIA HẠN - Khảo sát Chất lượng giảng dạy" (score: -0.41) | Top 2: "[Điểm rèn luyện] Tích lũy điểm rèn luyện khi đăng ký HUFLIT Career Bootcamp 10/2025" (score: 4.29) |
| Top 3: "THÔNG BÁO VỀ VIỆC HỖ TRỢ THÔNG TIN SINH VIÊN" (score: -1.31) | Top 3: "[Điểm rèn luyện] Hoạt động Tư vấn nghề nghiệp - HUFLIT Career Bootcamp 10/2025" (score: 4.08) |

### Lưu ý
- Đã rebuild Sparse Index (`data/index/`): inverted_index, TF-IDF matrix, BM25 params, doc_ids, doc_lengths.
- Đã regenerate `dense_doc_ids.json`. FAISS vectors (embeddings) không cần rebuild vì BGE-M3 encode từ raw text, không phụ thuộc tokenizer.
- Nếu sau này chạy lại `vector_store.py`, code đã được sửa để dùng đúng format ID.

---



## [2026-03-17] - Bổ sung Date và Category vào dataset


---




*Cập nhật lần cuối: 08:15, 20/03/2026*
