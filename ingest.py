#!/usr/bin/env python3
"""
Ingestion pipeline for Personal Learning Portal
Loads .txt, .md, and small PDFs from data/, chunks, embeds, and builds FAISS index
"""
import sys
from pathlib import Path
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
)
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

import config


def load_documents(data_dir: Path) -> List[Document]:
    """Load all supported documents from data directory."""
    documents = []
    
    # Supported extensions
    text_exts = [".txt", ".md"]
    pdf_ext = ".pdf"
    
    for file_path in data_dir.iterdir():
        if not file_path.is_file():
            continue
            
        try:
            if file_path.suffix.lower() in text_exts:
                # Use TextLoader for both .txt and .md files
                loader = TextLoader(str(file_path), encoding="utf-8")
                docs = loader.load()
                
                # Add source metadata
                for doc in docs:
                    doc.metadata["source"] = file_path.name
                    doc.metadata["type"] = file_path.suffix[1:]
                    
                documents.extend(docs)
                print(f"✓ Loaded {len(docs)} document(s) from {file_path.name}")
                
            elif file_path.suffix.lower() == pdf_ext:
                # Check file size (skip if > 30MB)
                if file_path.stat().st_size > 30 * 1024 * 1024:
                    print(f"⊘ Skipping {file_path.name} (exceeds 30MB)")
                    continue
                    
                loader = PyPDFLoader(str(file_path))
                docs = loader.load()
                
                # Add source metadata
                for doc in docs:
                    doc.metadata["source"] = file_path.name
                    doc.metadata["type"] = "pdf"
                    
                documents.extend(docs)
                print(f"✓ Loaded {len(docs)} page(s) from {file_path.name}")
                
        except Exception as e:
            print(f"✗ Error loading {file_path.name}: {e}")
            continue
    
    return documents


def chunk_documents(documents: List[Document]) -> List[Document]:
    """Split documents into chunks using RecursiveCharacterTextSplitter."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"\n✓ Split {len(documents)} documents into {len(chunks)} chunks")
    print(f"  (chunk_size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP})")
    
    return chunks


def build_faiss_index(chunks: List[Document]) -> FAISS:
    """Embed chunks and build FAISS index."""
    print(f"\n⚙ Embedding {len(chunks)} chunks with {config.EMBEDDING_MODEL}...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    # Build FAISS index
    vectorstore = FAISS.from_documents(chunks, embeddings)
    print(f"✓ FAISS index built successfully")
    
    return vectorstore


def save_index(vectorstore: FAISS, index_path: Path) -> None:
    """Save FAISS index to disk."""
    vectorstore.save_local(str(index_path), index_name="faiss_index")
    print(f"✓ FAISS index saved to {index_path}")


def main():
    """Main ingestion pipeline."""
    print("=" * 60)
    print("Personal Learning Portal - Ingestion Pipeline")
    print("=" * 60)
    
    # Check if data directory exists and has files
    if not config.DATA_DIR.exists():
        print(f"✗ Data directory not found: {config.DATA_DIR}")
        sys.exit(1)
    
    files = list(config.DATA_DIR.glob("*"))
    if len(files) <= 1:  # Only .gitkeep
        print(f"⚠ Warning: No data files found in {config.DATA_DIR}")
        print("  Add .txt, .md, or .pdf files to data/ directory")
        sys.exit(1)
    
    # Load documents
    print(f"\n📂 Loading documents from {config.DATA_DIR}...")
    documents = load_documents(config.DATA_DIR)
    
    if not documents:
        print("✗ No documents loaded. Check data/ directory.")
        sys.exit(1)
    
    print(f"\n📊 Summary: {len(documents)} documents loaded")
    
    # Chunk documents
    chunks = chunk_documents(documents)
    
    # Build FAISS index
    vectorstore = build_faiss_index(chunks)
    
    # Save index
    save_index(vectorstore, config.FAISS_INDEX_PATH)
    
    print("\n" + "=" * 60)
    print("✓ Ingestion complete!")
    print(f"  Documents: {len(documents)}")
    print(f"  Chunks: {len(chunks)}")
    print(f"  Index: {config.FAISS_INDEX_PATH}")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run 'make run' to launch the Streamlit app")
    print("  2. Run 'make eval-basic' to evaluate retrieval")
    print("=" * 60)


if __name__ == "__main__":
    main()
