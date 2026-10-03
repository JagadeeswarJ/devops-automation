"""Machine Learning Predictor for Cloud Infrastructure and Architecture.
Loads trained scikit-learn pipelines and provides probabilistic recommendations for:
- Deployment Archetype
- Cloud Provider (AWS vs GCP)
- Compute Service Target
- Auxiliary Infrastructure Services Mapping
"""

import os
import joblib
import pandas as pd
from typing import Dict, Any, Tuple

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

# Cloud Infrastructure Service Mappings for AWS and GCP
INFRASTRUCTURE_CATALOG = {
    "AWS": {
        "compute_services": {
            "AWS Lambda": {
                "type": "Serverless Function",
                "scaling": "Auto 0 to 10,000+ concurrent executions",
                "cold_start_mitigation": "Provisioned Concurrency",
                "protocol": "API Gateway HTTP/REST",
            },
            "AWS ECS Fargate": {
                "type": "Managed Serverless Container PaaS",
                "scaling": "Horizontal Target-Tracking Auto Scaling",
                "cold_start_mitigation": "Always-on minimum replicas",
                "protocol": "Application Load Balancer (ALB)",
            },
            "AWS EC2": {
                "type": "Virtual Machine Compute Instance (t3/c6i)",
                "scaling": "Auto Scaling Group (ASG)",
                "cold_start_mitigation": "Warm Standby Pool",
                "protocol": "Application Load Balancer (ALB)",
            }
        },
        "database": {
            "PostgreSQL": "Amazon RDS for PostgreSQL (Multi-AZ)",
            "MySQL": "Amazon RDS for MySQL (Multi-AZ)",
            "MongoDB": "Amazon DocumentDB (MongoDB-compatible)",
            "DynamoDB": "Amazon DynamoDB (On-Demand NoSQL)",
            "Firestore": "Amazon DocumentDB",
            "None": "None Required",
        },
        "cache": {
            "Redis": "Amazon ElastiCache for Redis (In-Memory Cluster)",
            "None": "None Required"
        },
        "queue": {
            "MessageQueue": "Amazon SQS (Simple Queue Service) + SNS",
            "None": "None Required"
        },
        "storage": "Amazon S3 (Simple Storage Service)",
        "monitoring": "Amazon CloudWatch Metrics & Logs + X-Ray Tracing",
        "iam_security": "AWS IAM Roles for Service Accounts / Task Execution Role",
        "networking": "AWS VPC (Public & Private Isolated Subnets, NAT Gateway)"
    },
    "GCP": {
        "compute_services": {
            "GCP Cloud Run": {
                "type": "Managed Serverless Container Runtime",
                "scaling": "Rapid auto-scaling from 0 to 1,000 instances",
                "cold_start_mitigation": "min-instances configuration",
                "protocol": "Cloud Run Direct HTTPS / Cloud Load Balancing",
            },
            "GCP Cloud Functions": {
                "type": "Serverless Event-Driven Functions (Gen 2)",
                "scaling": "Event/HTTP auto-scaling",
                "cold_start_mitigation": "min-instances configuration",
                "protocol": "HTTP Trigger / Cloud Eventarc",
            },
            "GCP Compute Engine": {
                "type": "Virtual Machine Compute Instance (e2/n2)",
                "scaling": "Managed Instance Groups (MIG)",
                "cold_start_mitigation": "Pre-provisioned VM templates",
                "protocol": "Google Cloud External HTTPS Load Balancer",
            }
        },
        "database": {
            "PostgreSQL": "Google Cloud SQL for PostgreSQL (High Availability)",
            "MySQL": "Google Cloud SQL for MySQL (High Availability)",
            "MongoDB": "MongoDB Atlas on GCP / Cloud Firestore",
            "DynamoDB": "Google Cloud Firestore (Datastore Mode)",
            "Firestore": "Google Cloud Firestore (Native NoSQL)",
            "None": "None Required",
        },
        "cache": {
            "Redis": "Google Cloud Memorystore for Redis",
            "None": "None Required"
        },
        "queue": {
            "MessageQueue": "Google Cloud Pub/Sub",
            "None": "None Required"
        },
        "storage": "Google Cloud Storage (GCS Multi-Region)",
        "monitoring": "Google Cloud Monitoring & Cloud Logging (Operations Suite)",
        "iam_security": "Google Cloud IAM Workload Identity + Service Accounts",
        "networking": "Google Cloud VPC Network (Subnets, Cloud NAT, Serverless VPC Access)"
    }
}


class DevOpsPredictor:
    """Inference engine for autonomous cloud recommendations."""

    def __init__(self, model_dir: str = None):
        self.model_dir = model_dir or MODEL_DIR
        self._load_models()

    def _load_models(self):
        arch_path = os.path.join(self.model_dir, "archetype_model.joblib")
        cloud_path = os.path.join(self.model_dir, "cloud_model.joblib")
        comp_path = os.path.join(self.model_dir, "compute_model.joblib")

        if not (os.path.exists(arch_path) and os.path.exists(cloud_path) and os.path.exists(comp_path)):
            raise FileNotFoundError(
                f"Trained models not found in '{self.model_dir}'. Run devops_engine.ml.trainer first."
            )

        self.archetype_model = joblib.load(arch_path)
        self.cloud_model = joblib.load(cloud_path)
        self.compute_model = joblib.load(comp_path)

    def predict_archetype(self, features_df: pd.DataFrame) -> Tuple[str, Dict[str, float]]:
        """Predict architectural archetype and probability distribution."""
        arch = self.archetype_model.predict(features_df)[0]
        probs = self.archetype_model.predict_proba(features_df)[0]
        classes = self.archetype_model.classes_
        prob_dict = {cls_name: round(float(p), 4) for cls_name, p in zip(classes, probs)}
        return arch, prob_dict

    def predict_cloud(self, features_df: pd.DataFrame, forced_cloud: str = None) -> Tuple[str, Dict[str, float]]:
        """Predict recommended cloud provider (AWS vs GCP) or apply override."""
        probs = self.cloud_model.predict_proba(features_df)[0]
        classes = self.cloud_model.classes_
        scores = {cls_name: round(float(p), 4) for cls_name, p in zip(classes, probs)}

        if forced_cloud:
            forced_upper = forced_cloud.upper()
            if forced_upper not in ("AWS", "GCP"):
                raise ValueError(f"Forced cloud must be 'AWS' or 'GCP', got '{forced_cloud}'")
            selected_cloud = forced_upper
        else:
            selected_cloud = max(scores, key=scores.get)

        return selected_cloud, scores

    def predict_compute(self, features_df: pd.DataFrame, cloud: str) -> Tuple[str, Dict[str, float]]:
        """Predict recommended compute service conditional on features and cloud choice."""
        df_comp = features_df.copy()
        df_comp["cloud"] = cloud

        probs = self.compute_model.predict_proba(df_comp)[0]
        classes = self.compute_model.classes_
        scores = {cls_name: round(float(p), 4) for cls_name, p in zip(classes, probs)}

        # Filter only services relevant to the selected cloud
        cloud_prefix = f"{cloud} "
        cloud_scores = {k: v for k, v in scores.items() if k.startswith(cloud_prefix)}
        if not cloud_scores:
            cloud_scores = scores

        # Normalize probabilities for the filtered cloud
        total_p = sum(cloud_scores.values()) or 1.0
        normalized_scores = {k: round(v / total_p, 4) for k, v in cloud_scores.items()}
        selected_compute = max(normalized_scores, key=normalized_scores.get)

        return selected_compute, normalized_scores

    def resolve_infrastructure(
        self,
        cloud: str,
        compute: str,
        database: str,
        has_cache: bool,
        has_queue: bool
    ) -> Dict[str, Any]:
        """Construct full infrastructure stack mapping for the target cloud."""
        catalog = INFRASTRUCTURE_CATALOG.get(cloud, INFRASTRUCTURE_CATALOG["AWS"])
        compute_info = catalog["compute_services"].get(compute, {
            "type": "Managed Cloud Compute",
            "scaling": "Auto Scaling",
            "cold_start_mitigation": "Active",
            "protocol": "HTTPS"
        })

        db_service = catalog["database"].get(database, catalog["database"].get("None"))
        cache_service = catalog["cache"]["Redis"] if has_cache else catalog["cache"]["None"]
        queue_service = catalog["queue"]["MessageQueue"] if has_queue else catalog["queue"]["None"]

        return {
            "provider": cloud,
            "compute_service": compute,
            "compute_details": compute_info,
            "database_service": db_service,
            "cache_service": cache_service,
            "queue_service": queue_service,
            "storage_service": catalog["storage"],
            "monitoring_service": catalog["monitoring"],
            "security_iam": catalog["iam_security"],
            "networking": catalog["networking"],
        }

    def predict_full_pipeline(
        self,
        features: Dict[str, Any],
        forced_cloud: str = None
    ) -> Dict[str, Any]:
        """Execute full end-to-end ML prediction pipeline for an extracted feature set."""
        df = pd.DataFrame([features])

        archetype, arch_probs = self.predict_archetype(df)
        selected_cloud, cloud_probs = self.predict_cloud(df, forced_cloud=forced_cloud)
        recommended_compute, compute_probs = self.predict_compute(df, selected_cloud)

        # Also get counterfactual compute recommendation for the other cloud
        alternate_cloud = "GCP" if selected_cloud == "AWS" else "AWS"
        alt_compute, alt_compute_probs = self.predict_compute(df, alternate_cloud)

        # Resolve full infrastructure maps for primary and alternative
        primary_infra = self.resolve_infrastructure(
            selected_cloud,
            recommended_compute,
            features.get("database", "None"),
            bool(features.get("has_cache", 0)),
            bool(features.get("has_queue", 0)),
        )

        alt_infra = self.resolve_infrastructure(
            alternate_cloud,
            alt_compute,
            features.get("database", "None"),
            bool(features.get("has_cache", 0)),
            bool(features.get("has_queue", 0)),
        )

        return {
            "input_features": features,
            "archetype": archetype,
            "archetype_probabilities": arch_probs,
            "selected_cloud": selected_cloud,
            "cloud_probabilities": cloud_probs,
            "recommended_compute": recommended_compute,
            "compute_probabilities": compute_probs,
            "primary_infrastructure": primary_infra,
            "alternate_cloud": alternate_cloud,
            "alternate_compute": alt_compute,
            "alternate_compute_probabilities": alt_compute_probs,
            "alternate_infrastructure": alt_infra,
            "is_forced_cloud": forced_cloud is not None,
        }
