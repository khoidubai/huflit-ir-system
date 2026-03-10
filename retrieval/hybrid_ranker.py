""" 
Kết hợp tất cả signals thành final score. Công thức: final = 0.30·tfidf + 0.40·bm25 + 0.20·lm + 0.10·entity_boost. entity_boost = 1.5 nếu category của doc khớp với entity type trong query, ngược lại = 1.0. Thêm exact_match_boost = 2.0 nếu query xuất hiện nguyên văn trong title. Sort descending, trả top-K.
"""
