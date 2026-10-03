"""Machine Learning Model Trainer for Autonomous DevOps Decision Engine.
Trains, evaluates, and exports multi-output pipelines:
1. Architectural Archetype Classifier
2. Cloud Provider Recommender (AWS vs GCP)
3. Compute Service Recommender (conditional on features + cloud)
Includes cross-validation, feature importance extraction, and detailed metrics logging.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix

try:
    from .dataset_generator import generate_devops_dataset
except (ImportError, ValueError):
    from dataset_generator import generate_devops_dataset

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

CATEGORICAL_FEATURES = ["language", "framework", "database", "loc_category"]
NUMERIC_FEATURES = ["is_containerized", "has_api", "has_cache", "has_queue", "route_count", "base_memory_mb"]
ALL_INPUT_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES


def build_preprocessor(extra_categorical: list = None) -> ColumnTransformer:
    """Construct ColumnTransformer for numerical and categorical pipeline branches."""
    cat_cols = list(CATEGORICAL_FEATURES)
    if extra_categorical:
        cat_cols.extend(extra_categorical)

    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
            ("num", StandardScaler(), NUMERIC_FEATURES),
        ]
    )


def train_and_evaluate_all(csv_path: str = None) -> dict:
    """Train all models, compute metrics, and persist artifacts."""
    if csv_path and os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        csv_path = os.path.join(MODEL_DIR, "devops_training_data.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            df = generate_devops_dataset(n_samples=1600)
            df.to_csv(csv_path, index=False)

    print(f"[ML Trainer] Training on dataset with {len(df)} samples...")

    X = df[ALL_INPUT_FEATURES]
    y_archetype = df["archetype"]
    y_cloud = df["recommended_cloud"]

    metrics_report = {}

    # -------------------------------------------------------------------------
    # 1. Architectural Archetype Classifier
    # -------------------------------------------------------------------------
    print("\n--- Training Model 1: Architectural Archetype Classifier ---")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_archetype, test_size=0.20, random_state=42, stratify=y_archetype
    )

    archetype_preprocessor = build_preprocessor()
    archetype_rf = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42)
    archetype_pipeline = Pipeline([
        ("preprocessor", archetype_preprocessor),
        ("classifier", archetype_rf),
    ])

    archetype_pipeline.fit(X_train, y_train)
    y_pred_arch = archetype_pipeline.predict(X_test)
    acc_arch = accuracy_score(y_test, y_pred_arch)
    f1_arch = f1_score(y_test, y_pred_arch, average="weighted")
    cv_scores_arch = cross_val_score(archetype_pipeline, X, y_archetype, cv=5, scoring="accuracy")

    print(f"Archetype Test Accuracy: {acc_arch * 100:.2f}% | F1-Score: {f1_arch * 100:.2f}%")
    print(f"Archetype 5-Fold CV Accuracy: {cv_scores_arch.mean() * 100:.2f}% (std: {cv_scores_arch.std() * 100:.2f}%)")

    metrics_report["archetype_classifier"] = {
        "test_accuracy": round(float(acc_arch), 4),
        "test_f1_weighted": round(float(f1_arch), 4),
        "cv_accuracy_mean": round(float(cv_scores_arch.mean()), 4),
        "cv_accuracy_std": round(float(cv_scores_arch.std()), 4),
        "classes": list(archetype_pipeline.classes_),
        "classification_report": classification_report(y_test, y_pred_arch, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, y_pred_arch).tolist(),
    }

    joblib.dump(archetype_pipeline, os.path.join(MODEL_DIR, "archetype_model.joblib"))

    # -------------------------------------------------------------------------
    # 2. Cloud Provider Recommender (AWS vs GCP)
    # -------------------------------------------------------------------------
    print("\n--- Training Model 2: Cloud Provider Recommender (AWS vs GCP) ---")
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
        X, y_cloud, test_size=0.20, random_state=42, stratify=y_cloud
    )

    cloud_preprocessor = build_preprocessor()
    cloud_rf = RandomForestClassifier(n_estimators=180, max_depth=10, random_state=42)
    cloud_pipeline = Pipeline([
        ("preprocessor", cloud_preprocessor),
        ("classifier", cloud_rf),
    ])

    cloud_pipeline.fit(X_train_c, y_train_c)
    y_pred_cloud = cloud_pipeline.predict(X_test_c)
    acc_cloud = accuracy_score(y_test_c, y_pred_cloud)
    f1_cloud = f1_score(y_test_c, y_pred_cloud, average="weighted")
    cv_scores_cloud = cross_val_score(cloud_pipeline, X, y_cloud, cv=5, scoring="accuracy")

    print(f"Cloud Recommender Test Accuracy: {acc_cloud * 100:.2f}% | F1-Score: {f1_cloud * 100:.2f}%")
    print(f"Cloud Recommender 5-Fold CV: {cv_scores_cloud.mean() * 100:.2f}% (std: {cv_scores_cloud.std() * 100:.2f}%)")

    metrics_report["cloud_recommender"] = {
        "test_accuracy": round(float(acc_cloud), 4),
        "test_f1_weighted": round(float(f1_cloud), 4),
        "cv_accuracy_mean": round(float(cv_scores_cloud.mean()), 4),
        "cv_accuracy_std": round(float(cv_scores_cloud.std()), 4),
        "classes": list(cloud_pipeline.classes_),
        "classification_report": classification_report(y_test_c, y_pred_cloud, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test_c, y_pred_cloud).tolist(),
    }

    joblib.dump(cloud_pipeline, os.path.join(MODEL_DIR, "cloud_model.joblib"))

    # -------------------------------------------------------------------------
    # 3. Compute Service Recommender (Given Features + Cloud Target)
    # -------------------------------------------------------------------------
    print("\n--- Training Model 3: Compute Service Recommender ---")
    X_compute = X.copy()
    X_compute["cloud"] = df["recommended_cloud"]
    y_compute = df["recommended_compute"]

    X_train_comp, X_test_comp, y_train_comp, y_test_comp = train_test_split(
        X_compute, y_compute, test_size=0.20, random_state=42, stratify=y_compute
    )

    compute_preprocessor = build_preprocessor(extra_categorical=["cloud"])
    compute_rf = RandomForestClassifier(n_estimators=160, max_depth=12, random_state=42)
    compute_pipeline = Pipeline([
        ("preprocessor", compute_preprocessor),
        ("classifier", compute_rf),
    ])

    compute_pipeline.fit(X_train_comp, y_train_comp)
    y_pred_comp = compute_pipeline.predict(X_test_comp)
    acc_comp = accuracy_score(y_test_comp, y_pred_comp)
    f1_comp = f1_score(y_test_comp, y_pred_comp, average="weighted")
    cv_scores_comp = cross_val_score(compute_pipeline, X_compute, y_compute, cv=5, scoring="accuracy")

    print(f"Compute Service Test Accuracy: {acc_comp * 100:.2f}% | F1-Score: {f1_comp * 100:.2f}%")
    print(f"Compute Service 5-Fold CV: {cv_scores_comp.mean() * 100:.2f}% (std: {cv_scores_comp.std() * 100:.2f}%)")

    metrics_report["compute_recommender"] = {
        "test_accuracy": round(float(acc_comp), 4),
        "test_f1_weighted": round(float(f1_comp), 4),
        "cv_accuracy_mean": round(float(cv_scores_comp.mean()), 4),
        "cv_accuracy_std": round(float(cv_scores_comp.std()), 4),
        "classes": list(compute_pipeline.classes_),
        "classification_report": classification_report(y_test_comp, y_pred_comp, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test_comp, y_pred_comp).tolist(),
    }

    joblib.dump(compute_pipeline, os.path.join(MODEL_DIR, "compute_model.joblib"))

    # Feature Importance analysis from Cloud Recommender
    fitted_preprocessor = cloud_pipeline.named_steps["preprocessor"]
    cat_encoder = fitted_preprocessor.named_transformers_["cat"]
    cat_feature_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES)
    all_feature_names = list(cat_feature_names) + NUMERIC_FEATURES
    importances = cloud_pipeline.named_steps["classifier"].feature_importances_
    
    top_indices = np.argsort(importances)[::-1][:10]
    top_features = [{
        "feature": str(all_feature_names[i]),
        "importance": round(float(importances[i]), 4)
    } for i in top_indices if i < len(all_feature_names)]
    
    metrics_report["top_cloud_features"] = top_features

    # Save metrics JSON
    metrics_path = os.path.join(MODEL_DIR, "evaluation_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_report, f, indent=2)

    print(f"\n[ML Trainer] Successfully saved models and evaluation report to '{MODEL_DIR}'")
    return metrics_report


if __name__ == "__main__":
    train_and_evaluate_all()
