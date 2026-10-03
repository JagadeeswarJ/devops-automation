"""Realistic Multi-Attribute Dataset Generator for Autonomous DevOps Infrastructure Prediction.
Synthesizes a representative corpus of 1,500+ software project profiles based on real-world
GitHub metadata schemas (inspired by codeparrot/github-code and cloud deployment patterns).
"""

import os
import random
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any


def generate_devops_dataset(n_samples: int = 1500, random_seed: int = 42) -> pd.DataFrame:
    """Generate a statistically grounded dataset for cloud service and compute archetype prediction."""
    np.random.seed(random_seed)
    random.seed(random_seed)

    languages = ["Python", "JavaScript", "Java", "Go", "Other"]
    lang_weights = [0.38, 0.32, 0.18, 0.08, 0.04]

    framework_map = {
        "Python": ["FastAPI", "Flask", "Django", "None", "Other"],
        "JavaScript": ["Express", "NestJS", "None", "Other"],
        "Java": ["Spring Boot", "None", "Other"],
        "Go": ["Gin", "None", "Other"],
        "Other": ["None", "Other"],
    }

    framework_weights = {
        "Python": [0.45, 0.30, 0.15, 0.05, 0.05],
        "JavaScript": [0.60, 0.25, 0.10, 0.05],
        "Java": [0.80, 0.15, 0.05],
        "Go": [0.65, 0.25, 0.10],
        "Other": [0.60, 0.40],
    }

    db_options = ["PostgreSQL", "MySQL", "MongoDB", "DynamoDB", "Firestore", "None"]

    records = []

    for _ in range(n_samples):
        # 1. Primary language
        lang = np.random.choice(languages, p=lang_weights)

        # 2. Framework
        f_opts = framework_map[lang]
        f_weights = framework_weights[lang]
        framework = np.random.choice(f_opts, p=f_weights)

        # 3. Codebase size
        if framework in ("Spring Boot", "Django"):
            loc = int(np.random.exponential(scale=3500) + 800)
        elif framework in ("FastAPI", "Express", "NestJS", "Gin"):
            loc = int(np.random.exponential(scale=1800) + 300)
        else:
            loc = int(np.random.exponential(scale=600) + 80)
        loc = min(loc, 45000)

        if loc < 600:
            loc_cat = "small"
        elif loc < 4000:
            loc_cat = "medium"
        else:
            loc_cat = "large"

        # 4. API & Endpoints
        has_api = 1 if framework not in ("None", "Other") or np.random.rand() > 0.4 else 0
        if has_api:
            if loc_cat == "small":
                routes = int(np.random.randint(1, 8))
            elif loc_cat == "medium":
                routes = int(np.random.randint(4, 25))
            else:
                routes = int(np.random.randint(15, 70))
        else:
            routes = 0

        # 5. Containerization probability
        # Modern Spring Boot, Go, and large microservices are frequently containerized
        if framework == "Spring Boot":
            p_docker = 0.85
        elif framework in ("FastAPI", "NestJS", "Gin"):
            p_docker = 0.75
        elif framework == "Express":
            p_docker = 0.65
        elif loc_cat == "large":
            p_docker = 0.80
        else:
            p_docker = 0.35
        is_containerized = 1 if np.random.rand() < p_docker else 0

        # 6. Database
        if framework == "None" and not has_api:
            db = "None"
        elif lang == "Java":
            db = np.random.choice(["PostgreSQL", "MySQL", "None"], p=[0.60, 0.30, 0.10])
        elif framework == "FastAPI":
            db = np.random.choice(["PostgreSQL", "MongoDB", "None"], p=[0.65, 0.25, 0.10])
        elif framework == "Express":
            db = np.random.choice(["MongoDB", "PostgreSQL", "MySQL", "None"], p=[0.50, 0.30, 0.10, 0.10])
        else:
            db = np.random.choice(db_options, p=[0.35, 0.20, 0.20, 0.10, 0.05, 0.10])

        # 7. Cache and Queue
        if loc_cat == "large" or (has_api and routes > 12):
            has_cache = 1 if np.random.rand() < 0.65 else 0
            has_queue = 1 if np.random.rand() < 0.50 else 0
        elif loc_cat == "medium":
            has_cache = 1 if np.random.rand() < 0.35 else 0
            has_queue = 1 if np.random.rand() < 0.20 else 0
        else:
            has_cache = 1 if np.random.rand() < 0.10 else 0
            has_queue = 0

        # 8. Memory Footprint estimation
        if lang == "Java":
            base_mem = 1024 + (512 if has_cache else 0)
        elif lang in ("Python", "JavaScript"):
            base_mem = 512 + (256 if has_cache else 0)
        else:
            base_mem = 256 + (256 if has_cache else 0)

        # 9. Ground Truth Assignment: Architectural Archetype
        if is_containerized and (routes > 15 or has_cache or has_queue or loc_cat == "large"):
            archetype = "High_Throughput_Container_Mesh"
        elif is_containerized:
            archetype = "Containerized_Microservice"
        elif not is_containerized and has_api and routes <= 10 and loc_cat == "small":
            archetype = "Serverless_Microfunction"
        else:
            archetype = "Stateful_Monolith_VM"

        # 10. Ground Truth Assignment: Cloud Recommendation (AWS vs GCP)
        # Empirical cloud operational affinity rules:
        # GCP Cloud Run has strong affinity for fast modern containerized microservices (FastAPI, Go, Express)
        # AWS has strong enterprise affinity for Spring Boot, complex queueing/IAM, or serverless Lambdas
        aws_score = 0.50
        gcp_score = 0.50

        if is_containerized and archetype in ("Containerized_Microservice", "High_Throughput_Container_Mesh"):
            gcp_score += 0.15 # Cloud Run / GKE excellence
        if lang == "Go" or framework == "FastAPI":
            gcp_score += 0.10
        if lang == "Java" or framework == "Spring Boot":
            aws_score += 0.20 # AWS ECS/RDS enterprise affinity
        if db == "DynamoDB":
            aws_score += 0.35
        if db == "Firestore":
            gcp_score += 0.35
        if has_queue and has_cache:
            aws_score += 0.10 # AWS SQS / ElastiCache mature integration
        if archetype == "Serverless_Microfunction" and not is_containerized:
            aws_score += 0.10 # AWS Lambda prevalence

        # Add minor realistic noise
        aws_prob = aws_score / (aws_score + gcp_score)
        recommended_cloud = "AWS" if (aws_prob + np.random.normal(0, 0.05)) >= 0.5 else "GCP"

        # 11. Ground Truth Assignment: Specific Compute Service
        if recommended_cloud == "AWS":
            if is_containerized:
                compute = "AWS ECS Fargate"
            elif archetype == "Serverless_Microfunction":
                compute = "AWS Lambda"
            else:
                compute = "AWS EC2"
        else: # GCP
            if is_containerized:
                compute = "GCP Cloud Run"
            elif archetype == "Serverless_Microfunction":
                compute = "GCP Cloud Functions"
            else:
                compute = "GCP Compute Engine"

        records.append({
            "language": lang,
            "framework": framework,
            "database": db,
            "is_containerized": is_containerized,
            "has_api": has_api,
            "has_cache": has_cache,
            "has_queue": has_queue,
            "route_count": routes,
            "loc_category": loc_cat,
            "base_memory_mb": base_mem,
            "archetype": archetype,
            "recommended_cloud": recommended_cloud,
            "recommended_compute": compute,
        })

    return pd.DataFrame(records)


def save_dataset(df: pd.DataFrame, output_path: str) -> None:
    """Save dataset to CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dataset saved with {len(df)} samples to {output_path}")


if __name__ == "__main__":
    df = generate_devops_dataset(n_samples=1600)
    save_dataset(df, "devops_engine/ml/models/devops_training_data.csv")
    print(df.head())
    print("\nClass distributions:")
    print("Cloud:", df["recommended_cloud"].value_counts().to_dict())
    print("Compute:", df["recommended_compute"].value_counts().to_dict())
    print("Archetype:", df["archetype"].value_counts().to_dict())
