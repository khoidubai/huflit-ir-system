""" 
Phase 2. Dùng sentence-transformers model (paraphrase-multilingual-MiniLM-L12-v2 hỗ trợ tiếng Việt) để embed từng document thành dense vector 384 chiều. Lưu vào FAISS flat index (IndexFlatIP, inner product = cosine sau khi normalize).
"""
