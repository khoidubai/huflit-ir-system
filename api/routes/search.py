from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import time

from retrieval.query_processor import process_query
from retrieval.lexical_retrieval import RankedRetrieval
from retrieval.embedder import DenseRetriever
from retrieval.rrf_merge import RRFMerger
from retrieval.reranker import CrossEncoderReranker
from rag.context_builder import build_context
from rag.answer_generator import AnswerGenerator
import json

router = APIRouter()

# Schema
class SearchRequest(BaseModel):
    query: str
    top_k: int = 3
    use_llm: bool = True

class SearchResponse(BaseModel):
    query: str
    answer: str
    results: List[dict]
    total_time_ms: int

# Khởi tạo modules
index_dir = "data/index"
corpus_path = "data/processed/corpus.json"
with open(corpus_path, "r", encoding="utf-8") as f:
    corpus = json.load(f)
    corpus_metadata = {doc.get('id', f"huflit_{i+1:04d}"): doc for i, doc in enumerate(corpus)}

lexical_retriever = RankedRetrieval(index_dir)
dense_retriever = DenseRetriever(index_dir)
rrf_merger = RRFMerger(k=60)
cross_encoder_reranker = CrossEncoderReranker()

@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    start_time = time.time()
    
    # 1. Pipeline Lexical
    tokens = process_query(request.query)
    lexical_candidates = lexical_retriever.get_candidates(tokens, top_k=20)
    
    # 2. Pipeline Dense Vectors
    dense_candidates = dense_retriever.retrieve(request.query, top_k=20)
    
    # 3. RRF Merge
    top_10_rf_ids = rrf_merger.merge(lexical_candidates, dense_candidates, top_k=10)
    
    # 4. Neural Re-ranking top 3
    final_ranked_docs = cross_encoder_reranker.rerank(request.query, top_10_rf_ids, corpus_metadata, top_k=request.top_k)
    
    # 5. Build Context and Ask LLM
    context = build_context(final_ranked_docs)
    generator = AnswerGenerator(use_llm=request.use_llm)
    answer = generator.generate(request.query, context)
    
    total_time_ms = int((time.time() - start_time) * 1000)
    
    return SearchResponse(
        query=request.query,
        answer=answer,
        results=final_ranked_docs,
        total_time_ms=total_time_ms
    )
