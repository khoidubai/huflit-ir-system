# HUFLIT IR System — Compact Summary

File này tổng hợp toàn bộ trạng thái hiện tại của dự án để dùng làm context cho hội thoại mới.

---

## 1. Tổng quan dự án

Hệ thống IR tìm kiếm thông tin từ portal.huflit.edu.vn cho sinh viên HUFLIT. Kiến trúc **Advanced RAG Pipeline** gồm 3 phase:

- **Phase 1 (Lexical):** Query → tokenize → BM25 + TF-IDF → top-K candidates
- **Phase 2 (Hybrid):** Dense search (BGE-M3 + FAISS) → RRF merge lexical+dense → Cross-encoder rerank → top-3
- **Phase 3 (RAG):** Context builder → Qwen2.5-7B Local (GGUF, 100% offline) → sinh câu trả lời

## 2. Tech Stack

| Component | Tech |
|-----------|------|
| Tokenizer | `underthesea` + unigram fallback |
| Sparse Index | BM25 Okapi (k1=1.5, b=0.75), TF-IDF (bigram), Inverted Index |
| Dense Index | FAISS ANN + BAAI/bge-m3 (SentenceTransformer) |
| Reranker | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| LLM | Qwen2.5-7B-Instruct-Q4_K_M.gguf via llama-cpp-python |
| API | FastAPI |
| Frontend | SPA (HTML/JS/CSS) |
| Python | 3.13, venv tại `IR_HUFLIT/` |

## 3. Cây thư mục chính

```
huflit-ir-system/
├── test_search.py              ← Test pipeline qua terminal
├── crawler/                    ← spider, parser, cleaner, config
├── scripts/
│   └── generate_corpus_new.py  ← Trích xuất date → corpus_new.json
├── data/
│   ├── processed/
│   │   ├── corpus.json         ← Dataset gốc (193 docs: title, content, url)
│   │   └── corpus_new.json     ← Dataset nâng cấp (+ id, category, date)
│   └── index/
│       ├── inverted_index.pkl, tfidf_matrix.npz, bm25_params.json
│       ├── faiss_index.bin, dense_doc_ids.json
│       ├── doc_ids.json, doc_lengths.json, vocab.json
├── indexer/
│   ├── tokenizer.py            ← underthesea + unigram fallback
│   ├── build_index.py          ← Title boosting (title_tokens * 3 + content_tokens)
│   ├── vector_store.py         ← FAISS + BGE-M3, doc_id = huflit_XXXX
│   ├── inverted_index.py, tfidf.py, bm25.py
├── retrieval/
│   ├── query_processor.py      ← lowercase → tokenize → stopwords → synonym
│   ├── lexical_retrieval.py    ← BM25 + TF-IDF scoring
│   ├── embedder.py             ← Dense query encoding (BGE-M3)
│   ├── rrf_merge.py            ← Reciprocal Rank Fusion
│   ├── reranker.py             ← Cross-encoder reranker
│   ├── entity_extractor.py     ← (chưa tích hợp pipeline chính)
│   └── exact_match.py          ← (chưa tích hợp pipeline chính)
├── rag/
│   ├── context_builder.py, answer_generator.py, prompt_templates.py
├── api/main.py, routes/search.py
├── frontend/index.html, app.js, style.css
├── planning.md                 ← Kế hoạch khai thác category + date
├── CauTrucDataSet.md           ← Schema dataset kì vọng
├── HISTORY.md                  ← Nhật ký chi tiết
└── README.md
```

## 4. Dataset Schema (corpus_new.json)

```json
{
  "id": "huflit_0001",
  "title": "Thông báo tuyển sinh đại học chính quy năm 2024",
  "content": "Trường Đại học Ngoại ngữ - Tin học TP.HCM thông báo...",
  "url": "https://portal.huflit.edu.vn/tuyen-sinh/dai-hoc-2024",
  "category": "",
  "date": "2024-03-15"
}
```

- **193 docs** tổng cộng
- **category**: cần fill thủ công, mặc định "Thông báo chung"
- **date**: 139/193 có date (YYYY-MM-DD), 54 docs = null
- **tokens**: KHÔNG lưu trong corpus — tính on-the-fly khi build index

## 5. Các bug đã fix (2026-03-16)

### Bug 1 (Critical): dense_doc_ids.json toàn null
- **File:** `indexer/vector_store.py:37`
- **Nguyên nhân:** `doc.get('url')` → null → Dense retrieval trả doc_id null → RRF không merge được → Cross-encoder drop hết semantic results
- **Fix:** Đổi sang `doc.get('id', f"huflit_{idx+1:04d}")`

### Bug 2 (High): Tokenization mismatch
- **File:** `indexer/tokenizer.py:34-47`
- **Nguyên nhân:** underthesea tách query "tích điểm" → `tích_điểm`, nhưng doc title "[Điểm rèn luyện]" → `điểm` → BM25 không match
- **Fix:** Unigram Fallback — compound `tích_điểm` → thêm `tích` + `điểm`

### Bug 3 (Medium): Không ưu tiên title match
- **File:** `indexer/build_index.py:43-48`
- **Nguyên nhân:** title+content tokenize chung, không trọng số
- **Fix:** Title Boosting — `title_tokens * 3 + content_tokens`

### Kết quả
- Trước: top-3 toàn doc không liên quan (score 0.91 → -1.31)
- Sau: top-3 đều là "[Điểm rèn luyện]" docs (score 4.08 → 4.34)

## 6. Hướng phát triển tiếp theo (xem planning.md)

3 tính năng chính cần triển khai:
1. **Hard-Filtering theo Category** — pre-filter corpus theo category trước khi search
2. **Time-Aware Retrieval** — Time Decay boost dựa trên trường `date`
3. **Rich Context Prompt** — gắn category + date vào LLM prompt

Các file cần thay đổi:
- `retrieval/query_processor.py` — thêm Intent Extractor (rút trích category, detect time signal)
- `retrieval/lexical_retrieval.py` — nhận thêm `category_filter`
- `retrieval/rrf_merge.py` — thêm Time Decay boost
- `rag/context_builder.py` — gắn metadata vào prompt
- `indexer/build_index.py` — xuất thêm `doc_metadata.json`
- `test_search.py` & `api/` — đổi sang load `corpus_new.json`

## 7. Lệnh thường dùng

```bash
# Activate venv
source IR_HUFLIT/bin/activate

# Build sparse index
python indexer/build_index.py --corpus data/processed/corpus.json --output data/index/

# Regenerate dense_doc_ids.json (không cần rebuild FAISS vectors)
python3 -c "
import json
with open('data/processed/corpus.json') as f: corpus = json.load(f)
doc_ids = [doc.get('id', f'huflit_{i+1:04d}') for i, doc in enumerate(corpus)]
with open('data/index/dense_doc_ids.json', 'w') as f: json.dump(doc_ids, f)
"

# Test search
python test_search.py "Tôi cần tìm hoạt động tích điểm rèn luyện mới nhất"

# Generate corpus_new.json (trích xuất date)
python scripts/generate_corpus_new.py

# Start API
python api/main.py
```

## 8. Lưu ý quan trọng

- **KHÔNG đọc file `CauTrucDataSet.md` để nắm context code** — đó là schema kì vọng, không phải code thực tế.
- Venv: `IR_HUFLIT/` (Python 3.13)
- FAISS index vẫn dùng embeddings cũ (BGE-M3 encode từ raw text, không phụ thuộc tokenizer) → không cần rebuild khi đổi tokenizer.
- Model BGE-M3 có thể gặp lỗi `OSError` khi load nếu HF cache hỏng → dùng `repair_hf_cache.py` để sửa.
- Hiện tại `corpus_new.json` có `category = ""` cho tất cả docs → cần fill thủ công trước khi triển khai category filtering.

---
*Tạo: 20/03/2026*
