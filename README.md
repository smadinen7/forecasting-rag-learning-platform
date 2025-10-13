# Personal Learning Portal (PLP)
## Corporate Forecasting & Structural Breaks

A Retrieval-Augmented Generation (RAG) learning platform for mastering corporate forecasting under structural breaks, with modular progression, intelligent Q&A, and comprehensive evaluation.

---

## 📋 Project Overview

This Personal Learning Portal (PLP) implements a complete RAG system designed to teach practitioners about structural breaks in financial time series and break-aware forecasting techniques. It fulfills a comprehensive assignment workflow:

**Assignment Mapping:**
- **Step 1:** Learning Questions (7 questions in `docs/learning_questions.md`)
- **Step 2:** Learning Objectives (5 Bloom-verb objectives in `docs/objectives.md`) + Platform Features (`docs/features_inspired.md`)
- **Step 3:** Deep Search Corpus (3 starter documents in `data/` + extensible)
- **Step 4:** RAG Implementation (Streamlit app with Gemini/OpenAI/extractive fallback)
- **Step 5:** Evaluation (retrieval metrics + LLM-as-judge)
- **Step 6:** Reflection (`docs/reflection_template.md`)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11
- Virtual environment support
- (Optional) Gemini API key or OpenAI API key for generative Q&A

### Installation

```bash
# 1. Clone/navigate to project
cd plp/

# 2. Create virtual environment and install dependencies
make venv
make install

# 3. (Optional) Configure API keys
cp .env.example .env
# Edit .env and add:
#   PROVIDER=gemini          # or "openai" or "none"
#   GEMINI_API_KEY=your_key
#   OPENAI_API_KEY=your_key  # optional fallback

# 4. Build FAISS index from data/
make ingest

# 5. Launch Streamlit app
make run
```

The app will open at `http://localhost:8501`.

---

## 🏗️ Architecture

### Core Components

1. **Ingestion (`ingest.py`)**
   - Loads `.txt`, `.md`, and small PDFs (<30MB) from `data/`
   - Chunks with `RecursiveCharacterTextSplitter(600, 80)`
   - Embeds with `sentence-transformers/all-MiniLM-L6-v2`
   - Builds FAISS index with metadata preservation

2. **Retrieval & Reranking (`rerank.py`)**
   - Retrieve top-20 candidates
   - Optional BM25-style reranking (toggle `USE_RERANKER` in `config.py`)
   - Return top-5 for answer generation

3. **Answer Generation (`app.py`)**
   - **Gemini** (preferred): `gemini-1.5-pro` via `google-generativeai`
   - **OpenAI** (fallback): `gpt-4o-mini` via `openai`
   - **Extractive** (no keys): Bullet points from top chunks
   - Strict system prompt enforces citation `[1], [2], ...` and groundedness

4. **Evaluation**
   - **Basic (`eval_basic.py`)**: Recall@5 proxy (keyword matching) + cosine relevance
   - **LLM Judge (`eval_judge_llm.py`)**: Gemini/OpenAI scores answers on groundedness, relevance, completeness, citation correctness (0-5 scale)

5. **Streamlit UI (`app.py`)**
   - Sidebar: Module checkboxes (Mechanisms, Detection, Overlays, Nowcasting, Evaluation, Reflection) with progress bar
   - Learning Paths: QuickStart, QuantDeepDive, OpsPlaybooks
   - Micro-survey: Helpful (Y/N), Novelty (0-2), Confidence (0-2)
   - Weekly Analytics: Helpful rate, avg metrics, "Next Best Action"

---

## 📚 Learning Modules & Paths

### Modules (6 total)
1. **Mechanisms**: What are structural breaks? Types, causes, impact
2. **Detection**: Statistical tests (Chow, CUSUM, Bai-Perron)
3. **Overlays**: Regime-switching, ensemble methods, adaptive filters
4. **Nowcasting**: High-frequency data, mixed-frequency models
5. **Evaluation**: Break-adjusted metrics, governance
6. **Reflection**: Meta-learning, failure analysis

### Learning Paths
- **QuickStart**: Mechanisms + Detection (fast intro)
- **QuantDeepDive**: Mechanisms + Detection + Overlays + Nowcasting (quant methods)
- **OpsPlaybooks**: Detection + Evaluation + Reflection (operational focus)

Paths guide module completion and unlock gated content.

---

## 🔧 Configuration (`config.py`)

### Key Settings

```python
# Chunking
CHUNK_SIZE = 600
CHUNK_OVERLAP = 80

# Retrieval
K_CANDIDATES = 20  # Initial retrieval
TOP_K = 5          # Final top-k for answer
USE_RERANKER = False  # Toggle BM25 reranking

# Providers
PROVIDER = "gemini"  # "gemini" | "openai" | "none"
GEMINI_MODEL = "gemini-1.5-pro"
OPENAI_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.2
```

### Environment Variables (`.env`)

```bash
PROVIDER=gemini          # Provider selection
GEMINI_API_KEY=...       # Gemini key (required for Gemini)
OPENAI_API_KEY=...       # OpenAI key (optional fallback)
```

---

## 📊 Evaluation

### Basic Metrics (`make eval-basic`)

Computes per-query and aggregate:
- **Recall@5**: Fraction of expected keywords found in top-5 docs
- **Avg Relevance**: Cosine similarity proxy (0-1)

Output: `eval/results/basic_eval.json`

### LLM-as-Judge (`make eval-judge`)

Uses Gemini (preferred) or OpenAI to score answers on:
- **Groundedness** (0-5): Answer supported by context?
- **Relevance** (0-5): Addresses query?
- **Completeness** (0-5): Covers key points?
- **Citation Correctness** (0-5): Citations accurate?

Output: `eval/results/llm_judge_eval.json` + `.jsonl`

**Graceful Fallback:** If no API keys, prints skip notice and exits cleanly.

---

## 🗂️ Adding Sources

1. **Markdown/Text**: Drop `.md` or `.txt` files into `data/`
2. **PDFs**: Add small PDFs (<30MB) to `data/`
3. **Metadata**: Include YAML frontmatter:
   ```yaml
   ---
   title: "Document Title"
   source: "Author/Organization"
   type: "Tutorial | Research | Case Study"
   relevance: "Core | Advanced | Reference"
   ---
   ```
4. **Re-ingest**: Run `make ingest` to rebuild index
5. **Document**: Add entry to `docs/sources_template.csv`

---

## 📈 Analytics & Logging

### Logs (`logs/run_YYYYMMDD.jsonl`)
Each query logs:
- Timestamp, query, answer, provider
- Top-5 sources, config hash
- Survey responses (helpful, novelty, confidence)

### Weekly Analytics Card
Displays:
- **Helpful Rate**: % queries marked "Helpful"
- **Avg Novelty/Confidence**: User self-assessment
- **Next Best Action**: Data-driven suggestion (e.g., "Review low-helpful queries")

---

## 🧪 Testing

```bash
make test
```

Runs pytest suite:
- `test_ingest.py`: FAISS index builds, loads, contains vectors
- `test_retrieval.py`: Similarity search works, metadata present, reranker preserves docs
- `test_eval.py`: Eval results have correct structure, metrics in valid ranges

---

## 🔍 Troubleshooting

### Issue: "FAISS index not found"
**Solution:** Run `make ingest` to build index from `data/` directory.

### Issue: "No API keys found" (LLM judge)
**Solution:** Set `GEMINI_API_KEY` or `OPENAI_API_KEY` in `.env`. LLM judge gracefully skips if no keys.

### Issue: Streamlit port conflict
**Solution:** Kill existing Streamlit process or run:
```bash
.venv/bin/streamlit run app.py --server.port 8502
```

### Issue: Import errors
**Solution:** Ensure virtual environment is activated and dependencies installed:
```bash
source .venv/bin/activate
make install
```

### Issue: Slow embedding
**Solution:** First run downloads `all-MiniLM-L6-v2` model (~90MB). Subsequent runs are fast. CPU-only; no GPU required.

---

## 📖 Platform-Inspired Features

Adapted from best-in-class learning platforms:

| Platform   | Feature                | Our Adaptation                                 |
|------------|------------------------|-----------------------------------------------|
| **Canvas** | Modules + Prerequisites| 6 gated modules with progress bar             |
| **Canvas** | Mastery Paths          | 3 predefined paths (QuickStart, QuantDeepDive, Ops) |
| **Canvas** | Embedded Assessments   | Micro-survey (Helpful/Novelty/Confidence)     |
| **EducateMe** | Micro-Surveys       | Post-answer 3-question pulse check            |
| **EducateMe** | Kanban Boards       | Progress bar + Analytics card                 |
| **Valamis** | Learning Paths + Analytics | Paths + Weekly metrics (4 scores + action) |
| **Valamis** | Competency Progression | Module gating + "Next Best Action" suggestions |

See `docs/features_inspired.md` for details.

---

## 📝 Sources Table

Document your knowledge corpus in `docs/sources_template.csv`:

| Title | URL | Type | Relevance |
|-------|-----|------|-----------|
| Structural Breaks Fundamentals | Internal | Tutorial | Core |
| Forecasting Under Breaks | Internal | Methodology | Advanced |
| Evaluation & Governance | Internal | Governance | Operational |
| (Add more...) | | | |

---

## 🔮 Next Steps

### Immediate (Post-MVP)
- [ ] Add more domain sources (research papers, case studies)
- [ ] Tune `CHUNK_SIZE` based on eval metrics
- [ ] Enable `USE_RERANKER=True` and compare performance
- [ ] Export logs/analytics to CSV for external analysis

### Stretch
- [ ] Cross-encoder reranking (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
- [ ] RAGAs/ARES integration (with graceful skip if install fails)
- [ ] Notes panel: Allow users to save annotated answers
- [ ] Multi-user support with authentication
- [ ] Cloud deployment (Streamlit Cloud, AWS, GCP)

---

## 🛠️ Make Targets

| Command | Description |
|---------|-------------|
| `make venv` | Create Python 3.11 virtual environment |
| `make install` | Install dependencies from `requirements.txt` |
| `make ingest` | Build FAISS index from `data/` |
| `make run` | Launch Streamlit app |
| `make eval-basic` | Run basic retrieval evaluation |
| `make eval-judge` | Run LLM-as-judge evaluation |
| `make test` | Run pytest suite |
| `make lint` | Check Python syntax |
| `make clean` | Remove venv, index, logs, results |

---

## 📄 License

MIT License - See `LICENSE` file

---

## 🙏 Acknowledgments

- **LangChain** for RAG primitives
- **FAISS** for efficient vector search
- **Sentence Transformers** for embeddings
- **Streamlit** for rapid UI prototyping
- **Gemini/OpenAI** for LLM capabilities

---

## 📞 Support

For questions or issues:
1. Check `docs/` for guides
2. Review `eval/results/` for performance insights
3. Use `docs/reflection_template.md` for structured iteration

---

**Built with ❤️ for practitioners mastering forecasting under uncertainty.**
