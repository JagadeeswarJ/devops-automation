import os
import joblib
import pandas as pd

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier


ARTIFACT_DIR = "artifacts"

os.makedirs(ARTIFACT_DIR, exist_ok=True)


# ---------------------------------------------------------
# Training dataset
# ---------------------------------------------------------

# synthetic dataset
data = [
    # language, framework, database, containerized, api, cloud, compute
    ["Python", "FastAPI", "PostgreSQL", 0, 1, "AWS", "Lambda"],
    ["Python", "Flask", "None", 0, 1, "AWS", "Lambda"],
    ["Python", "Django", "PostgreSQL", 1, 1, "AWS", "ECS"],
    ["Python", "FastAPI", "PostgreSQL", 1, 1, "AWS", "ECS"],

    ["JavaScript", "Express", "None", 0, 1, "AWS", "Lambda"],
    ["JavaScript", "Express", "MongoDB", 1, 1, "AWS", "ECS"],
    ["JavaScript", "Express", "PostgreSQL", 1, 1, "AWS", "ECS"],

    ["Java", "Spring Boot", "PostgreSQL", 1, 1, "AWS", "ECS"],
    ["Java", "Spring Boot", "PostgreSQL", 1, 1, "GCP", "Cloud Run"],
    ["Java", "Spring Boot", "None", 1, 1, "GCP", "Cloud Run"],

    ["Python", "FastAPI", "PostgreSQL", 0, 1, "Azure", "Functions"],
    ["Python", "Flask", "None", 0, 1, "Azure", "Functions"],
    ["Python", "Django", "PostgreSQL", 1, 1, "Azure", "Container Apps"],

    ["JavaScript", "Express", "MongoDB", 1, 1, "GCP", "Cloud Run"],
    ["JavaScript", "Express", "None", 0, 1, "GCP", "Cloud Run"],
]


columns = [
    "language",
    "framework",
    "database",
    "containerized",
    "api",
    "cloud",
    "compute",
]


df = pd.DataFrame(data, columns=columns)


features = [
    "language",
    "framework",
    "database",
    "containerized",
    "api",
]


X = df[features]


# ---------------------------------------------------------
# Model 1: Cloud recommendation
# ---------------------------------------------------------

cloud_y = df["cloud"]


categorical_features = [
    "language",
    "framework",
    "database",
]


numeric_features = [
    "containerized",
    "api",
]


preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features,
        ),
        (
            "numeric",
            "passthrough",
            numeric_features,
        ),
    ]
)


cloud_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=100,
                random_state=42,
            ),
        ),
    ]
)


cloud_model.fit(X, cloud_y)


joblib.dump(
    cloud_model,
    f"{ARTIFACT_DIR}/cloud_model.joblib",
)


# ---------------------------------------------------------
# Model 2: Compute recommendation
# ---------------------------------------------------------

# Compute recommendation depends on both:
# application features + selected cloud.

X_compute = X.copy()

X_compute["cloud"] = df["cloud"]


compute_features = features + ["cloud"]


compute_categorical = [
    "language",
    "framework",
    "database",
    "cloud",
]


compute_numeric = [
    "containerized",
    "api",
]


compute_preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            compute_categorical,
        ),
        (
            "numeric",
            "passthrough",
            compute_numeric,
        ),
    ]
)


compute_model = Pipeline(
    steps=[
        ("preprocessor", compute_preprocessor),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=100,
                random_state=42,
            ),
        ),
    ]
)


compute_model.fit(
    X_compute[compute_features],
    df["compute"],
)


joblib.dump(
    compute_model,
    f"{ARTIFACT_DIR}/compute_model.joblib",
)


print("Training completed.")
print("Models saved to:", ARTIFACT_DIR)
