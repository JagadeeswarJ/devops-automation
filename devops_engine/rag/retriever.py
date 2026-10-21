"""Context Retriever for Application Codebase and Cloud Architecture.
Ingests project code, architectural decisions, and cloud knowledge into the vector store.
"""

import os
from typing import List, Dict, Any
from .vector_store import DevOpsVectorStore
from .knowledge_base import get_all_knowledge_docs

TEXT_FILE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".json",
    ".xml", ".yaml", ".yml", ".md", ".txt", ".sql", ".env.example"
}


class ContextRetriever:
    """Orchestrates document chunking and vector indexing across codebase and cloud domain knowledge."""

    def __init__(self, vector_store: DevOpsVectorStore = None):
        self.vector_store = vector_store or DevOpsVectorStore()
        self.is_indexed = False

    def index_project(
        self,
        project_path: str,
        scan_result: Dict[str, Any],
        decision_result: Dict[str, Any]
    ):
        """Build a unified semantic index containing codebase, decision summary, and cloud knowledge."""
        self.vector_store.clear()
        project_path = os.path.abspath(project_path)

        # 1. Index Curated Cloud Knowledge Documents
        for doc in get_all_knowledge_docs():
            self.vector_store.add_document(
                doc_id=doc["id"],
                title=doc["title"],
                content=doc["content"],
                source="Cloud Knowledge Base",
                category=doc["category"],
                line_range=""
            )

        # 2. Index Synthesized Architectural Decision Document
        final_cloud = decision_result.get("final_cloud", "AWS")
        final_compute = decision_result.get("final_compute", "AWS ECS Fargate")
        infra = decision_result.get("final_infrastructure", {})
        costs = decision_result.get("cost_comparison", {})
        
        decision_summary = (
            f"Deployment Decision Summary for {os.path.basename(project_path)}:\n"
            f"- Recommended Cloud: {final_cloud}\n"
            f"- Recommended Compute Service: {final_compute}\n"
            f"- Managed Database: {infra.get('database_service', 'None')}\n"
            f"- Cache Service: {infra.get('cache_service', 'None')}\n"
            f"- Queue Service: {infra.get('queue_service', 'None')}\n"
            f"- Object Storage: {infra.get('storage_service', 'None')}\n"
            f"- Estimated AWS Monthly Cost: ${costs.get('AWS', {}).get('total_estimated_monthly_usd', 0)}\n"
            f"- Estimated GCP Monthly Cost: ${costs.get('GCP', {}).get('total_estimated_monthly_usd', 0)}\n"
            f"- Cost-Effective Cloud: {costs.get('cheaper_provider', 'N/A')} "
            f"(savings: ${costs.get('monthly_difference_usd', 0)}/mo, {costs.get('percentage_savings', 0)}%)\n"
            f"- Policy & Validation Status: {[c['gate'] + ': ' + c['status'] for c in decision_result.get('policy_checks', [])]}"
        )
        self.vector_store.add_document(
            doc_id="architecture-decision-summary",
            title="Generated Cloud Architecture Decision & Cost Analysis",
            content=decision_summary,
            source="Decision Engine",
            category="System Architecture",
            line_range=""
        )

        # 3. Chunk and Index Codebase Files
        ignored = {".git", "node_modules", ".venv", "venv", "__pycache__", "target", "dist", "build"}
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ignored and not d.startswith(".")]
            for fname in files:
                rel_path = os.path.relpath(os.path.join(root, fname), project_path).replace("\\", "/")
                ext = os.path.splitext(fname)[1].lower()
                is_dockerfile = fname.lower() == "dockerfile" or fname.lower().startswith("dockerfile.")

                if ext in TEXT_FILE_EXTENSIONS or is_dockerfile:
                    full_p = os.path.join(root, fname)
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
                            lines = f.readlines()
                    except Exception:
                        continue

                    # Chunk by 30-line blocks with 5-line overlap
                    chunk_size = 30
                    overlap = 5
                    for start_idx in range(0, max(len(lines), 1), chunk_size - overlap):
                        end_idx = min(start_idx + chunk_size, len(lines))
                        chunk_text = "".join(lines[start_idx:end_idx]).strip()
                        if not chunk_text:
                            continue

                        self.vector_store.add_document(
                            doc_id=f"{rel_path}:{start_idx+1}-{end_idx}",
                            title=f"Source File: {rel_path} (lines {start_idx+1}-{end_idx})",
                            content=chunk_text,
                            source=rel_path,
                            category="Codebase Source",
                            line_range=f"{start_idx+1}-{end_idx}"
                        )
                        if end_idx == len(lines):
                            break

        # Build index
        self.vector_store.build_index()
        self.is_indexed = True

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Retrieve relevant context chunks for a given query."""
        if not self.is_indexed:
            return []
        return self.vector_store.query(query, top_k=top_k)
