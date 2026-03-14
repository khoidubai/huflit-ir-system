import os
from pathlib import Path
os.environ["HF_HUB_CACHE"] = str(Path("models/bge_cache").resolve())
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from sentence_transformers import CrossEncoder

class CrossEncoderReranker:
    """
    Phase 2: Reranker.
    Uses a Cross-Encoder to re-score query-document pairs.
    This provides highly accurate semantic similarity at the cost of computation.
    """
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = CrossEncoder(self.model_name)
        
    def rerank(self, query, top_doc_ids, corpus_metadata, top_k=3):
        """
        Takes the query and the top candidates from RRF.
        Builds pairs of (query, document) and scores them.
        Returns the top_k results.
        """
        if not top_doc_ids:
            return []
            
        pairs = []
        valid_doc_ids = []
        
        for doc_id in top_doc_ids:
            meta = corpus_metadata.get(doc_id)
            if not meta: continue
            
            # Combine title and content for better context
            text = f"{meta.get('title', '')}. {meta.get('content', '')}"
            pairs.append([query, text])
            valid_doc_ids.append(doc_id)
            
        if not pairs:
            return []
            
        # Compute Cross-Encoder scores
        scores = self.model.predict(pairs)
        
        # Pair up doc_ids with their new scores
        results = []
        for i in range(len(valid_doc_ids)):
            doc_id = valid_doc_ids[i]
            meta = corpus_metadata.get(doc_id, {})
            
            results.append({
                'id': doc_id,
                'title': meta.get('title', 'Unknown'),
                'url': meta.get('url', '#'),
                'category': meta.get('category', 'Chung'),
                'score': float(scores[i]),
                'snippet': meta.get('content', '')[:250] + "..." # Extracted Snippet
            })
            
        # Sort descending by the new Cross-Encoder score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]
