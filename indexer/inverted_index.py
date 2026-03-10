import pickle
from collections import defaultdict

def build_inverted_index(documents):
    """
    documents: list of dict {'id': str, 'tokens': list}
    Returns: inverted_index dict 
    {
        term: {
            'df': int, 
            'postings': [
                {'doc_id': str, 'tf': int, 'positions': [int]}
            ]
        }
    }
    """
    index = defaultdict(lambda: {'df': 0, 'postings': []})
    
    for doc in documents:
        doc_id = doc['id']
        tokens = doc['tokens']
        
        # Thống kê tf và positions cho từng term trong doc
        term_stats = defaultdict(lambda: {'tf': 0, 'positions': []})
        for i, token in enumerate(tokens):
            term_stats[token]['tf'] += 1
            term_stats[token]['positions'].append(i)
            
        # Cập nhật vào inverted index
        for term, stats in term_stats.items():
            index[term]['df'] += 1
            index[term]['postings'].append({
                'doc_id': doc_id,
                'tf': stats['tf'],
                'positions': stats['positions']
            })
            
    return dict(index)

def save_index(index, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(index, f)

def load_index(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)
