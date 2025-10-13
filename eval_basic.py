#!/usr/bin/env python3
"""
Basic evaluation: recall@5 proxy + groundedness proxy
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import yaml

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import config
from rerank import rerank, compute_relevance_scores


def load_queries(queries_file: Path) -> List[Dict[str, Any]]:
    """Load sample queries from YAML."""
    with open(queries_file, "r") as f:
        data = yaml.safe_load(f)
    return data["queries"]


def compute_recall_at_k(retrieved_docs: List[Document], keywords: List[str], k: int = 5) -> float:
    """
    Recall@K proxy: fraction of keywords found in top-k retrieved docs.
    """
    top_k_text = " ".join([doc.page_content.lower() for doc in retrieved_docs[:k]])
    
    found_count = sum(1 for kw in keywords if kw.lower() in top_k_text)
    recall = found_count / len(keywords) if keywords else 0.0
    
    return recall


def compute_groundedness(answer: str, context_docs: List[Document], k: int = 5) -> float:
    """
    Groundedness proxy: average word overlap between answer and top-k context.
    Simple heuristic - not perfect but useful for basic eval.
    """
    if not answer or not context_docs:
        return 0.0
    
    answer_words = set(answer.lower().split())
    context_words = set()
    
    for doc in context_docs[:k]:
        context_words.update(doc.page_content.lower().split())
    
    if not answer_words or not context_words:
        return 0.0
    
    overlap = len(answer_words & context_words)
    groundedness = overlap / len(answer_words)
    
    return min(1.0, groundedness)


def evaluate_retrieval(vectorstore: FAISS, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate retrieval on sample queries.
    """
    results = []
    
    for query_data in queries:
        query_id = query_data["id"]
        question = query_data["question"]
        keywords = query_data["keywords"]
        
        # Retrieve
        candidate_docs = vectorstore.similarity_search(question, k=config.K_CANDIDATES)
        
        # Optional reranking
        reranked_docs = rerank(question, candidate_docs)
        
        # Compute recall@5
        recall = compute_recall_at_k(reranked_docs, keywords, k=config.TOP_K)
        
        # Compute relevance scores
        relevance_scores = compute_relevance_scores(question, reranked_docs[:config.TOP_K])
        avg_relevance = np.mean(relevance_scores) if relevance_scores else 0.0
        
        result = {
            "query_id": query_id,
            "question": question,
            "recall_at_5": round(recall, 3),
            "avg_relevance": round(float(avg_relevance), 3),
            "top_sources": [doc.metadata.get("source", "Unknown") for doc in reranked_docs[:config.TOP_K]]
        }
        
        results.append(result)
        print(f"Query {query_id}: Recall@5={recall:.3f}, Relevance={avg_relevance:.3f}")
    
    # Aggregate metrics
    avg_recall = np.mean([r["recall_at_5"] for r in results])
    avg_relevance = np.mean([r["avg_relevance"] for r in results])
    
    summary = {
        "avg_recall_at_5": round(float(avg_recall), 3),
        "avg_relevance": round(float(avg_relevance), 3),
        "num_queries": len(results),
        "config": {
            "top_k": config.TOP_K,
            "k_candidates": config.K_CANDIDATES,
            "use_reranker": config.USE_RERANKER
        },
        "per_query_results": results
    }
    
    return summary


def main():
    print("=" * 60)
    print("Basic Evaluation - Recall@5 + Groundedness Proxy")
    print("=" * 60)
    
    # Load queries
    queries_file = config.EVAL_DIR / "queries.yaml"
    if not queries_file.exists():
        print(f"✗ Queries file not found: {queries_file}")
        sys.exit(1)
    
    queries = load_queries(queries_file)
    print(f"\n✓ Loaded {len(queries)} queries")
    
    # Load vectorstore
    if not config.FAISS_INDEX_PATH.exists():
        print(f"✗ FAISS index not found: {config.FAISS_INDEX_PATH}")
        print("  Run 'make ingest' first")
        sys.exit(1)
    
    print(f"✓ Loading FAISS index from {config.FAISS_INDEX_PATH}...")
    embeddings = HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    vectorstore = FAISS.load_local(
        str(config.FAISS_INDEX_PATH),
        embeddings,
        index_name="faiss_index",
        allow_dangerous_deserialization=True
    )
    print("✓ FAISS index loaded")
    
    # Evaluate
    print("\n" + "=" * 60)
    print("Evaluating Retrieval...")
    print("=" * 60 + "\n")
    
    summary = evaluate_retrieval(vectorstore, queries)
    
    # Save results
    results_file = config.EVAL_DIR / "results" / "basic_eval.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Avg Recall@5:  {summary['avg_recall_at_5']:.3f}")
    print(f"Avg Relevance: {summary['avg_relevance']:.3f}")
    print(f"Queries:       {summary['num_queries']}")
    print("=" * 60)
    print(f"\n✓ Results saved to {results_file}")
    print("\nNext steps:")
    print("  - Run 'make eval-judge' for LLM-as-judge evaluation")
    print("  - Review per-query results in basic_eval.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
