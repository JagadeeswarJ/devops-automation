"""Unit tests for ML Inference Engine."""

import unittest
import pandas as pd
from devops_engine.ml.predictor import DevOpsPredictor


class TestMLEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = DevOpsPredictor()

    def test_predictor_basic_inference(self):
        sample_features = {
            "language": "Python",
            "framework": "FastAPI",
            "database": "PostgreSQL",
            "is_containerized": 1,
            "has_api": 1,
            "has_cache": 1,
            "has_queue": 0,
            "route_count": 12,
            "loc_category": "medium",
            "base_memory_mb": 768
        }
        res = self.predictor.predict_full_pipeline(sample_features)
        self.assertIn(res["selected_cloud"], ["AWS", "GCP"])
        self.assertIn("archetype", res)
        self.assertIn("recommended_compute", res)
        self.assertIn(res["recommended_compute"], ["AWS ECS Fargate", "AWS Lambda", "AWS EC2", "GCP Cloud Run", "GCP Cloud Functions", "GCP Compute Engine"])

    def test_predictor_forced_cloud(self):
        sample_features = {
            "language": "Python",
            "framework": "FastAPI",
            "database": "PostgreSQL",
            "is_containerized": 1,
            "has_api": 1,
            "has_cache": 0,
            "has_queue": 0,
            "route_count": 5,
            "loc_category": "small",
            "base_memory_mb": 512
        }
        res_aws = self.predictor.predict_full_pipeline(sample_features, forced_cloud="AWS")
        self.assertEqual(res_aws["selected_cloud"], "AWS")

        res_gcp = self.predictor.predict_full_pipeline(sample_features, forced_cloud="GCP")
        self.assertEqual(res_gcp["selected_cloud"], "GCP")


if __name__ == "__main__":
    unittest.main()
