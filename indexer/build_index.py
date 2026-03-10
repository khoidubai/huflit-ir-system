""" 
Entry point của toàn bộ indexer. Chạy theo thứ tự: load corpus.json → tokenize → build inverted index → build TF-IDF → build BM25 params → (nếu Phase 2) build FAISS. In progress log từng bước.
"""
