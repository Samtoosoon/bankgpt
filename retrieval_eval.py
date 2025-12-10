# retrieval_eval.py
import json
from rag_engine import RAG

"""
Evaluation script for RAG retrieval quality.

Expected file: eval/queries.jsonl

Each line format:
{
  "query": "What KYC documents are required for opening a loan account?",
  "relevant_sources": ["KYC_Master_Direction_2016.pdf"]
}

- `relevant_sources` should contain filenames that you actually ingested into docs/
- This script measures Recall@k: in how many cases at least one relevant source is among the top-k retrieved.
"""

def load_queries(path: str = "eval/queries.jsonl"):
    queries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            queries.append(json.loads(line))
    return queries

def evaluate(rag: RAG, queries, top_k: int = 5):
    total = len(queries)
    if total == 0:
        print("No queries found in eval file.")
        return 0.0

    hits = 0

    for q in queries:
        query_text = q["query"]
        relevant_sources = set(q.get("relevant_sources", []))

        results = rag.query(query_text, top_k=top_k)
        retrieved_sources = {
            r["metadata"].get("source")
            for r in results
            if r.get("metadata") and r["metadata"].get("source")
        }

        if relevant_sources.intersection(retrieved_sources):
            hits += 1

    recall = hits / total
    print(f"Recall@{top_k}: {recall:.3f}  ({hits}/{total} queries)")
    return recall

if __name__ == "__main__":
    rag = RAG(persist_dir="chroma_db")
    queries = load_queries()
    evaluate(rag, queries, top_k=5)
