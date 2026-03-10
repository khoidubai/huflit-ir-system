""" 
Implement BM25Okapi: k1=1.5, b=0.75. Tính avgdl từ corpus. Tính IDF cho mỗi term theo công thức Robertson. Lưu params ra JSON để load nhanh khi query mà không cần load toàn bộ corpus.
"""

import json
import math
from collections import Counter

def build_bm25(documents, params_path):
    """
    documents: list of dict {'tokens': list}
    Calculates avgdl, N, and IDF for each term.
    k1 = 1.5, b = 0.75
    """
    N = len(documents)
    total_len = sum(len(doc['tokens']) for doc in documents)
    avgdl = total_len / N if N > 0 else 0
    
    # Tính document frequency cho từng term
    df_counts = Counter()
    for doc in documents:
        unique_terms = set(doc['tokens'])
        for term in unique_terms:
            df_counts[term] += 1
            
    # Tính IDF theo công thức Robertson
    idf = {}
    for term, df in df_counts.items():
        # IDF = log((N - df + 0.5) / (df + 0.5) + 1)
        # Công thức đơn giản hơn thường dùng: log(N/df)
        idf[term] = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
        
    params = {
        'N': N,
        'avgdl': avgdl,
        'idf': idf,
        'k1': 1.5,
        'b': 0.75
    }
    
    with open(params_path, 'w', encoding='utf-8') as f:
        json.dump(params, f, ensure_ascii=False, indent=2)
        
    return params

def load_bm25_params(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
