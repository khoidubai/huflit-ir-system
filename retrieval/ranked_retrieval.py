""" 
Tính TF-IDF score bằng cách transform query thành vector rồi tính cosine similarity với tfidf_matrix. Song song tính BM25 score bằng cách lookup từng query term trong inverted index và tính theo công thức BM25. Trả về dict {docId: {tfidf_score, bm25_score}}.
"""
