import argparse
import json
import os
import time
from pathlib import Path
os.environ["HF_HUB_CACHE"] = str(Path("models/bge_cache").resolve())
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def create_dense_index(corpus_path, output_dir, model_name='BAAI/bge-m3'):
    """
    Reads the corpus, embeds the content using a SentenceTransformer model,
    and saves the embeddings into a FAISS index.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading corpus from {corpus_path}...")
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)
        
    print(f"Loading SentenceTransformer model: {model_name}...")
    model = SentenceTransformer(model_name)
    
    # We will embed the combination of Title + Content
    docs_text = []
    doc_ids = []
    
    for doc in corpus:
        text = f"{doc.get('title', '')}. {doc.get('content', '')}"
        docs_text.append(text)
        doc_ids.append(doc.get('id'))
        
    print(f"Encoding {len(docs_text)} documents... This may take a while.")
    start_time = time.time()
    
    # Encode with progress bar enabled inside the model (show_progress_bar is True by default in some versions, 
    # but we can just let it run)
    embeddings = model.encode(docs_text, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=True)
    
    print(f"Encoding complete in {time.time() - start_time:.2f} seconds.")
    
    # Create FAISS Index (IndexFlatIP for Inner Product which is Cosine Similarity when normalized)
    embedding_dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(embedding_dim)
    index.add(embeddings)
    
    # Save the index to disk
    faiss_path = output_dir / "faiss_index.bin"
    faiss.write_index(index, str(faiss_path))
    
    # Save the mapping between FAISS integer IDs and our string doc_ids
    mapping_path = output_dir / "dense_doc_ids.json"
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(doc_ids, f, ensure_ascii=False)
        
    print(f"\n✅ Vector Store (FAISS) created successfully!")
    print(f"Saved FAISS index to: {faiss_path}")
    print(f"Saved mapping to: {mapping_path}")
    print(f"Index size: {index.ntotal} documents")

def main():
    parser = argparse.ArgumentParser(description="Build FAISS Vector Store for Semantic Search")
    parser.add_argument("--corpus", required=True, help="Path to corpus.json")
    parser.add_argument("--output", default="data/index/", help="Directory to save the FAISS index files")
    parser.add_argument("--model", default="BAAI/bge-m3", help="Sentence transformer model to use")
    
    args = parser.parse_args()
    
    create_dense_index(args.corpus, args.output, args.model)

if __name__ == "__main__":
    main()
