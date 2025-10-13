"""
Simple reranking module for retrieved documents
Implements cosine similarity and BM25-style scoring
"""
from typing import List
import numpy as np
from langchain.schema import Document

import config


def rerank(query: str, documents: List[Document]) -> List[Document]:
    """
    Rerank documents based on query relevance.
    
    Args:
        query: User query string
        documents: List of retrieved documents
        
    Returns:
        Reranked list of documents (if USE_RERANKER=True), otherwise original list
    """
    if not config.USE_RERANKER or not documents:
        return documents
    
    # Simple cosine similarity reranking (placeholder)
    # In practice, this would use a more sophisticated scorer
    scores = []
    query_lower = query.lower()
    query_terms = set(query_lower.split())
    
    for doc in documents:
        doc_text = doc.page_content.lower()
        doc_terms = set(doc_text.split())
        
        # Simple term overlap score (BM25 approximation)
        overlap = len(query_terms & doc_terms)
        doc_length = len(doc_terms)
        
        # Normalize by document length
        score = overlap / (doc_length + 1) if doc_length > 0 else 0
        
        # Bonus for exact phrase match
        if query_lower in doc_text:
            score += 0.5
        
        scores.append(score)
    
    # Sort documents by score (descending)
    scored_docs = list(zip(scores, documents))
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    
    # Return reranked documents
    reranked = [doc for score, doc in scored_docs]
    
    return reranked


def compute_relevance_scores(query: str, documents: List[Document]) -> List[float]:
    """
    Compute relevance scores for documents without reordering.
    
    Args:
        query: User query string
        documents: List of documents
        
    Returns:
        List of relevance scores (0-1 range)
    """
    if not documents:
        return []
    
    query_lower = query.lower()
    query_terms = set(query_lower.split())
    
    scores = []
    for doc in documents:
        doc_text = doc.page_content.lower()
        doc_terms = set(doc_text.split())
        
        # Term overlap ratio
        if len(query_terms) == 0:
            score = 0.0
        else:
            overlap = len(query_terms & doc_terms)
            score = overlap / len(query_terms)
        
        # Exact match bonus
        if query_lower in doc_text:
            score = min(1.0, score + 0.3)
        
        scores.append(score)
    
    return scores
