""" 
POST /search. Nhận SearchRequest → gọi query_processor → entity_extractor → exact_match (nếu có phrase) → ranked_retrieval → hybrid_ranker → trả SearchResponse. Log query vào search_log.jsonl để phân tích sau.
"""
