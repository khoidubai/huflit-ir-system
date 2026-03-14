import os
from pathlib import Path

# Trỏ đúng thư mục cache chứa models--BAAI--bge-m3
os.environ["HF_HUB_CACHE"] = str(Path("models/bge_cache").resolve())
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1" # Force offline mode since models are cached

import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class DenseRetriever:
    """
    Handles Phase 2 embedding of queries and retrieving from FAISS.
    """
    def __init__(self, index_dir="data/index", model_name="BAAI/bge-m3"):
        self.index_dir = Path(index_dir)
        self.model_name = model_name
        self.model = None
        self.index = None
        self.doc_ids = []
        
        self._load_vector_store()
        
    def _load_vector_store(self):
        faiss_path = self.index_dir / "faiss_index.bin"
        mapping_path = self.index_dir / "dense_doc_ids.json"
        
        if not faiss_path.exists() or not mapping_path.exists():
            print(f"Warning: Vector index not found at {self.index_dir}. Run indexer/vector_store.py first.")
            return
            
        # Load FAISS
        self.index = faiss.read_index(str(faiss_path))
        
        # Load ID mapping
        with open(mapping_path, "r", encoding="utf-8") as f:
            self.doc_ids = json.load(f)
            
        # Load Model (Lazy load can be implemented, but we'll load it upfront for API responsiveness)
        self.model = SentenceTransformer(self.model_name)
        
    def retrieve(self, query: str, top_k: int = 20):
        """
        Embeds the query and retrieves the top_k relevant documents using FAISS.
        Returns a list of dictionaries: [{'doc_id': str, 'dense_score': float}]
        """
        if not self.model or not self.index:
            return []
            
        # Encode the query (normalize for cosine similarity)
        query_vector = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        
        # Search FAISS
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < 0 or idx >= len(self.doc_ids):
                continue
                
            doc_id = self.doc_ids[idx]
            score = float(distances[0][i])
            
            results.append({
                "doc_id": doc_id,
                "dense_score": score
            })
            
        return results
