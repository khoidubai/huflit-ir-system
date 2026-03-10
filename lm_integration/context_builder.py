""" 
Nhận top-3 document từ hybrid_ranker. Ghép title + snippet của từng doc thành một context string. Thêm metadata (category, date, url) vào context. Truncate để không vượt quá context window của LLM.
"""
