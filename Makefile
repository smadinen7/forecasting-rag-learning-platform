.PHONY: venv install ingest run eval-basic eval-judge test lint clean help

PYTHON := python3.11
VENV := .venv
BIN := $(VENV)/bin

help:
	@echo "Personal Learning Portal - Make targets:"
	@echo "  make venv        - Create virtual environment"
	@echo "  make install     - Install dependencies"
	@echo "  make ingest      - Build FAISS index from data/"
	@echo "  make run         - Launch Streamlit app"
	@echo "  make eval-basic  - Run basic retrieval evaluation"
	@echo "  make eval-judge  - Run LLM-as-judge evaluation"
	@echo "  make test        - Run pytest suite"
	@echo "  make lint        - Run code linting"
	@echo "  make clean       - Clean generated files"

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created. Activate with: source $(BIN)/activate"

install: venv
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	@echo "Dependencies installed successfully"

ingest:
	$(BIN)/python ingest.py
	@echo "Ingestion complete - FAISS index built"

run:
	$(BIN)/streamlit run app.py

eval-basic:
	$(BIN)/python eval_basic.py

eval-judge:
	$(BIN)/python eval_judge_llm.py

test:
	$(BIN)/pytest tests/ -v

lint:
	$(BIN)/python -m py_compile *.py
	@echo "Linting complete"

clean:
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf index/
	rm -rf logs/
	rm -rf eval/results/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete"
