"""Unit tests for RAG Vector Store and Context Retrieval."""

import os
import unittest
from devops_engine.rag.vector_store import DevOpsVectorStore
from devops_engine.rag.qa_engine import DevOpsQAEngine
from devops_engine.analyzer.codebase_scanner import scan_directory
from devops_engine.analyzer.feature_extractor import extract_ml_features
from devops_engine.ml.predictor import DevOpsPredictor
from devops_engine.decision_rules.policy_engine import apply_decision_rules

SAMPLE_BASE = os.path.join(os.path.dirname(__file__), "..", "devops_engine", "sample_projects")


class TestRAGEngine(unittest.TestCase):

    def test_vector_store_operations(self):
        vs = DevOpsVectorStore()
        vs.add_document("doc1", "AWS Fargate", "AWS Fargate runs containers serverless", "AWS Docs", "Compute")
        vs.add_document("doc2", "GCP Cloud Run", "GCP Cloud Run runs containerized web services", "GCP Docs", "Compute")
        vs.build_index()

        results = vs.query("How to run containers serverless in AWS?", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "doc1")

    def test_qa_engine_e2e(self):
        proj_dir = os.path.join(SAMPLE_BASE, "fastapi_microservice")
        scan = scan_directory(proj_dir)
        features = extract_ml_features(scan)
        pred = DevOpsPredictor()
        ml_res = pred.predict_full_pipeline(features)
        dec = apply_decision_rules(scan, ml_res)

        qa = DevOpsQAEngine()
        qa.set_context(proj_dir, scan, dec)
        questions = qa.generate_contextual_questions()
        self.assertGreater(len(questions), 3)

        ans = qa.answer_question(questions[0])
        self.assertIn("answer", ans)
        self.assertIn("retrieved_chunks", ans)
        self.assertGreater(len(ans["retrieved_chunks"]), 0)


if __name__ == "__main__":
    unittest.main()
