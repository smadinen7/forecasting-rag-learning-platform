"""
Test retrieval functionality
"""
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from rerank import rerank, compute_relevance_scores


@pytest.fixture
def vectorstore():
    """Load FAISS vectorstore for testing."""
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
    
    return vectorstore


def test_similarity_search_returns_docs(vectorstore):
    """Test that similarity search returns documents."""
    query = "What are structural breaks?"
    docs = vectorstore.similarity_search(query, k=5)
    
    assert len(docs) > 0, "No documents returned"
    assert len(docs) <= 5, "Too many documents returned"


def test_retrieved_docs_have_metadata(vectorstore):
    """Test that retrieved documents have source metadata."""
    query = "regime-switching models"
    docs = vectorstore.similarity_search(query, k=3)
    
    for doc in docs:
        assert "source" in doc.metadata, f"Document missing 'source' metadata: {doc.metadata}"
        assert doc.metadata["source"], "Source metadata is empty"


def test_retrieved_docs_have_content(vectorstore):
    """Test that retrieved documents have non-empty content."""
    query = "forecasting evaluation metrics"
    docs = vectorstore.similarity_search(query, k=3)
    
    for doc in docs:
        assert doc.page_content, "Document has empty content"
        assert len(doc.page_content) > 0, "Document content is empty"


def test_reranker_preserves_count(vectorstore):
    """Test that reranker returns same number of docs."""
    query = "nowcasting"
    docs = vectorstore.similarity_search(query, k=10)
    
    reranked = rerank(query, docs)
    
    assert len(reranked) == len(docs), "Reranker changed document count"


def test_reranker_returns_same_docs(vectorstore):
    """Test that reranker returns same documents (possibly reordered)."""
    query = "break detection methods"
    docs = vectorstore.similarity_search(query, k=5)
    
    reranked = rerank(query, docs)
    
    # Check that same documents are present (by content)
    original_contents = {doc.page_content for doc in docs}
    reranked_contents = {doc.page_content for doc in reranked}
    
    assert original_contents == reranked_contents, "Reranker changed document set"


def test_relevance_scores_in_range(vectorstore):
    """Test that relevance scores are in [0, 1] range."""
    query = "governance framework"
    docs = vectorstore.similarity_search(query, k=5)
    
    scores = compute_relevance_scores(query, docs)
    
    assert len(scores) == len(docs), "Score count doesn't match document count"
    
    for score in scores:
        assert 0.0 <= score <= 1.0, f"Score {score} out of range [0, 1]"


def test_retrieval_config():
    """Test that retrieval configuration is valid."""
    assert config.K_CANDIDATES > 0, "K_CANDIDATES must be positive"
    assert config.TOP_K > 0, "TOP_K must be positive"
    assert config.TOP_K <= config.K_CANDIDATES, "TOP_K must be <= K_CANDIDATES"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
