#!/usr/bin/env python3
"""
Personal Learning Portal - Streamlit App
RAG Q&A with Gemini/OpenAI/extractive fallback, modules, paths, micro-survey, analytics
"""
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

import config
from rerank import rerank, compute_relevance_scores


# =============================================================================
# LLM PROVIDERS
# =============================================================================

def answer_with_gemini(query: str, context_docs: List[Document]) -> Tuple[str, bool]:
    """Generate answer using Gemini API."""
    try:
        import google.generativeai as genai
        
        if not config.GEMINI_API_KEY:
            return "", False
        
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        
        # Build context string with citations
        context_parts = []
        for i, doc in enumerate(context_docs[:config.TOP_K], 1):
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content
            context_parts.append(f"[{i}] Source: {source}\n{content}")

        context_str = "\n\n".join(context_parts)

        # Construct prompt
        prompt = f"""{config.SYSTEM_PROMPT}

QUERY: {query}

CONTEXT:
{context_str}

Provide a concise answer with citations [1], [2], etc."""
        
        # Generate
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=config.TEMPERATURE,
                max_output_tokens=config.MAX_TOKENS,
            )
        )
        
        answer = response.text.strip()
        return answer, True
        
    except Exception as e:
        st.error(f"Gemini API error: {e}")
        return "", False


def answer_with_openai(query: str, context_docs: List[Document]) -> Tuple[str, bool]:
    """Generate answer using OpenAI API."""
    try:
        from openai import OpenAI
        
        if not config.OPENAI_API_KEY:
            return "", False
        
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Build context string with citations
        context_parts = []
        for i, doc in enumerate(context_docs[:config.TOP_K], 1):
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content
            context_parts.append(f"[{i}] Source: {source}\n{content}")
        
        context_str = "\n\n".join(context_parts)
        
        # Construct messages
        messages = [
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": f"""QUERY: {query}

CONTEXT:
{context_str}

Provide a concise answer with citations [1], [2], etc."""}
        ]
        
        # Generate
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=messages,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
        )
        
        answer = response.choices[0].message.content.strip()
        return answer, True
        
    except Exception as e:
        st.error(f"OpenAI API error: {e}")
        return "", False


def answer_extractive(context_docs: List[Document]) -> str:
    """Fallback: extractive bullet points from top chunks."""
    bullets = []
    for i, doc in enumerate(context_docs[:config.TOP_K], 1):
        source = doc.metadata.get("source", "Unknown")
        snippet = doc.page_content[:300].strip()
        if len(doc.page_content) > 300:
            snippet += "..."
        bullets.append(f"**[{i}] {source}**\n{snippet}")
    
    return "\n\n".join(bullets)


def generate_answer(query: str, context_docs: List[Document]) -> Tuple[str, str]:
    """
    Generate answer using configured provider (Gemini/OpenAI/extractive).
    
    Returns:
        (answer, provider_used)
    """
    if config.PROVIDER == "gemini" and config.GEMINI_API_KEY:
        answer, success = answer_with_gemini(query, context_docs)
        if success:
            return answer, "gemini"
    
    if config.PROVIDER == "openai" and config.OPENAI_API_KEY:
        answer, success = answer_with_openai(query, context_docs)
        if success:
            return answer, "openai"
    
    # Try OpenAI as fallback if Gemini was requested but failed
    if config.PROVIDER == "gemini" and config.OPENAI_API_KEY:
        answer, success = answer_with_openai(query, context_docs)
        if success:
            return answer, "openai (fallback)"
    
    # Extractive fallback
    answer = answer_extractive(context_docs)
    return answer, "extractive"


# =============================================================================
# LOGGING
# =============================================================================

def log_interaction(query: str, answer: str, docs: List[Document], 
                    provider: str, survey_data: Optional[Dict] = None):
    """Log interaction to JSONL file."""
    timestamp = datetime.now().isoformat()
    date_str = datetime.now().strftime("%Y%m%d")
    
    log_entry = {
        "timestamp": timestamp,
        "query": query,
        "answer": answer,
        "provider": provider,
        "top_k": config.TOP_K,
        "use_reranker": config.USE_RERANKER,
        "config_hash": hashlib.md5(str(config.__dict__).encode()).hexdigest()[:8],
        "sources": [doc.metadata.get("source", "Unknown") for doc in docs[:config.TOP_K]],
        "survey": survey_data
    }
    
    log_file = config.LOGS_DIR / f"run_{date_str}.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


# =============================================================================
# ANALYTICS
# =============================================================================

def compute_analytics() -> Dict[str, Any]:
    """Compute weekly analytics from logs."""
    cutoff_date = datetime.now() - timedelta(days=config.ANALYTICS_WINDOW_DAYS)
    
    interactions = []
    for log_file in config.LOGS_DIR.glob("run_*.jsonl"):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                entry_date = datetime.fromisoformat(entry["timestamp"])
                if entry_date >= cutoff_date:
                    interactions.append(entry)
    
    if not interactions:
        return {
            "helpful_rate": 0.0,
            "avg_novelty": 0.0,
            "avg_confidence": 0.0,
            "total_queries": 0,
            "next_action": "Submit queries to collect data"
        }
    
    # Compute metrics
    total = len(interactions)
    helpful_count = sum(1 for x in interactions if x.get("survey", {}).get("helpful") == "Yes")
    helpful_rate = helpful_count / total if total > 0 else 0.0
    
    novelties = [x.get("survey", {}).get("novelty", 0) for x in interactions if x.get("survey")]
    avg_novelty = sum(novelties) / len(novelties) if novelties else 0.0
    
    confidences = [x.get("survey", {}).get("confidence", 0) for x in interactions if x.get("survey")]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    
    # Suggest next action
    if helpful_rate < 0.6:
        next_action = "Review low-helpful queries; add relevant sources or tune prompts"
    elif avg_confidence < 1.0:
        next_action = "Low confidence detected; review answer quality and citations"
    else:
        next_action = "Performance stable; continue monitoring and expand corpus"
    
    return {
        "helpful_rate": helpful_rate,
        "avg_novelty": avg_novelty,
        "avg_confidence": avg_confidence,
        "total_queries": total,
        "next_action": next_action
    }


# =============================================================================
# STREAMLIT APP
# =============================================================================

def load_vectorstore() -> Optional[FAISS]:
    """Load FAISS index."""
    if not config.FAISS_INDEX_PATH.exists():
        return None
    
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


def main():
    st.set_page_config(
        page_title="Personal Learning Portal",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Personal Learning Portal")
    st.caption("Corporate Forecasting & Structural Breaks")
    
    # Initialize session state
    if "completed_modules" not in st.session_state:
        st.session_state.completed_modules = set()
    if "current_path" not in st.session_state:
        st.session_state.current_path = None
    if "show_survey" not in st.session_state:
        st.session_state.show_survey = False
    if "last_answer" not in st.session_state:
        st.session_state.last_answer = None
    if "last_docs" not in st.session_state:
        st.session_state.last_docs = []
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""
    if "last_provider" not in st.session_state:
        st.session_state.last_provider = ""
    
    # Load vectorstore
    vectorstore = load_vectorstore()
    
    # =============================================================================
    # SIDEBAR: Modules, Paths, Progress
    # =============================================================================
    with st.sidebar:
        st.header("🎯 Learning Modules")
        
        # Module checkboxes (gated)
        for module in config.MODULES:
            completed = module in st.session_state.completed_modules
            if st.checkbox(f"{module}", value=completed, key=f"module_{module}"):
                st.session_state.completed_modules.add(module)
            elif module in st.session_state.completed_modules:
                st.session_state.completed_modules.remove(module)
        
        # Progress bar
        progress = len(st.session_state.completed_modules) / len(config.MODULES)
        st.progress(progress)
        st.caption(f"{len(st.session_state.completed_modules)}/{len(config.MODULES)} modules completed")
        
        st.divider()
        
        # Learning paths
        st.header("🗺️ Learning Paths")
        path_options = ["None"] + list(config.PATHS.keys())
        selected_path = st.selectbox(
            "Select Path",
            path_options,
            index=0 if st.session_state.current_path is None else path_options.index(st.session_state.current_path)
        )
        
        if selected_path != "None":
            st.session_state.current_path = selected_path
            path_info = config.PATHS[selected_path]
            st.info(f"**{selected_path}**\n\n{path_info['description']}")
            
            required = path_info["required_modules"]
            st.caption(f"Required: {', '.join(required)}")
            
            path_completed = all(m in st.session_state.completed_modules for m in required)
            if path_completed:
                st.success("✅ Path Complete!")
        else:
            st.session_state.current_path = None
        
        st.divider()
        
        # Config info
        st.caption(f"**Provider:** {config.PROVIDER}")
        st.caption(f"**Reranker:** {'ON' if config.USE_RERANKER else 'OFF'}")
        st.caption(f"**Top-K:** {config.TOP_K}")
    
    # =============================================================================
    # MAIN: RAG Q&A
    # =============================================================================
    
    if vectorstore is None:
        st.error("⚠️ FAISS index not found. Run `make ingest` first.")
        st.stop()
    
    st.header("💬 Ask a Question")
    
    query = st.text_input(
        "Enter your query about forecasting & structural breaks:",
        placeholder="e.g., What are regime-switching models and when should they be used?"
    )
    
    if st.button("🔍 Search", type="primary"):
        if not query.strip():
            st.warning("Please enter a query.")
        else:
            with st.spinner("Retrieving and generating answer..."):
                # Retrieve candidates
                candidate_docs = vectorstore.similarity_search(query, k=config.K_CANDIDATES)
                
                # Optional reranking
                reranked_docs = rerank(query, candidate_docs)
                
                # Generate answer
                answer, provider = generate_answer(query, reranked_docs)
                
                # Store in session for survey
                st.session_state.last_query = query
                st.session_state.last_answer = answer
                st.session_state.last_docs = reranked_docs
                st.session_state.last_provider = provider
                st.session_state.show_survey = True
                
                # Display answer
                st.subheader("📝 Answer")
                st.markdown(answer)
                st.caption(f"*Provider: {provider}*")
                
                # Display citations
                st.subheader("📚 Sources")
                for i, doc in enumerate(reranked_docs[:config.TOP_K], 1):
                    source = doc.metadata.get("source", "Unknown")
                    snippet = doc.page_content[:200].strip()
                    if len(doc.page_content) > 200:
                        snippet += "..."
                    with st.expander(f"[{i}] {source}"):
                        st.text(snippet)
    
    # =============================================================================
    # MICRO-SURVEY
    # =============================================================================
    
    if st.session_state.show_survey and st.session_state.last_answer:
        st.divider()
        st.subheader("📊 Quick Feedback")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            helpful = st.radio("Helpful?", ["Yes", "No"], key="survey_helpful")
        
        with col2:
            novelty = st.slider("Novelty", 0, 2, 1, key="survey_novelty",
                               help="0=Known, 1=Somewhat new, 2=Very novel")
        
        with col3:
            confidence = st.slider("Confidence", 0, 2, 1, key="survey_confidence",
                                  help="0=Low, 1=Medium, 2=High")
        
        if st.button("Submit Feedback"):
            survey_data = {
                "helpful": helpful,
                "novelty": novelty,
                "confidence": confidence
            }
            
            log_interaction(
                st.session_state.last_query,
                st.session_state.last_answer,
                st.session_state.last_docs,
                st.session_state.last_provider,
                survey_data
            )
            
            st.success("✅ Feedback recorded!")
            st.session_state.show_survey = False
    
    # =============================================================================
    # ANALYTICS CARD
    # =============================================================================
    
    st.divider()
    st.header("📈 Weekly Analytics")
    
    analytics = compute_analytics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Helpful Rate", f"{analytics['helpful_rate']:.1%}")
    
    with col2:
        st.metric("Avg Novelty", f"{analytics['avg_novelty']:.1f}/2")
    
    with col3:
        st.metric("Avg Confidence", f"{analytics['avg_confidence']:.1f}/2")
    
    with col4:
        st.metric("Total Queries", analytics['total_queries'])
    
    st.info(f"**Next Best Action:** {analytics['next_action']}")
    
    # Footer
    st.divider()
    st.caption("💡 Tip: Complete modules to unlock learning paths. Run `make eval-basic` and `make eval-judge` for detailed metrics.")


if __name__ == "__main__":
    main()
