import json
import argparse
from retrieval.query_processor import process_query
from retrieval.ranked_retrieval import RankedRetrieval
from retrieval.hybrid_ranker import HybridRanker
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str, help="Câu hỏi tìm kiếm")
    args = parser.parse_args()

    print(f"🔍 Đang tìm kiếm: '{args.query}'...")

    # 1. Load data
    index_dir = "data/index"
    corpus_path = "data/processed/corpus.json"
    
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)
        # Chuyển list sang dict để lookup cho nhanh
        corpus_metadata = {doc.get('id', f"huflit_{i+1:04d}"): doc for i, doc in enumerate(corpus)}

    # 2. Xử lý query
    tokens = process_query(args.query)
    print(f"⚙️ Tokens: {tokens}")

    # 3. Tính điểm (Retrieval)
    retriever = RankedRetrieval(index_dir)
    scores = retriever.get_all_scores(tokens)

    # 4. Xếp hạng (Ranking)
    ranker = HybridRanker(top_k=4)
    results = ranker.rank(scores, corpus_metadata)

    # 5. Hiển thị kết quả
    print("\n--- KẾT QUẢ TÌM KIẾM ---")
    if not results:
        print("Không tìm thấy kết quả phù hợp.")
    else:
        for i, res in enumerate(results):
            print(f"{i+1}. [{res['score']}] {res['title']}")
            print(f"   URL: {res['url']}")
            print(f"   Snippet: {res['snippet']}\n")

if __name__ == "__main__":
    main()
