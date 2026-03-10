""" 
Tiền xử lý query trước khi search. Các bước: lowercase → tokenize (dùng tokenizer.py) → remove stopwords → synonym expansion (ví dụ "tiền học" → "học phí", "bài thi" → "lịch thi") → detect query intent (factual/navigational/transactional). Output: cleaned_tokens, intent, expanded_terms.
"""
