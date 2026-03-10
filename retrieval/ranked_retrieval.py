import os
import json
import pickle
import numpy as np
from pathlib import Path
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

# Thêm path để import indexer.bm25 (nếu cần load helper)
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class RankedRetrieval:
    def __init__(self, index_dir):
        self.index_dir = Path(index_dir)
        self._load_all()

    def _load_all(self):
        # 1. Load Inverted Index
        with open(self.index_dir / "inverted_index.pkl", "rb") as f:
            self.inv_index = pickle.load(f)
            
        # 2. Load TF-IDF & Docs
        with open(self.index_dir / "vocab.json", "r", encoding="utf-8") as f:
            self.vocab = json.load(f)
        with open(self.index_dir / "doc_ids.json", "r", encoding="utf-8") as f:
            self.doc_ids = json.load(f)
        self.tfidf_matrix = sparse.load_npz(self.index_dir / "tfidf_matrix.npz")
        
        # 3. Load BM25 Params & Lengths
        with open(self.index_dir / "bm25_params.json", "r", encoding="utf-8") as f:
            self.bm25_params = json.load(f)
        with open(self.index_dir / "doc_lengths.json", "r", encoding="utf-8") as f:
            self.doc_lengths = json.load(f)
            
        self.avgdl = self.bm25_params['avgdl']
        self.idf = self.bm25_params['idf']
        self.k1 = self.bm25_params['k1']
        self.b = self.bm25_params['b']

    def calculate_tfidf_scores(self, query_tokens):
        if not query_tokens: return {}
        vectorizer = TfidfVectorizer(vocabulary=self.vocab, ngram_range=(1, 2))
        query_tfidf = vectorizer.fit_transform([" ".join(query_tokens)])
        # Cosine similarity
        scores = (self.tfidf_matrix * query_tfidf.T).toarray().flatten()
        return {self.doc_ids[i]: float(scores[i]) for i in range(len(self.doc_ids)) if scores[i] > 0}

    def calculate_bm25_scores(self, query_tokens):
        scores = {}
        for token in query_tokens:
            if token not in self.inv_index: continue
            token_idf = self.idf.get(token, 0)
            for p in self.inv_index[token]['postings']:
                doc_id = p['doc_id']
                tf = p['tf']
                doc_len = self.doc_lengths.get(doc_id, self.avgdl)
                score = token_idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl))
                scores[doc_id] = scores.get(doc_id, 0.0) + score
        return scores

    def get_all_scores(self, query_tokens):
        tfidf_scores = self.calculate_tfidf_scores(query_tokens)
        bm25_scores = self.calculate_bm25_scores(query_tokens)
        
        all_doc_ids = set(tfidf_scores.keys()) | set(bm25_scores.keys())
        results = {}
        for d_id in all_doc_ids:
            results[d_id] = {
                'tfidf': tfidf_scores.get(d_id, 0.0),
                'bm25': bm25_scores.get(d_id, 0.0)
            }
        return results
