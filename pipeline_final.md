Pipeline sau tham khảo ý kiến cô T và chỉnh lại:

Phase 1 – Core IR (Lexical Retrieval)
User nhập query
    ↓
[query_processor.py]
lowercase → tokenize → remove stopwords → synonym expand
    ↓
[entity_extractor.py]
tách entities → xác định category filter
    ↓
[exact_match.py]
nếu query có dấu "" → phrase search trong inverted index
    ↓
[lexical_retrieval.py]
tìm candidate docs bằng:
    • TF-IDF
    • BM25
    • LM Dirichlet
    ↓
Trả về top-K lexical candidates

Output: candidate documents
{doc_id, title, url, snippet, score}

Phase 2: Hybrid Retrieval + Re-ranking

User query
    ↓
[embedder.py]
query → dense vector (multilingual embedding model)
    ↓
[vector_store.py]
FAISS ANN search → top-20 dense candidates
    ↓
[rrf_merge.py]
gộp ranking từ:
    • lexical retrieval
    • dense retrieval
    ↓
[reranker.py]
cross-encoder re-rank top-10 → top-3
    ↓
Top ranked documents

*Là phiên bản nâng cấp của phase 1

Phase 3: RAG (Retrieval-Augmented Generation)

Top documents
    ↓
[context_builder.py]
ghép title + snippet của top-3
    ↓
[answer_generator.py]
LLM đọc query + context
    ↓
Sinh câu trả lời tiếng Việt
    ↓
Trả về:
answer + source links


Pipeline hoàn chỉnh:

User query
    ↓
[Phase 1] lexical retrieval → top-K candidates
    ↓
[Phase 2] hybrid retrieval + re-ranking → top-3 documents
    ↓
[Phase 3] RAG → final answer + sources