class RRFMerger:
    """
    Implements Reciprocal Rank Fusion to combine multiple ranked lists.
    Formula: RRF_Score = sum(1 / (k + rank_in_list))
    """
    def __init__(self, k=60):
        self.k = k

    def merge(self, lexical_candidates, dense_candidates, top_k=20):
        """
        Merge results from Lexical Retrieval (Phase 1) and Dense Retrieval (Phase 2).
        lexical_candidates: list of dicts [{'doc_id': str, 'score': float}, ...]
        dense_candidates: list of dicts [{'doc_id': str, 'dense_score': float}, ...]
        Returns a sorted list of top_k doc_ids.
        """
        rrf_scores = {}
        
        # Helper to add scores
        def add_ranks(candidates_list):
            for rank, item in enumerate(candidates_list):
                doc_id = item['doc_id']
                # Rank is 0-indexed, so rank + 1
                score = 1.0 / (self.k + rank + 1)
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + score
                
        # 1. Add Lexical Ranks
        add_ranks(lexical_candidates)
        
        # 2. Add Dense Ranks
        add_ranks(dense_candidates)
        
        # Sort by RRF score descending
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top K doc_ids
        return [doc_id for doc_id, score in sorted_results[:top_k]]
