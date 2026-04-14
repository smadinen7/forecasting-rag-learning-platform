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
from rerank import rerank


# =============================================================================
# SESSION HELPERS
# =============================================================================

def _new_session_id() -> str:
    return uuid.uuid4().hex[:8]


def _call_llm_simple(prompt: str, max_tokens: int = 20, temperature: float = 0.3) -> str:
    """Minimal single-turn LLM call (title generation, etc.). Raises on failure."""
    if config.GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=config.GEMINI_API_KEY)
        resp = genai.GenerativeModel(config.GEMINI_MODEL).generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature, max_output_tokens=max_tokens
            ),
        )
        return resp.text.strip().strip('"').strip("'")
    if config.OPENAI_API_KEY:
        from openai import OpenAI
        resp = OpenAI(api_key=config.OPENAI_API_KEY).chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip().strip('"').strip("'")
    raise RuntimeError("No LLM provider configured")


def build_retrieval_query(current_query: str, messages: list) -> str:
    """
    Expand a vague follow-up query with the prior user topic so FAISS retrieves
    the right documents. E.g. 'Show me Python code for that' + prior 'What is GARCH?'
    → 'What is GARCH? Show me Python code for that'.
    """
    last_user = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"), None
    )
    if last_user is None:
        return current_query
    words = current_query.lower().split()
    vague_indicators = {"that", "it", "this", "those", "these", "them"}
    if len(words) <= 8 or bool(vague_indicators & set(words[:5])):
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


def generate_session_title(user_msg: str, assistant_msg: str) -> str:
    """Generate a 4-6 word title for a session using the configured LLM."""
    prompt = (
        "Generate a concise 4-6 word title (no quotes, no punctuation) that "
        f"summarizes this conversation.\nUser: {user_msg[:300]}\n"
        f"Assistant: {assistant_msg[:300]}\nTitle:"
    )
    try:
        return _call_llm_simple(prompt)
    except Exception:
        return (user_msg[:45].rstrip() + "...") if len(user_msg) > 45 else user_msg


def save_session(session_id: str, messages: list, title: str = "", date_str: str = ""):
    """
    Overwrite the session file with all messages so the full conversation
    can be restored. A 'meta' entry at the top stores the session title.
    date_str should be the session START date so cross-midnight chats stay
    in one file.
    """
    if not messages:
        return
    if not date_str:
        date_str = datetime.now().strftime("%Y%m%d")
    path = config.SESSIONS_DIR / f"{date_str}_{session_id}.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "role": "meta",
            "session_id": session_id,
            "title": title,
            "timestamp": datetime.now().isoformat(),
        }) + "\n")
        for msg in messages:
            f.write(json.dumps({
                "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                "session_id": session_id,
                "role": msg["role"],
                "content": msg["content"],
                "sources": [d.metadata.get("source", "?") for d in msg.get("docs", [])]
                           or msg.get("sources", []),
            }) + "\n")


def load_session(path: Path) -> list:
    """Reconstruct message list from a session JSONL file (skips meta entry)."""
    messages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            if entry.get("role") == "meta":
                continue
            messages.append({
                "role": entry["role"],
                "content": entry["content"],
                "docs": [],
                "sources": entry.get("sources", []),
                "timestamp": entry.get("timestamp", ""),
            })
    return messages


@st.cache_data(ttl=30)
def load_recent_sessions() -> list:
    """Return metadata list for sessions from the last 7 days, newest first."""
    cutoff = datetime.now() - timedelta(days=7)
    sessions = []
    for p in config.SESSIONS_DIR.glob("*.jsonl"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                lines = [json.loads(line) for line in f if line.strip()]
            if not lines:
                continue
            meta = lines[0] if lines[0].get("role") == "meta" else {}
            ts_str = meta.get("timestamp") or lines[0].get("timestamp", "")
            ts = datetime.fromisoformat(ts_str)
            if ts < cutoff:
                continue
            sid = meta.get("session_id") or lines[0].get("session_id", "")
            title = meta.get("title", "")
            if not title:
                first_user = next(
                    (ln["content"] for ln in lines if ln.get("role") == "user"), ""
                )
                title = (first_user[:45] + "...") if len(first_user) > 45 else first_user
            sessions.append({
                "session_id": sid,
                "date": ts.strftime("%b %d %H:%M"),
                "date_str": ts.strftime("%Y%m%d"),
                "ts": ts,
                "title": title or "Untitled session",
                "turn_count": sum(1 for ln in lines if ln.get("role") == "assistant"),
                "path": str(p),
            })
        except Exception:
            continue
    return sorted(sessions, key=lambda s: s["ts"], reverse=True)[:10]


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

        context_parts = []
        for i, doc in enumerate(context_docs[:config.TOP_K], 1):
            context_parts.append(
                f"[{i}] Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}"
            )
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

        context_parts = []
        for i, doc in enumerate(context_docs[:config.TOP_K], 1):
            context_parts.append(
                f"[{i}] Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}"
            )
        context_str = "\n\n".join(context_parts)
        prior_block = f"\n{prior_context}\n" if prior_context else ""

        response = OpenAI(api_key=config.OPENAI_API_KEY).chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": config.SYSTEM_PROMPT},
                {"role": "user", "content": f"""{prior_block}QUERY: {query}

CONTEXT:
{context_str}

Provide a concise answer with citations [1], [2], etc."""},
            ],
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
        snippet = doc.page_content[:300].strip()
        if len(doc.page_content) > 300:
            snippet += "..."
        bullets.append(f"**[{i}] {doc.metadata.get('source', 'Unknown')}**\n{snippet}")
    return "\n\n".join(bullets)


def generate_answer(
    query: str, context_docs: List[Document], prior_context: str = ""
) -> Tuple[str, str]:
    """Route to Gemini/OpenAI/extractive. Returns (answer, provider_used)."""
    if config.PROVIDER == "gemini" and config.GEMINI_API_KEY:
        answer, success = answer_with_gemini(query, context_docs, prior_context)
        if success:
            return answer, "gemini"

    if config.PROVIDER == "openai" and config.OPENAI_API_KEY:
        answer, success = answer_with_openai(query, context_docs, prior_context)
        if success:
            return answer, "openai"

    # OpenAI fallback when Gemini is configured but failed
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
    date_str = datetime.now().strftime("%Y%m%d")
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "answer": answer,
        "provider": provider,
        "top_k": config.TOP_K,
        "use_reranker": config.USE_RERANKER,
        "config_hash": hashlib.md5(str(config.__dict__).encode()).hexdigest()[:8],
        "sources": [doc.metadata.get("source", "Unknown") for doc in docs[:config.TOP_K]],
        "survey": survey_data,
    }
    with open(config.LOGS_DIR / f"run_{date_str}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


# =============================================================================
# ANALYTICS
# =============================================================================

@st.cache_data(ttl=300)
def compute_analytics() -> Dict[str, Any]:
    """Compute weekly analytics from logs (cached 5 min)."""
    cutoff_date = datetime.now() - timedelta(days=config.ANALYTICS_WINDOW_DAYS)
    interactions = []
    for log_file in config.LOGS_DIR.glob("run_*.jsonl"):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date:
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
    survey_entries = [x for x in interactions if x.get("survey")]

    if survey_entries:
        helpful_rate = sum(
            1 for x in survey_entries if x["survey"].get("helpful") == "Yes"
        ) / len(survey_entries)
        novelties = [x["survey"].get("novelty", 0) for x in survey_entries]
        avg_novelty = sum(novelties) / len(novelties)
        confidences = [x["survey"].get("confidence", 0) for x in survey_entries]
        avg_confidence = sum(confidences) / len(confidences)
    else:
        helpful_rate = avg_novelty = avg_confidence = None

    if helpful_rate is None:
        next_action = "No feedback collected yet"
    elif helpful_rate < 0.6:
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

@st.cache_resource
def load_vectorstore() -> Optional[FAISS]:
    """Load FAISS index (cached for the process lifetime)."""
    if not config.FAISS_INDEX_PATH.exists():
        return None
    embeddings = HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    return FAISS.load_local(
        str(config.FAISS_INDEX_PATH),
        embeddings,
        index_name="faiss_index",
        allow_dangerous_deserialization=True,
    )


def _render_sources(docs: List[Document], sources: List[str]) -> None:
    """Render a Sources expander from either full Document objects or filename strings."""
    items = docs[:config.TOP_K] if docs else sources[:config.TOP_K]
    if not items:
        return
    with st.expander("Sources"):
        for i, item in enumerate(items, 1):
            if isinstance(item, Document):
                snippet = item.page_content[:250].strip()
                if len(item.page_content) > 250:
                    snippet += "..."
                st.caption(f"**[{i}] {item.metadata.get('source', '?')}**")
                st.text(snippet)
            else:
                st.caption(f"**[{i}] {item}**")


def main():
    st.set_page_config(
        page_title="Personal Learning Portal",
        page_icon="📚",
        layout="wide",
    )

    st.title("📚 Personal Learning Portal")
    st.caption("Corporate Forecasting & Structural Breaks")

    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("session_id", _new_session_id())
    st.session_state.setdefault("session_title", "")
    st.session_state.setdefault("session_date", datetime.now().strftime("%Y%m%d"))
    st.session_state.setdefault("completed_modules", set())
    st.session_state.setdefault("current_path", None)

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

        if st.button("🆕 New Chat"):
            st.session_state.messages = []
            st.session_state.session_id = _new_session_id()
            st.session_state.session_title = ""
            st.session_state.session_date = datetime.now().strftime("%Y%m%d")
            st.rerun()

        st.subheader("📈 Analytics")
        analytics = compute_analytics()
        st.metric("Total Queries", analytics["total_queries"])
        if analytics["helpful_rate"] is not None:
            st.metric("Helpful Rate", f"{analytics['helpful_rate']:.1%}")
        if analytics["total_queries"] > 0:
            st.caption(f"💡 {analytics['next_action']}")

        st.divider()

        st.subheader("🕐 Recent Sessions")
        recent = load_recent_sessions()
        if recent:
            for s in recent:
                col_title, col_del = st.columns([5, 1])
                with col_title:
                    if st.button(s["title"], key=f"sess_{s['session_id']}"):
                        st.session_state.messages = load_session(Path(s["path"]))
                        st.session_state.session_id = s["session_id"]
                        st.session_state.session_title = s["title"]
                        st.session_state.session_date = s["date_str"]
                        load_recent_sessions.clear()
                        st.rerun()
                with col_del:
                    if st.button("🗑", key=f"del_{s['session_id']}"):
                        Path(s["path"]).unlink(missing_ok=True)
                        if st.session_state.session_id == s["session_id"]:
                            st.session_state.messages = []
                            st.session_state.session_id = _new_session_id()
                            st.session_state.session_title = ""
                        load_recent_sessions.clear()
                        st.rerun()
                st.caption(
                    f"{s['date']} · {s['turn_count']} turn{'s' if s['turn_count'] != 1 else ''}"
                )
        else:
            st.caption("No sessions yet.")

    # =========================================================================
    # MAIN: Chat UI
    # =========================================================================

    if vectorstore is None:
        st.error("⚠️ FAISS index not found. Run `make ingest` first.")
        st.stop()

    st.header("💬 Ask about Forecasting & Structural Breaks")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                _render_sources(msg.get("docs", []), msg.get("sources", []))

    if prompt := st.chat_input("Ask about time series forecasting..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

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
                    st.session_state.messages[:-1],  # excludes just-appended user msg
                    config.MAX_CONV_TURNS,
                )
                answer, provider = generate_answer(prompt, reranked_docs, prior_context)

            st.markdown(answer)
            st.caption(f"*Provider: {provider}*")
            _render_sources(reranked_docs, [])

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "docs": reranked_docs,
            "provider": provider,
            "timestamp": datetime.now().isoformat(),
        })
        log_interaction(prompt, answer, reranked_docs, provider)

        # Title generated once on the first turn, reused on subsequent turns
        if sum(1 for m in st.session_state.messages if m["role"] == "assistant") == 1:
            st.session_state.session_title = generate_session_title(prompt, answer)
        save_session(
            st.session_state.session_id,
            st.session_state.messages,
            title=st.session_state.session_title,
            date_str=st.session_state.session_date,
        )
        load_recent_sessions.clear()

    st.divider()
    st.caption(
        "💡 Tip: Complete modules to unlock learning paths. "
        "Run `make eval-basic` and `make eval-judge` for detailed metrics."
    )


if __name__ == "__main__":
    main()
