""" 
Load sentence-transformers model. Encode query thành dense vector. Normalize L2 trước khi đưa vào FAISS. Có cache để tránh encode lại query giống nhau.
"""
