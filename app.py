#!/usr/bin/env python3
"""
Personal Learning Portal - Streamlit App
RAG Q&A with Gemini/OpenAI/extractive fallback, multi-turn chat, session history,
modules, paths, and analytics.
"""
import json
import uuid
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
# SESSION HELPERS
# =============================================================================

def _new_session_id() -> str:
    return uuid.uuid4().hex[:8]


def build_retrieval_query(current_query: str, messages: list) -> str:
    """
    Expand a vague follow-up query with the prior user topic so FAISS retrieves
    the right documents. E.g. 'Show me Python code for that' + prior 'What is GARCH?'
    → 'What is GARCH? Show me Python code for that'.
    """
    if not messages:
        return current_query
    prior_user_msgs = [m for m in messages if m["role"] == "user"]
    if not prior_user_msgs:
        return current_query
    last_user = prior_user_msgs[-1]["content"]
    words = current_query.lower().split()
    vague_indicators = {"that", "it", "this", "those", "these", "them"}
    is_vague = len(words) <= 8 or bool(vague_indicators & set(words[:5]))
    if is_vague:
        return f"{last_user} {current_query}"
    return current_query


def build_prior_context(messages: list, max_turns: int) -> str:
    """Return last max_turns Q&A pairs as a formatted string for the LLM prompt."""
    qa_messages = [m for m in messages if m["role"] in ("user", "assistant")]
    tail = qa_messages[-(max_turns * 2):]
    if not tail:
        return ""
    lines = ["Prior conversation:"]
    for m in tail:
        label = "User" if m["role"] == "user" else "Assistant"
        lines.append(f"{label}: {m['content']}")
    return "\n".join(lines)


def save_session(session_id: str, messages: list):
    """
    Overwrite the session file with all messages so the full conversation
    can be restored. Saves both user and assistant turns.
    """
    if not messages:
        return
    date_str = datetime.now().strftime("%Y%m%d")
    path = config.SESSIONS_DIR / f"{date_str}_{session_id}.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for msg in messages:
            entry = {
                "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                "session_id": session_id,
                "role": msg["role"],
                "content": msg["content"],
                "sources": [
                    d.metadata.get("source", "?") for d in msg.get("docs", [])
                ],
            }
            f.write(json.dumps(entry) + "\n")


def load_session(path: Path) -> list:
    """Reconstruct message list from a session JSONL file."""
    messages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            messages.append({
                "role": entry["role"],
                "content": entry["content"],
                "docs": [],  # docs not serialized; sources shown as text below
                "sources": entry.get("sources", []),
                "timestamp": entry.get("timestamp", ""),
            })
    return messages


def load_recent_sessions() -> list:
    """Return metadata list for sessions from the last 7 days."""
    cutoff = datetime.now() - timedelta(days=7)
    sessions = {}
    for p in sorted(config.SESSIONS_DIR.glob("*.jsonl"), reverse=True):
        try:
            with open(p, "r", encoding="utf-8") as f:
                lines = [json.loads(line) for line in f if line.strip()]
            if not lines:
                continue
            ts = datetime.fromisoformat(lines[0]["timestamp"])
            if ts < cutoff:
                continue
            sid = lines[0]["session_id"]
            # Show first user message as the session preview
            first_user = next(
                (ln["content"] for ln in lines if ln.get("role") == "user"), "?"
            )
            turn_count = len([ln for ln in lines if ln.get("role") == "assistant"])
            sessions[sid] = {
                "session_id": sid,
                "date": ts.strftime("%b %d %H:%M"),
                "first_query": first_user,
                "turn_count": turn_count,
                "path": str(p),
            }
        except Exception:
            continue
    return list(sessions.values())[:10]


# =============================================================================
# LLM PROVIDERS
# =============================================================================

def answer_with_gemini(
    query: str, context_docs: List[Document], prior_context: str = ""
) -> Tuple[str, bool]:
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
        prior_block = f"\n{prior_context}\n" if prior_context else ""

        prompt = f"""{config.SYSTEM_PROMPT}
{prior_block}
QUERY: {query}

CONTEXT:
{context_str}

Provide a concise answer with citations [1], [2], etc."""

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=config.TEMPERATURE,
                max_output_tokens=config.MAX_TOKENS,
            ),
        )

        return response.text.strip(), True

    except Exception as e:
        st.error(f"Gemini API error: {e}")
        return "", False


def answer_with_openai(
    query: str, context_docs: List[Document], prior_context: str = ""
) -> Tuple[str, bool]:
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
        prior_block = f"\n{prior_context}\n" if prior_context else ""

        messages = [
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""{prior_block}QUERY: {query}

CONTEXT:
{context_str}

Provide a concise answer with citations [1], [2], etc.""",
            },
        ]

        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=messages,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
        )

        return response.choices[0].message.content.strip(), True

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


def generate_answer(
    query: str, context_docs: List[Document], prior_context: str = ""
) -> Tuple[str, str]:
    """
    Generate answer using configured provider (Gemini/OpenAI/extractive).

    Returns:
        (answer, provider_used)
    """
    if config.PROVIDER == "gemini" and config.GEMINI_API_KEY:
        answer, success = answer_with_gemini(query, context_docs, prior_context)
        if success:
            return answer, "gemini"

    if config.PROVIDER == "openai" and config.OPENAI_API_KEY:
        answer, success = answer_with_openai(query, context_docs, prior_context)
        if success:
            return answer, "openai"

    # Try OpenAI as fallback if Gemini was requested but failed
    if config.PROVIDER == "gemini" and config.OPENAI_API_KEY:
        answer, success = answer_with_openai(query, context_docs, prior_context)
        if success:
            return answer, "openai (fallback)"

    return answer_extractive(context_docs), "extractive"


# =============================================================================
# LOGGING
# =============================================================================

def log_interaction(
    query: str,
    answer: str,
    docs: List[Document],
    provider: str,
    survey_data: Optional[Dict] = None,
):
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
        "survey": survey_data,
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
            "next_action": "Submit queries to collect data",
        }

    total = len(interactions)
    helpful_count = sum(
        1 for x in interactions if x.get("survey", {}) and x["survey"].get("helpful") == "Yes"
    )
    helpful_rate = helpful_count / total if total > 0 else 0.0

    novelties = [
        x["survey"].get("novelty", 0) for x in interactions if x.get("survey")
    ]
    avg_novelty = sum(novelties) / len(novelties) if novelties else 0.0

    confidences = [
        x["survey"].get("confidence", 0) for x in interactions if x.get("survey")
    ]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

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
        "next_action": next_action,
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
        encode_kwargs={"normalize_embeddings": True},
    )

    vectorstore = FAISS.load_local(
        str(config.FAISS_INDEX_PATH),
        embeddings,
        index_name="faiss_index",
        allow_dangerous_deserialization=True,
    )

    return vectorstore


def main():
    st.set_page_config(
        page_title="Personal Learning Portal",
        page_icon="📚",
        layout="wide",
    )

    st.title("📚 Personal Learning Portal")
    st.caption("Corporate Forecasting & Structural Breaks")

    # -------------------------------------------------------------------------
    # Session state init
    # -------------------------------------------------------------------------
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("session_id", _new_session_id())
    st.session_state.setdefault("completed_modules", set())
    st.session_state.setdefault("current_path", None)

    # Load vectorstore once per session
    vectorstore = load_vectorstore()

    # =========================================================================
    # SIDEBAR
    # =========================================================================
    with st.sidebar:
        st.header("🎯 Learning Modules")

        for module in config.MODULES:
            completed = module in st.session_state.completed_modules
            if st.checkbox(f"{module}", value=completed, key=f"module_{module}"):
                st.session_state.completed_modules.add(module)
            elif module in st.session_state.completed_modules:
                st.session_state.completed_modules.remove(module)

        progress = len(st.session_state.completed_modules) / len(config.MODULES)
        st.progress(progress)
        st.caption(
            f"{len(st.session_state.completed_modules)}/{len(config.MODULES)} modules completed"
        )

        st.divider()

        st.header("🗺️ Learning Paths")
        path_options = ["None"] + list(config.PATHS.keys())
        selected_path = st.selectbox(
            "Select Path",
            path_options,
            index=(
                0
                if st.session_state.current_path is None
                else path_options.index(st.session_state.current_path)
            ),
        )

        if selected_path != "None":
            st.session_state.current_path = selected_path
            path_info = config.PATHS[selected_path]
            st.info(f"**{selected_path}**\n\n{path_info['description']}")
            required = path_info["required_modules"]
            st.caption(f"Required: {', '.join(required)}")
            if all(m in st.session_state.completed_modules for m in required):
                st.success("✅ Path Complete!")
        else:
            st.session_state.current_path = None

        st.divider()

        st.caption(f"**Provider:** {config.PROVIDER}")
        st.caption(f"**Reranker:** {'ON' if config.USE_RERANKER else 'OFF'}")
        st.caption(f"**Top-K:** {config.TOP_K}")

        st.divider()

        # New Chat button
        if st.button("🆕 New Chat"):
            st.session_state.messages = []
            st.session_state.session_id = _new_session_id()
            st.rerun()

        # Analytics summary
        st.subheader("📈 Analytics")
        analytics = compute_analytics()
        st.metric("Total Queries", analytics["total_queries"])
        st.metric("Helpful Rate", f"{analytics['helpful_rate']:.1%}")
        if analytics["total_queries"] > 0:
            st.caption(f"💡 {analytics['next_action']}")

        st.divider()

        # Recent sessions
        st.subheader("🕐 Recent Sessions")
        recent = load_recent_sessions()
        if recent:
            for s in recent:
                label = f"{s['date']} · {s['first_query'][:40]}..."
                if st.button(label, key=f"sess_{s['session_id']}"):
                    restored = load_session(Path(s["path"]))
                    st.session_state.messages = restored
                    st.session_state.session_id = s["session_id"]
                    st.rerun()
                st.caption(f"{s['turn_count']} turn{'s' if s['turn_count'] != 1 else ''}")
        else:
            st.caption("No sessions yet.")

    # =========================================================================
    # MAIN: Chat UI
    # =========================================================================

    if vectorstore is None:
        st.error("⚠️ FAISS index not found. Run `make ingest` first.")
        st.stop()

    st.header("💬 Ask about Forecasting & Structural Breaks")

    # Render existing conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                # Full docs available (live session)
                if msg.get("docs"):
                    with st.expander("Sources"):
                        for i, doc in enumerate(msg["docs"][:config.TOP_K], 1):
                            src = doc.metadata.get("source", "?")
                            snippet = doc.page_content[:250].strip()
                            if len(doc.page_content) > 250:
                                snippet += "..."
                            st.caption(f"**[{i}] {src}**")
                            st.text(snippet)
                # Source names only (restored session)
                elif msg.get("sources"):
                    with st.expander("Sources"):
                        for i, src in enumerate(msg["sources"][:config.TOP_K], 1):
                            st.caption(f"**[{i}] {src}**")

    # Chat input
    if prompt := st.chat_input("Ask about time series forecasting..."):
        # Append user message and show it immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Retrieve + generate
        with st.chat_message("assistant"):
            with st.spinner("Retrieving and generating answer..."):
                retrieval_query = build_retrieval_query(
                    prompt, st.session_state.messages[:-1]
                )
                candidate_docs = vectorstore.similarity_search(
                    retrieval_query, k=config.K_CANDIDATES
                )
                reranked_docs = rerank(prompt, candidate_docs)
                prior_context = build_prior_context(
                    st.session_state.messages[:-1],  # exclude just-appended user msg
                    config.MAX_CONV_TURNS,
                )
                answer, provider = generate_answer(prompt, reranked_docs, prior_context)

            st.markdown(answer)
            st.caption(f"*Provider: {provider}*")

            if reranked_docs:
                with st.expander("Sources"):
                    for i, doc in enumerate(reranked_docs[:config.TOP_K], 1):
                        src = doc.metadata.get("source", "?")
                        snippet = doc.page_content[:250].strip()
                        if len(doc.page_content) > 250:
                            snippet += "..."
                        st.caption(f"**[{i}] {src}**")
                        st.text(snippet)

        # Persist to session state and disk
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "docs": reranked_docs,
                "provider": provider,
                "timestamp": datetime.now().isoformat(),
            }
        )
        log_interaction(prompt, answer, reranked_docs, provider)
        save_session(st.session_state.session_id, st.session_state.messages)

    # Footer
    st.divider()
    st.caption(
        "💡 Tip: Complete modules to unlock learning paths. "
        "Run `make eval-basic` and `make eval-judge` for detailed metrics."
    )


if __name__ == "__main__":
    main()
