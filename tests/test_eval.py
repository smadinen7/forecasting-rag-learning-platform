"""
Test evaluation metrics
"""
import sys
from pathlib import Path
import json

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from langchain.schema import Document


def test_eval_queries_exist():
    """Test that queries.yaml exists."""
    queries_file = config.EVAL_DIR / "queries.yaml"
    assert queries_file.exists(), f"Queries file not found: {queries_file}"


def test_eval_results_directory():
    """Test that eval/results directory exists."""
    results_dir = config.EVAL_DIR / "results"
    assert results_dir.exists(), f"Results directory not found: {results_dir}"


def test_basic_eval_results_structure():
    """Test that basic eval results have correct structure."""
    results_file = config.EVAL_DIR / "results" / "basic_eval.json"
    
    if not results_file.exists():
        pytest.skip("basic_eval.json not found - run 'make eval-basic' first")
    
    with open(results_file, "r") as f:
        results = json.load(f)
    
    # Check required keys
    assert "avg_recall_at_5" in results, "Missing avg_recall_at_5"
    assert "avg_relevance" in results, "Missing avg_relevance"
    assert "num_queries" in results, "Missing num_queries"
    assert "per_query_results" in results, "Missing per_query_results"
    
    # Check metric ranges
    assert 0.0 <= results["avg_recall_at_5"] <= 1.0, "avg_recall_at_5 out of range"
    assert 0.0 <= results["avg_relevance"] <= 1.0, "avg_relevance out of range"
    
    # Check per-query results
    for result in results["per_query_results"]:
        assert "query_id" in result, "Missing query_id in per-query result"
        assert "recall_at_5" in result, "Missing recall_at_5 in per-query result"
        assert 0.0 <= result["recall_at_5"] <= 1.0, "recall_at_5 out of range"


def test_llm_judge_results_structure():
    """Test that LLM judge results have correct structure."""
    results_file = config.EVAL_DIR / "results" / "llm_judge_eval.json"
    
    if not results_file.exists():
        pytest.skip("llm_judge_eval.json not found - run 'make eval-judge' first or set API keys")
    
    with open(results_file, "r") as f:
        results = json.load(f)
    
    # Check if skipped
    if results.get("skipped"):
        pytest.skip("LLM judge evaluation was skipped (no API keys)")
    
    # Check required keys
    assert "avg_scores" in results, "Missing avg_scores"
    assert "num_queries" in results, "Missing num_queries"
    assert "per_query_results" in results, "Missing per_query_results"
    
    # Check average scores
    avg_scores = results["avg_scores"]
    assert "groundedness" in avg_scores, "Missing groundedness score"
    assert "relevance" in avg_scores, "Missing relevance score"
    assert "completeness" in avg_scores, "Missing completeness score"
    assert "citation_correctness" in avg_scores, "Missing citation_correctness score"
    
    # Check score ranges (0-5)
    for score_name, score_value in avg_scores.items():
        assert 0.0 <= score_value <= 5.0, f"{score_name} out of range [0, 5]: {score_value}"
    
    # Check per-query results
    for result in results["per_query_results"]:
        assert "query_id" in result, "Missing query_id"
        assert "scores" in result, "Missing scores"
        
        scores = result["scores"]
        for dimension in ["groundedness", "relevance", "completeness", "citation_correctness"]:
            assert dimension in scores, f"Missing {dimension} in scores"
            assert "score" in scores[dimension], f"Missing score in {dimension}"
            assert "rationale" in scores[dimension], f"Missing rationale in {dimension}"
            
            score_val = scores[dimension]["score"]
            assert 0 <= score_val <= 5, f"{dimension} score out of range: {score_val}"


def test_config_values():
    """Test that config values are reasonable."""
    assert config.CHUNK_SIZE > 0, "CHUNK_SIZE must be positive"
    assert config.TOP_K > 0, "TOP_K must be positive"
    assert config.TEMPERATURE >= 0.0, "TEMPERATURE must be non-negative"
    assert config.TEMPERATURE <= 2.0, "TEMPERATURE should be <= 2.0"


def test_modules_list():
    """Test that modules list is defined."""
    assert len(config.MODULES) > 0, "MODULES list is empty"
    assert "Mechanisms" in config.MODULES, "Expected 'Mechanisms' in MODULES"
    assert "Evaluation" in config.MODULES, "Expected 'Evaluation' in MODULES"


def test_paths_dict():
    """Test that learning paths are defined."""
    assert len(config.PATHS) > 0, "PATHS dictionary is empty"
    
    for path_name, path_info in config.PATHS.items():
        assert "description" in path_info, f"Missing description in {path_name}"
        assert "required_modules" in path_info, f"Missing required_modules in {path_name}"
        assert len(path_info["required_modules"]) > 0, f"Empty required_modules in {path_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
