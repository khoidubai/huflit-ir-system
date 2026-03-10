""" 
Phase 2. Nhận top-20 kết quả từ hybrid_ranker, dùng cross-encoder (ms-marco-MiniLM-L-6-v2) để re-score từng cặp (query, doc_snippet). Chậm hơn nhưng chính xác hơn. Chỉ chạy khi RERANKER_ENABLED=true trong .env.
"""
