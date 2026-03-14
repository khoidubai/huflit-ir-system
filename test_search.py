import json
import argparse
import time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
import sys
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
from retrieval.query_processor import process_query
from retrieval.lexical_retrieval import RankedRetrieval
from retrieval.embedder import DenseRetriever
from retrieval.rrf_merge import RRFMerger
from retrieval.reranker import CrossEncoderReranker
from rag.context_builder import build_context
from rag.answer_generator import AnswerGenerator

def main():
    parser = argparse.ArgumentParser(description="Test the Advanced RAG Pipeline locally")
    parser.add_argument("query", type=str, help="Câu hỏi tìm kiếm")
    parser.add_argument("--top_k", type=int, default=3, help="Số kết quả trả về cuối cùng")
    parser.add_argument("--use_llm", action="store_true", help="Bật sinh câu trả lời LLM (yêu cầu bật Ollama local)")
    args = parser.parse_args()

    print(f"\n Đang tìm kiếm: '{args.query}'...")
    start_time = time.time()

    # 1. Load data
    index_dir = "data/index"
    corpus_path = "data/processed/corpus.json"
    
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)
        corpus_metadata = {doc.get('id', f"huflit_{i+1:04d}"): doc for i, doc in enumerate(corpus)}

    # 2. Tiền xử lý query
    tokens = process_query(args.query)
    print(f"⚙️ Tokens: {tokens}")


    # PHASE 1: LEXICAL RETRIEVAL
    print("\n[Phase 1] Chạy Lexical Retrieval...")
    lexical_retriever = RankedRetrieval(index_dir)
    lexical_candidates = lexical_retriever.get_candidates(tokens, top_k=20)
    print(f"  -> Đã tìm được {len(lexical_candidates)} tài liệu bằng Lexical")

  
    # PHASE 2: HYBRID & RE-RANKING
    print("\n[Phase 2] Chạy Semantic Search (Dense Retrieval)...")
    dense_retriever = DenseRetriever(index_dir)
    dense_candidates = dense_retriever.retrieve(args.query, top_k=20)
    print(f"  -> Đã tìm được {len(dense_candidates)} tài liệu bằng Vector")

    print("[Phase 2] Chạy RRF (Reciprocal Rank Fusion)...")
    merger = RRFMerger(k=60)
    # Lấy ra Top-10 để đưa vào Cross-Encoder
    top_10_rrf_ids = merger.merge(lexical_candidates, dense_candidates, top_k=10)

    print("[Phase 2] Chạy Cross-Encoder Reranker...")
    reranker = CrossEncoderReranker()
    # Chắt lọc lấy Top-K (Mặc định 3)
    final_ranked_docs = reranker.rerank(args.query, top_10_rrf_ids, corpus_metadata, top_k=args.top_k)


    # PHASE 3: RAG GENERATION
    print("\n[Phase 3] Đang sinh câu trả lời RAG...")
    context = build_context(final_ranked_docs)
    generator = AnswerGenerator(use_llm=args.use_llm)
    answer = generator.generate(args.query, context)


    # KẾT QUẢ
    print(f"\n Hoàn thành trong {time.time() - start_time:.2f} giây\n")
    print("="*60)
    print("TRẢ LỜI:")
    print("="*60)
    print(answer)
    print("="*60)
    
    print("\n CÁC TÀI LIỆU TOP ĐẦU ĐƯỢC TRÍCH XUẤT:")
    for i, res in enumerate(final_ranked_docs):
        print(f"\n{i+1}. [{res['score']:.4f}] {res['title']}")
        print(f"   Chuyên mục: {res['category']}")
        print(f"   URL: {res['url']}")
        print(f"   Trích đoạn: {res.get('snippet', '')}")

if __name__ == "__main__":
    main()
