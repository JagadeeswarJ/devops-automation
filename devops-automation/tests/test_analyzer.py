"""Unit tests for Codebase Analyzer."""

import os
import unittest
from devops_engine.analyzer.codebase_scanner import scan_directory
from devops_engine.analyzer.feature_extractor import extract_ml_features

SAMPLE_BASE = os.path.join(os.path.dirname(__file__), "..", "devops_engine", "sample_projects")


class TestCodebaseAnalyzer(unittest.TestCase):

    def test_fastapi_scanner(self):
        proj_dir = os.path.join(SAMPLE_BASE, "fastapi_microservice")
        scan = scan_directory(proj_dir)
        self.assertEqual(scan["primary_language"], "Python")
        self.assertEqual(scan["primary_framework"], "FastAPI")
        self.assertEqual(scan["primary_database"], "PostgreSQL")
        self.assertTrue(scan["is_containerized"])
        self.assertTrue(scan["has_cache"])
        self.assertGreater(scan["route_count"], 0)

        features = extract_ml_features(scan)
        self.assertEqual(features["language"], "Python")
        self.assertEqual(features["framework"], "FastAPI")
        self.assertEqual(features["is_containerized"], 1)

    def test_node_scanner(self):
        proj_dir = os.path.join(SAMPLE_BASE, "node_express_api")
        scan = scan_directory(proj_dir)
        self.assertEqual(scan["primary_language"], "JavaScript")
        self.assertEqual(scan["primary_framework"], "Express")
        self.assertEqual(scan["primary_database"], "MongoDB")
        self.assertTrue(scan["is_containerized"])

    def test_java_scanner(self):
        proj_dir = os.path.join(SAMPLE_BASE, "java_spring_service")
        scan = scan_directory(proj_dir)
        self.assertEqual(scan["primary_language"], "Java")
        self.assertEqual(scan["primary_framework"], "Spring Boot")
        self.assertEqual(scan["primary_database"], "PostgreSQL")
        self.assertTrue(scan["is_containerized"])


if __name__ == "__main__":
    unittest.main()
