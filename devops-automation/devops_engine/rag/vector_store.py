"""Dense Semantic Vector Store using Sentence Transformers.
Indexes application code chunks, architectural summaries, and cloud knowledge docs into 384-dim embeddings.
"""

import os
import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer


class DevOpsVectorStore:
    """In-memory semantic vector store for codebase and cloud knowledge retrieval."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray = None

    def add_document(self, doc_id: str, title: str, content: str, source: str, category: str, line_range: str = ""):
        """Add a single chunk/document to the index queue."""
        self.documents.append({
            "id": doc_id,
            "title": title,
            "content": content,
            "source": source,
            "category": category,
            "line_range": line_range,
        })

    def add_documents_batch(self, docs: List[Dict[str, Any]]):
        """Batch add documents."""
        self.documents.extend(docs)

    def build_index(self):
        """Compute sentence transformer embeddings for all loaded documents."""
        if not self.documents:
            return

        texts = [f"{d['title']}: {d['content']}" for d in self.documents]
        raw_embs = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        # L2 normalize embeddings for cosine similarity via dot product
        norms = np.linalg.norm(raw_embs, axis=1, keepdims=True)
        norms[norms == 0] = 1e-9
        self.embeddings = raw_embs / norms

    def query(self, query_text: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Retrieve top-k most semantically similar documents."""
        if self.embeddings is None or len(self.documents) == 0:
            return []

        q_emb = self.model.encode([query_text], convert_to_numpy=True, show_progress_bar=False)
        q_norm = np.linalg.norm(q_emb, axis=1, keepdims=True)
        q_norm[q_norm == 0] = 1e-9
        q_emb_norm = q_emb / q_norm

        scores = np.dot(self.embeddings, q_emb_norm.T).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            doc_copy = dict(self.documents[idx])
            doc_copy["relevance_score"] = round(float(scores[idx]), 4)
            results.append(doc_copy)

        return results

    def clear(self):
        """Reset the vector store."""
        self.documents = []
        self.embeddings = None
