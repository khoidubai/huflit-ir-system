# HUFLIT Information Retrieval System
**Hệ thống Tìm kiếm Thông minh – portal.huflit.edu.vn**

---

## 0. TỔNG QUAN HỆ THỐNG

Hệ thống IR xây dựng để tìm kiếm thông tin từ cổng thông tin sinh viên HUFLIT. Người dùng nhập query bằng tiếng Việt tự nhiên → hệ thống xử lý → trả về top-4 link kết quả có relevance score cao nhất. Phase sau tích hợp Language Model để sinh câu trả lời mượt thay vì chỉ trả link.

**Ba giai đoạn triển khai:**
- **Phase 1 – Core IR:** Crawl data → Index → TF-IDF/BM25 search → Top-4 ranked links
- **Phase 2 – Semantic:** Entity extraction → Dense vector mapping → LM tạo câu trả lời tự nhiên
- **Phase 3 – Scale:** Knowledge Base → Relevance feedback loop → Query expansion → Re-ranking

---

## 1. CÂY CẤU TRÚC DỰ ÁN

```
huflit-ir-system/
├── README.md
├── requirements.txt
├── .env.example
├── docker-compose.yml
│
├── crawler/
│   ├── spider.py
│   ├── parser.py
│   ├── cleaner.py
│   ├── scheduler.py
│   └── config.py
│
├── data/
│   ├── raw/
│   │   └── huflit_raw_YYYYMMDD.html
│   ├── processed/
│   │   └── corpus.json                ← DATASET CHÍNH
│   ├── index/
│   │   ├── inverted_index.pkl
│   │   ├── tfidf_matrix.npz
│   │   ├── bm25_params.json
│   │   └── vocab.json
│   └── knowledge_base/
│       ├── entities.json
│       └── relations.json
│
├── indexer/
│   ├── tokenizer.py
│   ├── inverted_index.py
│   ├── tfidf.py
│   ├── bm25.py
│   ├── vector_store.py
│   └── build_index.py
│
├── retrieval/
│   ├── query_processor.py
│   ├── entity_extractor.py
│   ├── exact_match.py
│   ├── ranked_retrieval.py
│   ├── probabilistic.py
│   ├── hybrid_ranker.py
│   └── reranker.py
│
├── lm_integration/               ← Phase 2
│   ├── embedder.py
│   ├── context_builder.py
│   ├── answer_generator.py
│   └── prompt_templates.py
│
├── knowledge_base/               ← Phase 3
│   ├── kb_builder.py
│   ├── entity_linker.py
│   └── relation_extractor.py
│
├── api/
│   ├── main.py
│   ├── schemas.py
│   ├── middleware.py
│   └── routes/
│       ├── search.py
│       ├── suggest.py
│       └── feedback.py
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
│
└── scripts/
    ├── run_crawler.sh
    ├── build_index.sh
    └── start_api.sh
```

---

## 2. MÔ TẢ CHI TIẾT TỪNG FILE

### 2.1 crawler/

**spider.py**
Crawler chính. Bắt đầu từ danh sách URL seed trong config.py, crawl đệ quy tất cả trang con trong domain portal.huflit.edu.vn. Tuân thủ robots.txt, rate limit 1 request/2 giây, max depth 3 cấp. Lưu raw HTML theo ngày vào data/raw/. Dùng requests + BeautifulSoup4.

**parser.py**
Nhận raw HTML, trích xuất các trường: title (lấy từ thẻ h1 hoặc title), url, date (tìm trong meta hoặc nội dung), content (loại bỏ nav/header/footer/script, chỉ giữ main content), category (suy ra từ URL path hoặc breadcrumb). Output là list dict Python.

**cleaner.py**
Làm sạch dữ liệu sau parse: chuẩn hoá unicode (NFC), bỏ ký tự thừa, loại trùng lặp bằng SHA-256 hash trên nội dung, bỏ document quá ngắn (dưới 50 từ). Ghi kết quả ra data/processed/corpus.json.

**scheduler.py**
Chạy nền, cron re-crawl mỗi 24 giờ. So sánh hash nội dung mới vs cũ, chỉ update document khi nội dung thay đổi. Ghi log vào crawl_log.txt.

**config.py**
Chứa: danh sách URL seed ban đầu, URL blacklist pattern (tránh crawl file PDF/ảnh/login), User-Agent header, CRAWL_DELAY, MAX_PAGES, MAX_DEPTH, timeout settings.

---

### 2.2 data/

**data/raw/**
HTML thô lưu theo ngày, không xử lý. Chỉ dùng khi cần debug hoặc re-parse.

**data/processed/corpus.json**
Dataset chính. Xem Section 3 bên dưới để biết schema chi tiết.

**data/index/inverted_index.pkl**
Inverted index dạng dict serialized: `{term: {df: int, postings: [{docId, tf, positions}]}}`. Dùng cho exact match và BM25 lookup.

**data/index/tfidf_matrix.npz**
Ma trận TF-IDF sparse (N docs × V vocab). Lưu định dạng scipy sparse matrix. Dùng cho cosine similarity trong Vector Space Model.

**data/index/bm25_params.json**
Lưu avgdl (average document length), N (tổng số docs), và IDF đã tính sẵn cho từng term. Tránh tính lại khi query.

**data/index/vocab.json**
Mapping term → index và ngược lại. Đồng bộ giữa tfidf_matrix và inverted_index.

**data/knowledge_base/entities.json**
Danh sách tất cả entities đã tách từ corpus: `{entity_value, entity_type, doc_ids[], frequency}`. Dùng để entity linking khi query.

**data/knowledge_base/relations.json**
Quan hệ giữa entities: `{subject, relation, object, doc_id}`. Ví dụ: (Học bổng loại A, tương_đương, 100% học phí).

---

### 2.3 indexer/

**tokenizer.py**
Tách từ tiếng Việt dùng underthesea word_tokenize. Lowercase. Bỏ stopwords (file stopwords_vi.txt). Áp dụng simple stemming (bỏ tiền/hậu tố phổ biến). Đây là module dùng chung cho cả indexer lẫn retrieval.

**inverted_index.py**
Nhận list documents đã tokenize, xây inverted index. Với mỗi term: đếm df (số doc chứa term), lưu postings list gồm docId + tf + vị trí xuất hiện (dùng cho phrase search). Serialize ra .pkl.

**tfidf.py**
Dùng scikit-learn TfidfVectorizer với analyzer='word', ngram_range=(1,2), sublinear_tf=True. Fit trên toàn corpus → lưu sparse matrix và vocab. Cũng lưu lại vectorizer object để transform query lúc search.

**bm25.py**
Implement BM25Okapi: k1=1.5, b=0.75. Tính avgdl từ corpus. Tính IDF cho mỗi term theo công thức Robertson. Lưu params ra JSON để load nhanh khi query mà không cần load toàn bộ corpus.

**vector_store.py**
Phase 2. Dùng sentence-transformers model (paraphrase-multilingual-MiniLM-L12-v2 hỗ trợ tiếng Việt) để embed từng document thành dense vector 384 chiều. Lưu vào FAISS flat index (IndexFlatIP, inner product = cosine sau khi normalize).

**build_index.py**
Entry point của toàn bộ indexer. Chạy theo thứ tự: load corpus.json → tokenize → build inverted index → build TF-IDF → build BM25 params → (nếu Phase 2) build FAISS. In progress log từng bước.

---

### 2.4 retrieval/

**query_processor.py**
Tiền xử lý query trước khi search. Các bước: lowercase → tokenize (dùng tokenizer.py) → remove stopwords → synonym expansion (ví dụ "tiền học" → "học phí", "bài thi" → "lịch thi") → detect query intent (factual/navigational/transactional). Output: cleaned_tokens, intent, expanded_terms.

**entity_extractor.py**
Tách named entities từ query bằng regex pattern + underthesea NER. Xác định filter: nếu query có entity SEMESTER thì boost docs thuộc category "Lịch thi" hoặc "Lịch học". Nếu có MONEY thì boost "Học phí". Mapping entity type → category boost được cấu hình trong entities_config.json.

**exact_match.py**
Boolean retrieval trên inverted index. Hỗ trợ: AND (giao postings list), OR (hợp postings list), NOT (loại trừ), phrase search (kiểm tra positions). Dùng cho query ngắn rõ ràng hoặc khi người dùng dùng dấu ngoặc kép.

**ranked_retrieval.py**
Tính TF-IDF score bằng cách transform query thành vector rồi tính cosine similarity với tfidf_matrix. Song song tính BM25 score bằng cách lookup từng query term trong inverted index và tính theo công thức BM25. Trả về dict `{docId: {tfidf_score, bm25_score}}`.

**probabilistic.py**
Language Model với Dirichlet smoothing. Tính log P(query|doc) = Σ log[(tf(t,d) + μ·P(t|C)) / (|d| + μ)] với μ=2000. P(t|C) là xác suất term trong toàn corpus (collection LM). Tránh zero probability cho terms không xuất hiện trong doc.

**hybrid_ranker.py**
Kết hợp tất cả signals thành final score. Công thức: `final = 0.30·tfidf + 0.40·bm25 + 0.20·lm + 0.10·entity_boost`. entity_boost = 1.5 nếu category của doc khớp với entity type trong query, ngược lại = 1.0. Thêm exact_match_boost = 2.0 nếu query xuất hiện nguyên văn trong title. Sort descending, trả top-K.

**reranker.py**
Phase 2. Nhận top-20 kết quả từ hybrid_ranker, dùng cross-encoder (ms-marco-MiniLM-L-6-v2) để re-score từng cặp (query, doc_snippet). Chậm hơn nhưng chính xác hơn. Chỉ chạy khi RERANKER_ENABLED=true trong .env.

---

### 2.5 lm_integration/ (Phase 2)

**embedder.py**
Load sentence-transformers model. Encode query thành dense vector. Normalize L2 trước khi đưa vào FAISS. Có cache để tránh encode lại query giống nhau.

**context_builder.py**
Nhận top-3 document từ hybrid_ranker. Ghép title + snippet của từng doc thành một context string. Thêm metadata (category, date, url) vào context. Truncate để không vượt quá context window của LLM.

**answer_generator.py**
Nhận context + query gốc → gọi LLM (Gemini API hoặc model local) để sinh câu trả lời tiếng Việt mượt. Thêm source links vào cuối câu trả lời. Fallback: nếu LLM không available thì trả về snippet của top-1 result.

**prompt_templates.py**
Chứa các prompt template. Template chính: "Dựa trên thông tin sau từ cổng HUFLIT: [context]. Hãy trả lời câu hỏi: [query]. Trả lời ngắn gọn, chính xác bằng tiếng Việt."

---

### 2.6 knowledge_base/ (Phase 3)

**kb_builder.py**
Đọc toàn bộ corpus, tách entities từ mỗi document, đếm frequency, ghi ra entities.json. Đây là bước build KB ban đầu, chạy một lần sau khi có corpus.

**entity_linker.py**
Khi nhận query đã tách entities, tìm entity trong KB để lấy thêm context (ví dụ query hỏi về "học bổng loại A" → KB trả về "tương đương 100% học phí, điều kiện GPA 3.6+"). Bổ sung thông tin này vào context cho LLM.

**relation_extractor.py**
Trích xuất quan hệ đơn giản từ corpus theo pattern: [Entity1] + [relation keyword] + [Entity2]. Ví dụ pattern "X yêu cầu Y", "X từ Y đến Z", "X tương đương Y". Lưu vào relations.json.

---

### 2.7 api/

**main.py**
FastAPI app. Khởi động: load index vào memory (inverted_index.pkl, tfidf_matrix.npz, bm25_params.json). Mount các router. Expose /docs (Swagger). Health check tại GET /health.

**schemas.py**
Pydantic models: SearchRequest `{query: str, top_k: int=4, mode: str="hybrid"}`, SearchResult `{id, title, url, snippet, score, category, date, entities[]}`, SearchResponse `{results[], query_id, total_time_ms}`.

**middleware.py**
CORS (cho phép frontend localhost). Request logging. Rate limiting 60 req/phút/IP. Error handler trả JSON thay vì HTML.

**routes/search.py**
POST /search. Nhận SearchRequest → gọi query_processor → entity_extractor → exact_match (nếu có phrase) → ranked_retrieval → hybrid_ranker → trả SearchResponse. Log query vào search_log.jsonl để phân tích sau.

**routes/suggest.py**
GET /suggest?q=... Autocomplete dựa trên prefix match trong vocab.json và các query phổ biến trong search_log. Trả về tối đa 5 gợi ý.

**routes/feedback.py**
POST /feedback. Nhận `{query_id, doc_id, relevant: bool}` từ user click. Lưu vào feedback.jsonl. Dùng để cải thiện ranking trong Phase 3 (Relevance Feedback theo Rocchio algorithm).

---

### 2.8 frontend/

**index.html**
SPA đơn giản. Có search bar, nút search, khu hiển thị kết quả (card: title link + snippet + category badge + score bar). Phase 2 thêm khu hiển thị LM answer ở trên cùng.

**app.js**
Gọi POST /search khi user submit. Render kết quả dạng card. Gọi GET /suggest khi user gõ (debounce 300ms). Gọi POST /feedback khi user click vào một kết quả (implicit positive feedback).

**style.css**
Styling đơn giản, màu trường HUFLIT (xanh navy). Responsive mobile. Highlight từ khóa trong snippet.

---

## 3. CẤU TRÚC DATASET (corpus.json)

### 3.1 Nguồn dữ liệu – các trang ưu tiên crawl từ portal.huflit.edu.vn

- Tuyển sinh, Học phí, Lịch thi, Lịch học, Đăng ký môn học
- Thông báo chung, Kế hoạch đào tạo, Lịch nghỉ
- Tốt nghiệp, Học bổng, Chứng chỉ ngoại ngữ
- Ký túc xá, Công tác sinh viên, Dịch vụ hành chính
- Hợp tác quốc tế, Câu lạc bộ, Hoạt động sinh viên

### 3.2 Schema một document trong corpus.json

```json
{
  "id": "huflit_0001",
  "title": "Thông báo tuyển sinh đại học chính quy năm 2024",
  "url": "https://portal.huflit.edu.vn/tuyen-sinh/dai-hoc-2024",
  "category": "Tuyển sinh",
  "date": "2024-03-15",
  "content": "Trường Đại học Ngoại ngữ - Tin học TP.HCM thông báo...",
  "keywords": ["tuyển sinh", "chỉ tiêu", "xét tuyển", "học phí"],
  "entities": [
    { "type": "YEAR", "value": "2024" },
    { "type": "MONEY", "value": "12 triệu" },
    { "type": "MAJOR", "value": "Công nghệ thông tin" }
  ],
  "tokens": ["trường", "đại_học", "ngoại_ngữ", "tin_học", "thông_báo"],
  "word_count": 342,
  "crawled_at": "2024-11-01T08:30:00Z",
  "lang": "vi",
  "source": "portal.huflit.edu.vn"
}
```

**Lưu ý:**
- Trường `content` là plain text đã strip HTML, dùng cho indexing và snippet.
- Trường `tokens` là list sau khi tokenize + remove stopwords, dùng trực tiếp khi build index, không cần tokenize lại.
- Trường `entities` được tách lúc cleaning, lưu sẵn để tránh tách lại mỗi lần query.
- `id` format: `huflit_XXXX` với XXXX là số thứ tự 4 chữ số, padding zero.

### 3.3 Các loại entity được tách

| type | Mô tả | Ví dụ |
|------|-------|-------|
| DATE | Ngày tháng cụ thể | 15/3/2024, ngày 6/1/2025 |
| MONEY | Số tiền | 16.500.000 VNĐ, 12 triệu |
| SEMESTER | Học kỳ | học kỳ I, HK2 2024-2025 |
| GRADE | GPA hoặc điểm | GPA 3.6, điểm 2.0 |
| CERTIFICATE | Chứng chỉ | B1, IELTS 6.0, TOEFL 80 |
| MAJOR | Ngành học | Công nghệ thông tin, Ngôn ngữ Anh |
| DEPARTMENT | Phòng ban | Phòng Đào tạo, Phòng CTSV |
| CREDIT | Số tín chỉ | 120 tín chỉ, 12 tín chỉ |
| ACADEMIC_YEAR | Năm học | 2024-2025 |
| PERCENTAGE | Phần trăm | 100% học phí, 50% chi phí |

### 3.4 Danh sách category chuẩn

| category | URL pattern | Ví dụ trang |
|----------|-------------|-------------|
| Tuyển sinh | /tuyen-sinh/* | Chỉ tiêu, phương thức, ngành |
| Học phí | /tai-chinh/*, /hoc-phi/* | Mức phí, hạn nộp |
| Lịch thi | /lich-thi/* | Lịch thi kết thúc học phần |
| Lịch học | /lich-hoc/* | Thời khóa biểu |
| Đăng ký môn | /dang-ky-mon/* | Thời gian, hướng dẫn đăng ký |
| Học bổng | /hoc-bong/* | Điều kiện, mức học bổng |
| Tốt nghiệp | /tot-nghiep/* | Điều kiện, lịch xét, lễ trao bằng |
| Đào tạo | /dao-tao/* | Ngành, tín chỉ, chương trình |
| Ký túc xá | /ktx/* | Giá phòng, đăng ký |
| Thông báo | /thong-bao/* | Nghỉ lễ, sự kiện chung |
| Hợp tác quốc tế | /quoc-te/* | Trao đổi, học bổng nước ngoài |
| Chứng chỉ | /chung-chi/* | Ngoại ngữ, tin học |
| Hỗ trợ sinh viên | /ctsv/* | Thủ tục, giấy tờ, câu lạc bộ |

---

## 4. IR KEYWORD → MODULE MAPPING

Mỗi keyword học thuật được triển khai ở đâu trong hệ thống:

| Keyword | File | Cách triển khai |
|---------|------|-----------------|
| TF-IDF | indexer/tfidf.py, retrieval/ranked_retrieval.py | TfidfVectorizer fit corpus, cosine similarity khi query |
| Vector Space Model | indexer/tfidf.py, indexer/vector_store.py | Sparse vectors (TF-IDF) + Dense vectors (sentence-transformers) |
| Database | data/index/*.pkl, *.npz, *.json | Inverted index, TF-IDF matrix, BM25 params serialized trên disk |
| Search Engine | api/routes/search.py + retrieval/ | Toàn bộ pipeline từ nhận query đến trả kết quả |
| IR Pipeline | retrieval/ (toàn bộ) | query → preprocess → retrieve → rank → return |
| Relevance | retrieval/hybrid_ranker.py, api/routes/feedback.py | Relevance score tổng hợp; thu feedback từ user click |
| User–Query–Document | api/schemas.py, retrieval/query_processor.py | Model hoá 3 thực thể theo mô hình Cranfield |
| Exact Match | retrieval/exact_match.py | Boolean AND/OR/NOT + phrase search trên postings list |
| Ranked Retrieval | retrieval/ranked_retrieval.py, hybrid_ranker.py | Sort theo score giảm dần, trả top-K |
| Probabilistic Model | retrieval/probabilistic.py | Language Model Dirichlet smoothing; BM25 trong bm25.py |
| Knowledge Base | knowledge_base/ (toàn bộ) | Entities + relations trích từ corpus |
| BM25 | indexer/bm25.py, retrieval/ranked_retrieval.py | BM25Okapi k1=1.5 b=0.75 |
| Indexing | indexer/inverted_index.py, build_index.py | Inverted index: term → {df, postings list} |
| Language Models | lm_integration/ + retrieval/probabilistic.py | Dirichlet LM cho scoring; LLM (Gemini/Qwen) cho answer gen |
| Entity Extraction | retrieval/entity_extractor.py, knowledge_base/kb_builder.py | Regex + NER tách DATE/MONEY/MAJOR/CERT từ query và corpus |

---

## 5. PIPELINE XỬ LÝ QUERY

### Phase 1 – Core IR (link-based results)

```
User nhập query
    ↓
[query_processor.py]    lowercase → tokenize → remove stopwords → synonym expand
    ↓
[entity_extractor.py]   tách entities → xác định category filter
    ↓
[exact_match.py]        nếu query có dấu "" → phrase search trong inverted index
    ↓
[ranked_retrieval.py]   tính TF-IDF cosine score + BM25 score cho candidate docs
    ↓
[probabilistic.py]      tính Language Model score (Dirichlet)
    ↓
[hybrid_ranker.py]      final = 0.30·tfidf + 0.40·bm25 + 0.20·lm + entity_boost
    ↓
API trả về top-4: {title, url, snippet, score, category, entities}
```

### Phase 2 – Semantic + LM answer

```
User nhập query
    ↓
[entity_extractor.py]   tách entities → structured intent
    ↓
[embedder.py]           query → dense vector 384 chiều (multilingual model)
    ↓
[vector_store.py]       FAISS ANN search → top-20 candidates
    ↓
[hybrid_ranker.py]      kết hợp BM25 + dense cosine → top-5
    ↓
[reranker.py]           cross-encoder re-rank top-5 → top-3
    ↓
[context_builder.py]    ghép title + snippet của top-3 thành context
    ↓
[answer_generator.py]   LLM đọc context + query → sinh câu trả lời tiếng Việt
    ↓
Trả về: câu trả lời mượt + source links
```

---

## 6. CÔNG THỨC SCORING

**TF-IDF:**
```
TF(t,d)      = count(t,d) / |d|
IDF(t)       = log((N+1) / (df(t)+1)) + 1
TF-IDF(t,d)  = TF(t,d) × IDF(t)
```

**BM25 (Robertson et al.):**
```
score(q,d) = Σ IDF(t) × [tf(t,d)×(k1+1)] / [tf(t,d) + k1×(1 - b + b×|d|/avgdl)]
k1 = 1.5,  b = 0.75
```

**Language Model – Dirichlet Smoothing:**
```
P(t|d)     = [tf(t,d) + μ × P(t|C)] / [|d| + μ]
P(t|C)     = cf(t) / total_tokens_in_corpus
μ          = 2000  (hyperparameter)
log score  = Σ log P(t|d)  for t in query
```

**Hybrid Final Score:**
```
final = 0.30·tfidf_cosine + 0.40·bm25 + 0.20·lm + entity_boost
entity_boost = 1.5 nếu category khớp entity query, ngược lại = 1.0
exact_boost  = ×2.0 nếu query phrase xuất hiện nguyên văn trong title
```

---

## 7. SETUP TỪNG BƯỚC

**Bước 1 – Cài môi trường**
```
git clone <repo> && cd huflit-ir-system
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

requirements.txt cần: scrapy, requests, beautifulsoup4, lxml, underthesea, scikit-learn, rank-bm25, sentence-transformers, faiss-cpu, fastapi, uvicorn, pydantic, python-dotenv, schedule

**Bước 2 – Crawl data**
```
python crawler/spider.py --start-url https://portal.huflit.edu.vn --max-pages 500
python crawler/parser.py --input data/raw/ --output data/processed/corpus_raw.json
python crawler/cleaner.py --input data/processed/corpus_raw.json --output data/processed/corpus.json
```
Kết quả: corpus.json với khoảng 200–500 documents tùy số trang crawl được.

**Bước 3 – Build index**
```
python indexer/build_index.py --corpus data/processed/corpus.json --output data/index/
```
Chạy tuần tự: tokenize → inverted index → TF-IDF → BM25 → (optional Phase 2) FAISS. Khoảng 2–5 phút.

**Bước 4 – Khởi động API**
```
uvicorn api.main:app --reload --port 8000
```
Swagger docs tại http://localhost:8000/docs

**Bước 5 – Chạy frontend**
```
cd frontend && python -m http.server 3000
```
Mở http://localhost:3000

**Bước 6 – (Phase 2) Bật LM**
Trong .env set `LLM_ENABLED=true` và `GEMINI_API_KEY=...` hoặc `LLM_MODEL=qwen2:7b` (chạy local qua Ollama). Chạy thêm:
```
python indexer/vector_store.py --corpus data/processed/corpus.json
```

---

## 8. CÁC BIẾN MÔI TRƯỜNG (.env)

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| HUFLIT_BASE_URL | URL gốc cần crawl | https://portal.huflit.edu.vn |
| CRAWL_DELAY | Giây giữa các request | 2 |
| MAX_PAGES | Số trang tối đa crawl | 500 |
| MAX_DEPTH | Độ sâu đệ quy | 3 |
| BM25_K1 | Tham số BM25 k1 | 1.5 |
| BM25_B | Tham số BM25 b | 0.75 |
| LM_MU | Tham số Dirichlet μ | 2000 |
| TOP_K | Số kết quả trả về | 4 |
| LLM_ENABLED | Bật Phase 2 LM | false |
| GEMINI_API_KEY | API key Gemini | — |
| LLM_MODEL | Model local (Ollama) | qwen2:7b |
| RERANKER_ENABLED | Bật cross-encoder | false |

---

## 9. API ENDPOINTS

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| POST /search | POST | Tìm kiếm chính. Body: `{query, top_k, mode}` |
| GET /suggest | GET | Autocomplete. Param: `?q=...` |
| POST /feedback | POST | Nhận feedback relevance từ user |
| GET /health | GET | Kiểm tra trạng thái hệ thống |

**Request example:**
```json
POST /search
{
  "query": "học phí học kỳ 2 năm 2025",
  "top_k": 4,
  "mode": "hybrid"
}
```

**Response example:**
```json
{
  "results": [
    {
      "id": "huflit_0003",
      "title": "Thông báo học phí học kỳ II năm học 2024-2025",
      "url": "https://portal.huflit.edu.vn/tai-chinh/hoc-phi-hk2",
      "snippet": "Hạn nộp học phí từ 3/2/2025 đến 28/2/2025. Học phí ngành CNTT: 16.500.000 VNĐ...",
      "score": 0.847,
      "category": "Học phí",
      "date": "2024-12-01",
      "entities": [
        { "type": "SEMESTER", "value": "học kỳ II" },
        { "type": "ACADEMIC_YEAR", "value": "2024-2025" },
        { "type": "MONEY", "value": "16.500.000 VNĐ" }
      ]
    }
  ],
  "query_id": "q_20241201_001",
  "total_time_ms": 42
}
```

---

## 10. LƯU Ý QUAN TRỌNG KHI TRIỂN KHAI

- **Underthesea** cần cài thêm model: `underthesea download`. Nếu server không có internet, pre-download trước.
- **FAISS** cần cài `faiss-cpu` không phải `faiss-gpu` trừ khi có GPU.
- **sentence-transformers** lần đầu chạy sẽ tự download model (~400MB). Pre-download nếu server offline.
- **corpus.json** nên commit vào Git để team có data đồng nhất. Nếu quá lớn thì dùng Git LFS.
- **Inverted index** và TF-IDF matrix phải được rebuild mỗi khi corpus thay đổi (chạy lại build_index.py).
- Khi crawl thật cần kiểm tra xem HUFLIT portal có chặn bot không. Nếu có thì cần thêm cookie/session từ trình duyệt vào config.py.
- Stopwords tiếng Việt: dùng file stopwords_vi.txt từ thư viện underthesea hoặc tự build từ corpus (top-50 terms phổ biến nhất thường là stopwords).


## KIẾN TRÚC TỔNG QUAN:

```mermaid
User Query (text / tiếng Việt)
        │
        ▼
  Query Processor
  (lowercase → tokenize underthesea → remove stopwords → synonym expand)
        │
        ▼
  Entity Extractor
  (DATE / MONEY / SEMESTER / MAJOR / CERT / DEPARTMENT)
        │
        ▼
  Query Router (regex + entity type)
   ┌────┴────┐
   │                   │
Exact Match        RAG Pipeline
(phrase search)    (Hybrid)
   │                   │
   │         Dense (bge-m3 + ChromaDB)
   │         Sparse (BM25S)
   │         RRF Merge (k=60)
   │         Rerank (bge-reranker-v2-m3, top-4)
   │         Category Boost (entity → category)
   │                   │
   └────┬──────────────┘
        │
        ▼
  Hybrid Scorer
  (0.30×TF-IDF + 0.40×BM25 + 0.20×LM Dirichlet + entity_boost)
        │
        ▼
  ┌─────────────────────────┐
  │     Phase 1 Output      │
  │  Top-4 Ranked Links     │
  │  {title, url, snippet,  │
  │   score, category,      │
  │   entities}             │
  └─────────────────────────┘
        │
        ▼  (Phase 2 — LLM_ENABLED=true)
  Context Builder
  (ghép title + snippet top-3 docs)
        │
        ▼
  Qwen2.5-7B / Gemini API
  (sinh câu trả lời tiếng Việt mượt)
        │ SSE streaming
        ▼
  Frontend (Vanilla JS)
  (search bar → result cards → LM answer box)
```mermaid
