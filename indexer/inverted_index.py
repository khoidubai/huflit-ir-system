""" 
Nhận list documents đã tokenize, xây inverted index. Với mỗi term: đếm df (số doc chứa term), lưu postings list gồm docId + tf + vị trí xuất hiện (dùng cho phrase search). Serialize ra .pkl.
"""
