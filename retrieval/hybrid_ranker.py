class HybridRanker:
    def __init__(self, top_k=4):
        self.top_k = top_k
        # Trọng số theo README
        self.w_tfidf = 0.30
        self.w_bm25 = 0.40
        # self.w_lm = 0.20 # Phase 1 tạm chưa tính LM
        # self.entity_boost = 0.10

    def rank(self, scores_dict, corpus_metadata):
        """
        scores_dict: {doc_id: {tfidf, bm25}}
        corpus_metadata: {doc_id: {title, url, snippet, ...}}
        """
        final_results = []
        
        for doc_id, scores in scores_dict.items():
            # Tính điểm tổng hợp
            total_score = (
                self.w_tfidf * scores.get('tfidf', 0.0) + 
                self.w_bm25 * scores.get('bm25', 0.0)
            )
            
            # Lấy metadata
            meta = corpus_metadata.get(doc_id, {})
            
            final_results.append({
                'id': doc_id,
                'title': meta.get('title', 'Unknown'),
                'url': meta.get('url', '#'),
                'score': round(total_score, 4),
                'snippet': meta.get('content', '')[:200] + "..." # Snippet cơ bản
            })
            
        # Sắp xếp giảm dần theo điểm
        sorted_results = sorted(final_results, key=lambda x: x['score'], reverse=True)
        
        return sorted_results[:self.top_k]
