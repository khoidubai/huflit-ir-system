import argparse
import json
import os
import time
from pathlib import Path
import sys

# Fix import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from indexer.tokenizer import tokenize
from indexer.inverted_index import build_inverted_index, save_index
from indexer.tfidf import build_tfidf
from indexer.bm25 import build_bm25

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", required=True, help="Path to corpus.json")
    parser.add_argument("--output", required=True, help="Directory to save index files")
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load corpus
    print(f"Loading corpus from {args.corpus}...")
    with open(args.corpus, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    
    # 2. Tokenize (nếu chưa có trong corpus.json hoặc muốn chạy lại)
    # README nói corpus.json có sẵn tokens, nhưng ta cứ check
    processed_docs = []
    print(f"Tokenizing {len(corpus)} documents...")
    start_time = time.time()
    
    for i, doc in enumerate(corpus):
        # Tạo ID nếu chưa có
        doc_id = doc.get('id', f"huflit_{i+1:04d}")
        
        # Lấy tokens sẵn có hoặc tokenize mới
        tokens = doc.get('tokens')
        if not tokens:
            # Title boosting: tokenize title riêng và lặp lại 3 lần
            # để BM25/TF-IDF ưu tiên match title cao hơn content
            title_tokens = tokenize(doc.get('title', ''))
            content_tokens = tokenize(doc.get('content', ''))
            tokens = title_tokens * 3 + content_tokens
            
        processed_docs.append({
            'id': doc_id,
            'tokens': tokens,
            'url': doc.get('url', ''),
            'title': doc.get('title', '')
        })
        
        if (i+1) % 50 == 0:
            print(f"  Processed {i+1}/{len(corpus)} docs...")
            
    print(f"Tokenization finished in {time.time() - start_time:.2f}s")
    
    # 3. Build Inverted Index
    print("Building Inverted Index...")
    inv_index = build_inverted_index(processed_docs)
    save_index(inv_index, output_dir / "inverted_index.pkl")
    
    # Lưu doc_ids và doc_lengths để mapping khi search
    doc_ids = [doc['id'] for doc in processed_docs]
    doc_lengths = {doc['id']: len(doc['tokens']) for doc in processed_docs}
    
    with open(output_dir / "doc_ids.json", "w", encoding="utf-8") as f:
        json.dump(doc_ids, f, ensure_ascii=False)
    with open(output_dir / "doc_lengths.json", "w", encoding="utf-8") as f:
        json.dump(doc_lengths, f, ensure_ascii=False)
    # 4. Build TF-IDF
    print("Building TF-IDF Matrix...")
    all_tokens = [doc['tokens'] for doc in processed_docs]
    
    build_tfidf(
        all_tokens, 
        output_dir / "vocab.json", 
        output_dir / "tfidf_matrix.npz"
    )
    
    # 5. Build BM25 Params
    print("Building BM25 Parameters...")
    build_bm25(processed_docs, output_dir / "bm25_params.json")
    
    print(f"\n Indexing complete! Files saved to {args.output}")
    print(f"Total documents: {len(processed_docs)}")
    print(f"Total vocabulary size: {len(inv_index)}")

if __name__ == "__main__":
    main()
