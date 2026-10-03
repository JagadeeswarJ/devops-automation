"""Model Evaluation & Verification Reporter.
Loads the serialized evaluation metrics and outputs formal tables for review and presentation.
"""

import os
import json
import pandas as pd

METRICS_PATH = os.path.join("devops_engine", "ml", "models", "evaluation_metrics.json")


def report_evaluation():
    if not os.path.exists(METRICS_PATH):
        print(f"Error: {METRICS_PATH} not found. Please run train.py first.")
        return

    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    print("\n" + "=" * 70)
    print("      MACHINE LEARNING MODEL EVALUATION & EMPIRICAL VALIDATION")
    print("=" * 70)

    models = [
        ("Model 1: Architectural Archetype Classifier", "archetype_classifier"),
        ("Model 2: Cloud Provider Recommender (AWS vs GCP)", "cloud_recommender"),
        ("Model 3: Compute Service Recommender", "compute_recommender"),
    ]

    summary_rows = []
    for display_name, key in models:
        m = metrics[key]
        summary_rows.append({
            "Model Name": display_name,
            "Test Accuracy": f"{m['test_accuracy'] * 100:.2f}%",
            "Test F1 (Weighted)": f"{m['test_f1_weighted'] * 100:.2f}%",
            "5-Fold CV Mean": f"{m['cv_accuracy_mean'] * 100:.2f}% (±{m['cv_accuracy_std']*100:.2f}%)",
        })

    summary_df = pd.DataFrame(summary_rows)
    print("\n[Summary Metrics across 1,600 Dataset Samples]")
    print(summary_df.to_string(index=False))

    print("\n" + "-" * 70)
    print("Detailed Classification Report: Cloud Recommender (AWS vs GCP)")
    print("-" * 70)
    cloud_rep = metrics["cloud_recommender"]["classification_report"]
    cloud_df = pd.DataFrame(cloud_rep).transpose()
    print(cloud_df.to_string())

    print("\n" + "-" * 70)
    print("Top Predictive Feature Importances for Cloud Decision Making")
    print("-" * 70)
    for idx, item in enumerate(metrics.get("top_cloud_features", []), 1):
        print(f"  {idx}. {item['feature']:<30} : {item['importance'] * 100:.2f}%")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    report_evaluation()
