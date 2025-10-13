#!/usr/bin/env python3
"""
LLM-as-Judge Evaluation
Uses Gemini (preferred) or OpenAI to score RAG outputs on groundedness, relevance, completeness, citation correctness
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

sys.path.insert(0, str(Path(__file__).parent))
import config
from rerank import rerank


def load_queries(queries_file: Path) -> List[Dict[str, Any]]:
    """Load sample queries from YAML."""
    with open(queries_file, "r") as f:
        data = yaml.safe_load(f)
    return data["queries"]


def generate_answer_for_eval(query: str, context_docs: List[Document]) -> tuple[str, str]:
    """Generate answer using configured provider."""
    # Build context string
    context_parts = []
    for i, doc in enumerate(context_docs[:config.TOP_K], 1):
        source = doc.metadata.get("source", "Unknown")
        content = doc.page_content[:500]
        context_parts.append(f"[{i}] Source: {source}\n{content}")
    
    context_str = "\n\n".join(context_parts)
    
    # Try Gemini first if configured
    if config.PROVIDER == "gemini" and config.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel(config.GEMINI_MODEL)
            
            prompt = f"""{config.SYSTEM_PROMPT}

QUERY: {query}

CONTEXT:
{context_str}

Provide a concise answer with citations [1], [2], etc."""
            
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=config.TEMPERATURE,
                    max_output_tokens=config.MAX_TOKENS,
                )
            )
            
            return response.text.strip(), "gemini"
        except Exception as e:
            print(f"  ⚠ Gemini failed: {e}")
    
    # Try OpenAI fallback
    if config.OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            
            messages = [
                {"role": "system", "content": config.SYSTEM_PROMPT},
                {"role": "user", "content": f"""QUERY: {query}

CONTEXT:
{context_str}

Provide a concise answer with citations [1], [2], etc."""}
            ]
            
            response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS,
            )
            
            return response.choices[0].message.content.strip(), "openai"
        except Exception as e:
            print(f"  ⚠ OpenAI failed: {e}")
    
    # Extractive fallback
    bullets = []
    for i, doc in enumerate(context_docs[:config.TOP_K], 1):
        source = doc.metadata.get("source", "Unknown")
        snippet = doc.page_content[:200].strip()
        bullets.append(f"[{i}] {source}: {snippet}")
    return "\n".join(bullets), "extractive"


def judge_with_gemini(query: str, context: str, answer: str) -> Optional[Dict[str, Any]]:
    """Use Gemini to judge answer quality."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        
        prompt = config.JUDGE_PROMPT_TEMPLATE.format(
            query=query,
            context=context,
            answer=answer
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.0,  # Deterministic for evaluation
                max_output_tokens=800,
            )
        )
        
        # Parse JSON response
        result_text = response.text.strip()
        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        scores = json.loads(result_text)
        return scores
        
    except Exception as e:
        print(f"  ✗ Gemini judge error: {e}")
        return None


def judge_with_openai(query: str, context: str, answer: str) -> Optional[Dict[str, Any]]:
    """Use OpenAI to judge answer quality."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        prompt = config.JUDGE_PROMPT_TEMPLATE.format(
            query=query,
            context=context,
            answer=answer
        )
        
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert RAG evaluator. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=800,
        )
        
        result_text = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        scores = json.loads(result_text)
        return scores
        
    except Exception as e:
        print(f"  ✗ OpenAI judge error: {e}")
        return None


def evaluate_with_llm_judge(vectorstore: FAISS, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate answers using LLM-as-judge.
    """
    # Check if we have any API key
    if not config.GEMINI_API_KEY and not config.OPENAI_API_KEY:
        print("=" * 60)
        print("⊘ LLM-as-Judge Evaluation Skipped")
        print("=" * 60)
        print("\nNo API keys found (GEMINI_API_KEY or OPENAI_API_KEY).")
        print("Set at least one API key in .env to enable LLM judging.")
        print("\nExample:")
        print("  PROVIDER=gemini")
        print("  GEMINI_API_KEY=your_key_here")
        print("=" * 60)
        return {"skipped": True, "reason": "No API keys available"}
    
    results = []
    judge_provider = None
    
    for query_data in queries:
        query_id = query_data["id"]
        question = query_data["question"]
        
        print(f"\nQuery {query_id}: {question[:60]}...")
        
        # Retrieve
        candidate_docs = vectorstore.similarity_search(question, k=config.K_CANDIDATES)
        reranked_docs = rerank(question, candidate_docs)
        
        # Generate answer
        answer, gen_provider = generate_answer_for_eval(question, reranked_docs)
        print(f"  Answer generated with: {gen_provider}")
        
        # Build context string for judge
        context_parts = []
        for i, doc in enumerate(reranked_docs[:config.TOP_K], 1):
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content[:400]
            context_parts.append(f"[{i}] {source}: {content}")
        context_str = "\n\n".join(context_parts)
        
        # Judge answer
        scores = None
        
        # Try Gemini first if available
        if config.GEMINI_API_KEY:
            scores = judge_with_gemini(question, context_str, answer)
            if scores:
                judge_provider = "gemini"
        
        # Fallback to OpenAI if Gemini failed
        if not scores and config.OPENAI_API_KEY:
            scores = judge_with_openai(question, context_str, answer)
            if scores:
                judge_provider = "openai"
        
        if not scores:
            print(f"  ✗ Failed to judge query {query_id}")
            continue
        
        result = {
            "query_id": query_id,
            "question": question,
            "answer": answer,
            "generator_provider": gen_provider,
            "judge_provider": judge_provider,
            "scores": scores,
            "top_sources": [doc.metadata.get("source", "Unknown") for doc in reranked_docs[:config.TOP_K]]
        }
        
        results.append(result)
        print(f"  ✓ Judged by {judge_provider}")
        print(f"    Groundedness: {scores['groundedness']['score']}/5")
        print(f"    Relevance:    {scores['relevance']['score']}/5")
        print(f"    Completeness: {scores['completeness']['score']}/5")
        print(f"    Citations:    {scores['citation_correctness']['score']}/5")
    
    if not results:
        return {"error": "No queries successfully judged"}
    
    # Aggregate scores
    avg_groundedness = sum(r["scores"]["groundedness"]["score"] for r in results) / len(results)
    avg_relevance = sum(r["scores"]["relevance"]["score"] for r in results) / len(results)
    avg_completeness = sum(r["scores"]["completeness"]["score"] for r in results) / len(results)
    avg_citations = sum(r["scores"]["citation_correctness"]["score"] for r in results) / len(results)
    
    summary = {
        "avg_scores": {
            "groundedness": round(avg_groundedness, 2),
            "relevance": round(avg_relevance, 2),
            "completeness": round(avg_completeness, 2),
            "citation_correctness": round(avg_citations, 2)
        },
        "num_queries": len(results),
        "judge_provider": judge_provider,
        "config": {
            "provider": config.PROVIDER,
            "top_k": config.TOP_K,
            "use_reranker": config.USE_RERANKER
        },
        "per_query_results": results
    }
    
    return summary


def main():
    print("=" * 60)
    print("LLM-as-Judge Evaluation")
    print("=" * 60)
    
    # Load queries
    queries_file = config.EVAL_DIR / "queries.yaml"
    if not queries_file.exists():
        print(f"✗ Queries file not found: {queries_file}")
        sys.exit(1)
    
    queries = load_queries(queries_file)
    print(f"\n✓ Loaded {len(queries)} queries")
    
    # Load vectorstore
    if not config.FAISS_INDEX_PATH.exists():
        print(f"✗ FAISS index not found: {config.FAISS_INDEX_PATH}")
        print("  Run 'make ingest' first")
        sys.exit(1)
    
    print(f"✓ Loading FAISS index...")
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
    print("✓ FAISS index loaded")
    
    # Evaluate
    print("\n" + "=" * 60)
    print("Evaluating with LLM Judge...")
    print("=" * 60)
    
    summary = evaluate_with_llm_judge(vectorstore, queries)
    
    if summary.get("skipped"):
        sys.exit(0)
    
    if summary.get("error"):
        print(f"\n✗ Error: {summary['error']}")
        sys.exit(1)
    
    # Save results
    results_file = config.EVAL_DIR / "results" / "llm_judge_eval.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Save JSONL for easy processing
    jsonl_file = config.EVAL_DIR / "results" / "llm_judge_eval.jsonl"
    with open(jsonl_file, "w") as f:
        for result in summary["per_query_results"]:
            f.write(json.dumps(result) + "\n")
    
    print("\n" + "=" * 60)
    print("Summary - Average Scores (0-5 scale)")
    print("=" * 60)
    print(f"Groundedness:       {summary['avg_scores']['groundedness']:.2f}/5")
    print(f"Relevance:          {summary['avg_scores']['relevance']:.2f}/5")
    print(f"Completeness:       {summary['avg_scores']['completeness']:.2f}/5")
    print(f"Citation Correct:   {summary['avg_scores']['citation_correctness']:.2f}/5")
    print(f"\nQueries Evaluated:  {summary['num_queries']}")
    print(f"Judge Provider:     {summary['judge_provider']}")
    print("=" * 60)
    print(f"\n✓ Results saved to:")
    print(f"  - {results_file}")
    print(f"  - {jsonl_file}")
    print("\nNext steps:")
    print("  - Review detailed scores in llm_judge_eval.json")
    print("  - Use reflection_template.md to document findings")
    print("=" * 60)


if __name__ == "__main__":
    main()
