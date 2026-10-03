"""Feature Extractor for ML Pipeline.
Maps the analyzed codebase metadata into structured feature representations for inference.
"""

from typing import Dict, Any
import pandas as pd


def extract_ml_features(scan_result: Dict[str, Any]) -> Dict[str, Any]:
    """Convert scan results into a clean dictionary of features for ML models."""
    lang = scan_result.get("primary_language", "Unknown")
    if lang not in {"Python", "JavaScript", "TypeScript", "Java", "Go"}:
        lang = "Other"
    if lang == "TypeScript":
        lang = "JavaScript"

    framework = scan_result.get("primary_framework", "None")
    known_frameworks = {"FastAPI", "Flask", "Django", "Express", "Spring Boot", "NestJS", "Gin"}
    if framework not in known_frameworks:
        framework = "Other" if framework != "None" else "None"

    db = scan_result.get("primary_database", "None")
    known_dbs = {"PostgreSQL", "MySQL", "MongoDB", "DynamoDB", "Firestore", "None"}
    if db not in known_dbs:
        db = "PostgreSQL" if "SQL" in db.upper() else "MongoDB"

    loc = scan_result.get("total_loc", 0)
    if loc < 600:
        loc_category = "small"
    elif loc < 4000:
        loc_category = "medium"
    else:
        loc_category = "large"

    is_containerized = int(scan_result.get("is_containerized", False))
    has_api = int(scan_result.get("has_api", False))
    has_cache = int(scan_result.get("has_cache", False))
    has_queue = int(scan_result.get("has_queue", False))
    route_count = scan_result.get("route_count", 0)

    # Inferred memory requirements based on runtime footprint
    if lang == "Java":
        base_memory_mb = 1024
    elif lang in ("Python", "JavaScript"):
        base_memory_mb = 512
    elif lang == "Go":
        base_memory_mb = 256
    else:
        base_memory_mb = 512

    if has_cache:
        base_memory_mb += 256

    return {
        "language": lang,
        "framework": framework,
        "database": db,
        "is_containerized": is_containerized,
        "has_api": has_api,
        "has_cache": has_cache,
        "has_queue": has_queue,
        "route_count": route_count,
        "loc_category": loc_category,
        "base_memory_mb": base_memory_mb,
    }


def to_dataframe(feature_dict: Dict[str, Any]) -> pd.DataFrame:
    """Format single feature dict into DataFrame row."""
    return pd.DataFrame([feature_dict])
