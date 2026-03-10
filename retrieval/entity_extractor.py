""" 
Tách named entities từ query bằng regex pattern + underthesea NER. Xác định filter: nếu query có entity SEMESTER thì boost docs thuộc category "Lịch thi" hoặc "Lịch học". Nếu có MONEY thì boost "Học phí". Mapping entity type → category boost được cấu hình trong entities_config.json.
"""
