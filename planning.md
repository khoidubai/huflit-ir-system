# Hướng phát triển (Advanced Metadata & Hybrid Retrieval)

Dựa trên cấu trúc lý tưởng từ file `CauTrucDataSet.md`, so với dữ liệu thực tế hiện tại (`corpus.json`) + áp dụng các kỹ thuật tinh gọn và chống ảo giác (Zero Hallucination) => hiệu quả hơn.

Dưới đây là kế hoạch chi tiết sau khi cấu trúc manual dataset:

---

## Phần 1: Các Tính Năng Có Thể Khai Thác

### 1. Hard-Filtering (Lọc Metadata) Trước Khi Vector Search
- **Vấn đề cũ:** Khi crawl tự động, mọi thứ chỉ là text. Nếu user tìm "Học phí ngành CNTT 2024", thuật toán Semantic Search có thể mang nhầm thông báo "Học bổng năm 2024" vì độ tương đồng ngữ nghĩa cao.
- **Khai thác mới:** Dùng trường `category` và `entities`.
- **Luồng xử lý:** Câu hỏi user -> Phân loại ý định (Rút trích category "Học phí", entity "2024") -> Lọc SQL/ChromaDB để chỉ lấy các document đúng category và năm -> Mới đem đi tính khoảng cách Vector.
- **Lợi ích:** Độ chính xác tăng, tốc độ search nhanh hơn do đã khoanh vùng dữ liệu cực nhỏ.

### 2. Time-Aware Retrieval (Tìm Kiếm Theo Thời Gian Thực)
- **Vấn đề cũ:** Không biết thông báo nào mới, thông báo nào cũ.
- **Khai thác mới:** Dùng trường `date`.
- **Luồng xử lý:** Tích hợp hàm Time Decay (phân rã thời gian) vào cấu trúc BM25/TF-IDF hoặc RRF Merger. Document nào có `date` càng gần hiện tại, điểm (score) càng được boost lên.
- **Lợi ích:** Đảm bảo sinh viên luôn đọc được thông báo tuyển sinh/học phí mới nhất, tránh lấy văn bản cũ của năm 2021.

### 3. Entity Injection - Chống Ảo Giác (Zero Hallucination) cho LLM (Phase 3)
- **Vấn đề cũ:** LLM có thể đọc sai các con số học phí, số tín chỉ nằm rải rác trong đoạn văn dài.
- **Khai thác mới:** Dùng trường `entities` (MONEY, MAJOR, DATE...).
- **Luồng xử lý:** Bơm thẳng mảng `entities` vào Prompt của Context, thay vì chỉ ném `content` thô.
- **Lợi ích:** Ép LLM Qwen 2.5 phải chú ý đến các tham số cực kỳ quan trọng do con người đã chuẩn bị, loại bỏ hoàn toàn khả năng bịa ra số liệu.

### 4. Tối Ưu Tốc Độ Lexical Search (Phase 1)
- **Vấn đề cũ:** Mỗi lần tạo chỉ mục BM25 hoặc query, hệ thống phải chạy thư viện `underthesea` để cắt từ tiếng Việt, việc này tốn nhiều tài nguyên CPU.
- **Khai thác mới:** Tận dụng trực tiếp mảng `tokens` và `keywords` đã xử lý sẵn.
- **Luồng xử lý:** Bỏ qua hàm `tokenize(text)` khi đọc `corpus.json` vào bộ nhớ. Load thẳng mảng `tokens` vào bộ đếm BM25 và TF-IDF Indexer.
- **Lợi ích:** Cải thiện tốc độ khởi động (cold-start) và giảm tải CPU hơn 50% trong Phase 1.

### 5. Xây Dựng RAG Prompt Giàu Ngữ Nghĩa (Rich Context)
- **Vấn đề cũ:** Template đưa cho LLM chỉ có `[Title] - [Content]`.
- **Khai thác mới:** Gắn toàn bộ metadata vào Prompt. LLM nhận được một bản tóm tắt cực xịn trước khi đọc chi tiết.
- Cấu trúc Prompt Context dự kiến:
  ```text
  [Tài Liệu 1]:
  - Tiêu đề: {title}
  - Danh mục: {category} | Ngày đăng: {date}
  - Trọng tâm (Keywords): {keywords}
  - Thực thể (Entities): {entities}
  - Nội dung chí tiết: {content}
  ```

---

## Phần 2: Data Flow & Architecture

Nếu áp dụng cấu trúc Manual Dataset (`CauTrucDataSet.md`), các file sau trong hệ thống sẽ cần được thiết kế lại:

### 1. `indexer/build_index.py` (Chỉ Mục Lexical)
- **Thay đổi:** 
  - Đọc thẳng field `"tokens"` để build BM25/TF-IDF thay vì cắt từ thủ công lại từ field `"content"`.
  - Lưu metadata (`category`, `date`, `keywords`) vào Inverted Index để phục vụ Filter.
- **Hành động:** Viết lại hàm `load_corpus()`.

### 2. `indexer/vector_store.py` (Chỉ Mục Vector Dense)
- **Thay đổi:** 
  - Thay vì xài FAISS (thuần Vector), sẽ chuyển sang **ChromaDB** hoặc cập nhật metadata schema nếu dùng FAISS.
  - ChromaDB lý tưởng hơn vì hỗ trợ Metadata Filtering cực mạnh. Lưu `category` và `date` thành `metadata` đi kèm mỗi vector.

### 3. `retrieval/query_processor.py` (Phân Tích Câu Hỏi)
- **Thay đổi:** 
  - (New Feature) Thêm bộ phân tích câu hỏi (Intent Extractor). Ví dụ: Nhận diện câu hỏi có chứa số (nền tảng year), chứa từ khóa "Học phí" -> Tạo `filters = {"category": "Học phí", "year": "2024"}`.
- **Hành động:** Nâng cấp rule-based NLP hoặc dùng thử NER nhẹ nhàng.

### 4. `retrieval/lexical_retrieval.py` & `retrieval/embedder.py` (Tìm Kiếm)
- **Thay đổi:** 
  - Các hàm `search()` nay đều phải nhận thêm tham số `filters` từ Query Processor.
  - Áp dụng bộ lọc trước khi retrieve. Bổ sung trích thưởng điểm dựa trên field `"date"`.
- **Hành động:** Update params và logic tìm điểm.

### 5. `rag/context_builder.py` (Xây Dựng Khung RAG)
- **Thay đổi:** 
  - Sửa đổi chuỗi f-string định dạng tài liệu. Nối các metadata (category, date, entities, keywords) một cách rõ ràng kèm theo URL để hệ thống trả về thông minh hơn.
- **Hành động:** Xóa code cũ, viết lại hàm tạo chuỗi snippet với template rich-text như đã trình bày ở Phần 1.5.

### 6. `api/routes/search.py` (Đầu Mối Controller)
- **Thay đổi:** 
  - Update payload API để nhận và log quá trình lọc metadata. 
  - Luồng mới: Câu hỏi -> Extract Metadata Filter -> (Lexical & Vector Search với Filters) -> RRF Merger (sắp xếp thêm điểm thời gian) -> Context Builder với cấu trúc mới -> LLM sinh câu.

---

**NOTE:** Việc update này không cần đập code hiện tại, mà là **nắm lấy metadata và chèn nó vào các ngách của Data Flow**, tận dụng tối đa thông tin ngữ nghĩa đã được xử lý tay từ trước để LLM có thể dễ dàng hiểu câu hỏi và đáp ứng nhanh gọn lẹ.
