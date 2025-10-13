# Quick Reference Guide

## 🚀 First-Time Setup

```bash
# 1. Navigate to project
cd plp/

# 2. Setup environment
make venv
make install

# 3. (Optional) Configure API keys
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY or OPENAI_API_KEY

# 4. Build knowledge base
make ingest

# 5. Launch app
make run
```

## 🔄 Daily Workflow

```bash
# Start app
make run

# Run evaluations
make eval-basic
make eval-judge

# Run tests
make test
```

## 📝 Adding New Content

```bash
# 1. Add .md/.txt/.pdf to data/
# 2. Re-ingest
make ingest
# 3. Verify in app
make run
```

## 🧪 Evaluation Workflow

```bash
# 1. Edit queries in eval/queries.yaml
# 2. Run basic metrics
make eval-basic
# View: eval/results/basic_eval.json

# 3. Run LLM judge (requires API key)
make eval-judge
# View: eval/results/llm_judge_eval.json

# 4. Document findings
# Edit: docs/reflection_template.md
```

## ⚙️ Configuration Changes

Edit `config.py`:
```python
# Experiment with chunking
CHUNK_SIZE = 800  # Default: 600
CHUNK_OVERLAP = 100  # Default: 80

# Enable reranking
USE_RERANKER = True  # Default: False

# Adjust retrieval
K_CANDIDATES = 30  # Default: 20
TOP_K = 7  # Default: 5

# Change provider
PROVIDER = "openai"  # Default: "gemini"
```

Then re-ingest if chunking changed:
```bash
make clean
make install
make ingest
```

## 📊 Analytics Access

View weekly analytics in app's Analytics card, or parse logs:
```bash
# View today's logs
cat logs/run_$(date +%Y%m%d).jsonl | jq .

# Count helpful queries
cat logs/run_*.jsonl | jq 'select(.survey.helpful=="Yes")' | wc -l
```

## 🐛 Debugging

```bash
# Check FAISS index
python -c "
import config
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

emb = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
vs = FAISS.load_local(str(config.FAISS_INDEX_PATH), emb, index_name='faiss_index', allow_dangerous_deserialization=True)
print(f'Index loaded: {vs.index.ntotal} vectors')
"

# Test retrieval
python -c "
import config
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

emb = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
vs = FAISS.load_local(str(config.FAISS_INDEX_PATH), emb, index_name='faiss_index', allow_dangerous_deserialization=True)
docs = vs.similarity_search('structural breaks', k=3)
for d in docs: print(f'Source: {d.metadata.get(\"source\")}, Len: {len(d.page_content)}')
"
```

## 🔧 Troubleshooting Checklist

- [ ] Virtual environment activated? (`source .venv/bin/activate`)
- [ ] Dependencies installed? (`make install`)
- [ ] FAISS index built? (`make ingest`)
- [ ] API keys in `.env`? (For LLM features)
- [ ] Port 8501 free? (For Streamlit)
- [ ] Python 3.11+? (`python --version`)

## 📞 Support

Check `README.md` for full documentation.
