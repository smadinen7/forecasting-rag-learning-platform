"""
Configuration for Personal Learning Portal (PLP)
Centralizes all knobs: paths, chunking, retrieval, providers, modules, learning paths
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# PATHS
# =============================================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = BASE_DIR / "index"
LOGS_DIR = BASE_DIR / "logs"
EVAL_DIR = BASE_DIR / "eval"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
INDEX_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
EVAL_DIR.mkdir(exist_ok=True)
(EVAL_DIR / "results").mkdir(exist_ok=True)

FAISS_INDEX_PATH = INDEX_DIR / "faiss_index"

# =============================================================================
# CHUNKING & EMBEDDING
# =============================================================================
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# =============================================================================
# RETRIEVAL
# =============================================================================
K_CANDIDATES = 20  # Initial retrieval count
TOP_K = 7          # Final top-k after optional reranking
USE_RERANKER = True   # Toggle simple cosine/BM25 reranking

# =============================================================================
# LLM PROVIDERS
# =============================================================================
PROVIDER = os.getenv("PROVIDER", "gemini").lower()  # "gemini" | "openai" | "none"

# Gemini settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"

# Generation settings
TEMPERATURE = 0.2
MAX_TOKENS = 1500

# =============================================================================
# SYSTEM PROMPTS
# =============================================================================
SYSTEM_PROMPT = """You are an expert tutor for time series analysis and forecasting.

Your scope covers the full breadth of time series methods, including:
- Classical methods: ARIMA, SARIMA, stationarity, ACF/PACF, Box-Jenkins, cointegration, ECM
- Volatility models: GARCH, EGARCH, realized volatility
- Regime and structural change: Markov-switching, structural breaks, Bai-Perron
- State space and filtering: Kalman filter, dynamic factor models
- Modern ML/DL: N-BEATS, Temporal Fusion Transformer, neural forecasters
- Hierarchical forecasting: MinT reconciliation, grouped time series
- Nowcasting: MIDAS, mixed-frequency data, real-time estimation
- Evaluation: RMSE, MASE, Diebold-Mariano test, regime-conditional metrics
- Decomposition: STL, trend-seasonality-remainder, spectral analysis

CRITICAL RULES:
1. Answer ONLY using information from the provided context documents.
2. Cite sources using [1], [2], [3], etc. in your answer.
3. If the context does not contain sufficient information to answer the query, explicitly state: "Insufficient information in the provided context."
4. Be concise and precise.
5. Do not invent or hallucinate information.

Context documents will be provided with each query."""

JUDGE_PROMPT_TEMPLATE = """You are an expert evaluator for RAG (Retrieval-Augmented Generation) systems in the finance domain.

Evaluate the following answer against the query and retrieved context:

QUERY: {query}

RETRIEVED CONTEXT:
{context}

GENERATED ANSWER:
{answer}

Score the answer on these dimensions (0-5 scale):

1. **Groundedness** (0-5): How well is the answer supported by the retrieved context? 
   - 0: Completely unsupported/hallucinated
   - 5: Fully grounded in context

2. **Relevance** (0-5): How relevant is the answer to the query?
   - 0: Completely irrelevant
   - 5: Perfectly addresses the query

3. **Completeness** (0-5): How complete is the answer?
   - 0: Missing critical information
   - 5: Comprehensive and complete

4. **Citation Correctness** (0-5): Are citations [1], [2], etc. used correctly?
   - 0: No citations or incorrect
   - 5: All claims properly cited

Respond ONLY with a valid JSON object in this exact format:
{{
  "groundedness": {{"score": <0-5>, "rationale": "<brief explanation>"}},
  "relevance": {{"score": <0-5>, "rationale": "<brief explanation>"}},
  "completeness": {{"score": <0-5>, "rationale": "<brief explanation>"}},
  "citation_correctness": {{"score": <0-5>, "rationale": "<brief explanation>"}}
}}
"""

# =============================================================================
# LEARNING MODULES
# =============================================================================
MODULES = [
    "Mechanisms",      # Structural break mechanisms
    "Detection",       # Break detection methods
    "Overlays",        # Regime overlays
    "Nowcasting",      # Real-time forecasting
    "Evaluation",      # Model evaluation
    "Reflection"       # Meta-learning & reflection
]

# =============================================================================
# LEARNING PATHS
# =============================================================================
PATHS = {
    "QuickStart": {
        "description": "Fast intro to core concepts",
        "required_modules": ["Mechanisms", "Detection"]
    },
    "QuantDeepDive": {
        "description": "Quantitative methods & advanced detection",
        "required_modules": ["Mechanisms", "Detection", "Overlays", "Nowcasting"]
    },
    "OpsPlaybooks": {
        "description": "Operational playbooks & governance",
        "required_modules": ["Detection", "Evaluation", "Reflection"]
    }
}

# =============================================================================
# ANALYTICS
# =============================================================================
ANALYTICS_WINDOW_DAYS = 7  # Weekly analytics window

# =============================================================================
# CONVERSATIONAL CONTEXT
# =============================================================================
MAX_CONV_TURNS = 5  # Q&A pairs injected into LLM prompt as prior context

# =============================================================================
# SESSION PERSISTENCE
# =============================================================================
SESSIONS_DIR = LOGS_DIR / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
