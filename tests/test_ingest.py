"""
Test ingestion pipeline
"""
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def test_data_directory_exists():
    """Test that data directory exists."""
    assert config.DATA_DIR.exists(), f"Data directory not found: {config.DATA_DIR}"


def test_data_directory_has_files():
    """Test that data directory contains files."""
    files = list(config.DATA_DIR.glob("*.md")) + list(config.DATA_DIR.glob("*.txt"))
    assert len(files) > 0, "No .md or .txt files found in data directory"


def test_faiss_index_exists():
    """Test that FAISS index was created."""
    assert config.FAISS_INDEX_PATH.exists(), f"FAISS index not found: {config.FAISS_INDEX_PATH}"


def test_faiss_index_loads():
    """Test that FAISS index can be loaded."""
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
    
    assert vectorstore is not None, "Failed to load FAISS index"


def test_faiss_index_has_vectors():
    """Test that FAISS index contains vectors."""
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
    
    # Check that we can retrieve documents
    docs = vectorstore.similarity_search("structural breaks", k=1)
    assert len(docs) > 0, "FAISS index returned no documents"
    assert docs[0].page_content, "Retrieved document has no content"


def test_chunking_config():
    """Test that chunking configuration is valid."""
    assert config.CHUNK_SIZE > 0, "CHUNK_SIZE must be positive"
    assert config.CHUNK_OVERLAP >= 0, "CHUNK_OVERLAP must be non-negative"
    assert config.CHUNK_OVERLAP < config.CHUNK_SIZE, "CHUNK_OVERLAP must be less than CHUNK_SIZE"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
