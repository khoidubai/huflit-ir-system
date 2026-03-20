# Hướng phát triển (Advanced Metadata & Hybrid Retrieval)

Dựa trên cấu trúc lý tưởng từ file `CauTrucDataSet.md`, dataset đã được nâng cấp thêm 2 trường metadata: `category` và `date`. File `corpus_new.json` hiện có 193 docs với schema: `{id, title, content, url, category, date}`. Áp dụng các kỹ thuật tinh gọn và chống ảo giác (Zero Hallucination) => hiệu quả hơn.

## Mục tiêu
- Tối ưu hóa chất lượng trả lời thông tin cho sinh viên HUFLIT
- Tăng độ chính xác và độ tin cậy của kết quả tìm kiếm
- Giảm thời gian xử lý và chi phí tính toán

Dưới đây là kế hoạch khai thác 2 trường mới này:

---

## Phần 1: Các Tính Năng Có Thể Khai Thác

### 1. Hard-Filtering theo Category (Lọc Metadata Trước Khi Search)
- **Vấn đề cũ:** Khi crawl tự động, mọi thứ chỉ là text. Nếu user tìm "Học phí ngành CNTT 2024", Semantic Search có thể mang nhầm "Học bổng năm 2024" vì độ tương đồng ngữ nghĩa cao.
- **Khai thác mới:** Dùng trường `category` để pre-filter.
- **Luồng xử lý:**
  1. Query Processor phân tích câu hỏi → rút trích category (VD: "Học phí ngành CNTT" → `category = "Học phí"`).
  2. Lọc corpus chỉ giữ docs đúng category **trước khi** chạy BM25/Vector Search.
  3. Nếu không detect được category → search toàn bộ (fallback an toàn).
- **Lợi ích:** Độ chính xác tăng, tốc độ nhanh hơn do khoanh vùng dữ liệu nhỏ.

### 2. Time-Aware Retrieval (Tìm Kiếm Ưu Tiên Thời Gian)
- **Vấn đề cũ:** Không biết thông báo nào mới, thông báo nào cũ. Query "mới nhất" trả về doc năm 2020.
- **Khai thác mới:** Dùng trường `date` (139/193 docs có date, 54 docs date=null).
- **Luồng xử lý:**
  1. Tích hợp hàm **Time Decay** vào RRF Merger hoặc sau Cross-Encoder Reranker.
  2. Công thức: `final_score = relevance_score + alpha * time_boost(date)`, trong đó `time_boost` giảm dần theo khoảng cách ngày so với hiện tại.
  3. Docs không có date (`null`) → `time_boost = 0` (không bị penalty, chỉ không được boost).
  4. Chỉ kích hoạt khi query chứa tín hiệu thời gian ("mới nhất", "gần đây", "năm 2025").
- **Lợi ích:** Đảm bảo sinh viên luôn đọc được thông báo mới nhất, tránh lấy văn bản cũ.

### 3. Xây Dựng RAG Prompt Giàu Ngữ Nghĩa (Rich Context)
- **Vấn đề cũ:** Template đưa cho LLM chỉ có `[Title] - [Content]`. LLM không biết context thời gian hay chuyên mục.
- **Khai thác mới:** Gắn `category` và `date` vào Prompt → LLM hiểu rõ hơn về ngữ cảnh tài liệu.
- Cấu trúc Prompt Context dự kiến:
  ```text
  [Tài Liệu 1]:
  - Tiêu đề: {title}
  - Danh mục: {category} | Ngày đăng: {date}
  - Nội dung: {content}
  - Nguồn: {url}
  ```
- **Lợi ích:** LLM có thể trả lời chính xác hơn, VD: "Theo thông báo ngày 15/03/2026 thuộc mục Học phí,..." thay vì trả lời chung chung.

---

## Phần 2: Các File Cần Thay Đổi

Sau khi chuyển sang `corpus_new.json` (có `category` + `date`), các file sau cần update:

### 1. `retrieval/query_processor.py` — Thêm Intent Extractor
- **Hiện tại:** Chỉ tokenize query + synonym expansion.
- **Cần thêm:** Rule-based extractor rút trích `category` và tín hiệu thời gian từ câu hỏi.
  - VD: "Học phí ngành CNTT 2024" → `filters = {"category": "Học phí"}`
  - VD: "hoạt động ĐRL mới nhất" → `time_aware = True`
- **Cách làm:** Map từ khóa → category dựa trên bảng category trong `CauTrucDataSet.md`. Detect từ khóa thời gian ("mới nhất", "gần đây", "năm 2025").

### 2. `retrieval/lexical_retrieval.py` — Nhận thêm `filters`
- **Hiện tại:** `get_candidates(tokens, top_k)` search toàn bộ corpus.
- **Cần thêm:** Tham số `category_filter` để chỉ tính BM25 trên subset docs đúng category.
- **Cách làm:** Load metadata từ corpus, lọc `doc_ids` theo category trước khi tính score.

### 3. `retrieval/rrf_merge.py` — Thêm Time Decay Boost
- **Hiện tại:** RRF chỉ dựa trên rank position.
- **Cần thêm:** Nếu `time_aware = True`, cộng thêm `time_boost` vào RRF score.
- **Công thức:** `time_boost = alpha / (1 + days_since_publish)`, với `alpha` là hệ số tuning.
- Docs có `date = null` → `time_boost = 0`.

### 4. `rag/context_builder.py` — Gắn metadata vào Prompt
- **Hiện tại:** Chỉ truyền title + content + url.
- **Cần thêm:** Gắn `category` và `date` vào template để LLM có thêm ngữ cảnh.

### 5. `test_search.py` & `api/` — Load corpus_new.json
- **Thay đổi:** Đổi path corpus từ `corpus.json` → `corpus_new.json`.
- Cập nhật `corpus_metadata` để include `category`, `date`.

### 6. `indexer/build_index.py` — Lưu metadata index
- **Cần thêm:** Xuất thêm file `doc_metadata.json` chứa `{doc_id: {category, date}}` để lexical retrieval có thể filter mà không cần load toàn bộ corpus.

---

## Phần 3: Luồng Xử Lý Mới (Data Flow)

```
Câu hỏi user
  │
  ▼
Query Processor (tokenize + extract category + detect time signal)
  │
  ├── category_filter: "Học phí" (hoặc None)
  ├── time_aware: True/False
  ├── tokens: ["học_phí", "học", "phí", "ngành", "cntt"]
  │
  ▼
┌─────────────────────────────────────────┐
│  Phase 1: Lexical (BM25 + TF-IDF)      │ ← filter by category
│  Phase 2: Dense (FAISS + BGE-M3)       │ ← filter by category
└─────────────────────────────────────────┘
  │
  ▼
RRF Merger (+ Time Decay boost nếu time_aware=True)
  │
  ▼
Cross-Encoder Reranker (top 10 → top K)
  │
  ▼
Context Builder (title + category + date + content + url)
  │
  ▼
LLM sinh câu trả lời (Qwen2.5-7B)
```

---

**NOTE:** Không cần đập code hiện tại. Chỉ cần **chèn metadata vào các điểm nối** của pipeline: filter trước search, boost sau RRF, gắn vào prompt trước LLM.


### Tóm tắt
- **Mục tiêu:** Tối ưu hóa chất lượng trả lời thông tin cho sinh viên HUFLIT
- **Cách làm:** Chèn metadata vào các điểm nối của pipeline: filter trước search, boost sau RRF, gắn vào prompt trước LLM
- **Kết quả:** Tăng độ chính xác và độ tin cậy của kết quả tìm kiếm, giảm thời gian xử lý và chi phí tính toán

Góp ý mới nhất -> nếu kq search quá tốt mà k cần model phức t