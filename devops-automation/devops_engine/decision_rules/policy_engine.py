"""Decision and Policy Layer.
Applies user constraints, operational validation gates, and cost-aware arbitration
before finalizing the infrastructure recommendation.
"""

from typing import Dict, Any, List
from .cost_estimator import compare_costs


def apply_decision_rules(
    scan_result: Dict[str, Any],
    ml_result: Dict[str, Any],
    forced_cloud: str = None,
    optimization_strategy: str = "balanced"
) -> Dict[str, Any]:
    """Arbitrate ML recommendations against user constraints, optimization strategies, and policy gates."""
    strategy = optimization_strategy.lower()
    features = ml_result["input_features"]
    database = features.get("database", "None")
    has_cache = bool(features.get("has_cache", 0))

    # 1. Calculate side-by-side comparative costs
    aws_compute = ml_result["recommended_compute"] if ml_result["selected_cloud"] == "AWS" else ml_result["alternate_compute"]
    gcp_compute = ml_result["recommended_compute"] if ml_result["selected_cloud"] == "GCP" else ml_result["alternate_compute"]

    cost_comparison = compare_costs(
        aws_compute=aws_compute,
        gcp_compute=gcp_compute,
        database=database,
        has_cache=has_cache,
        traffic_tier="medium"
    )

    # 2. Finalize Provider Decision
    active_cloud = ml_result["selected_cloud"]
    override_reason = None

    if forced_cloud:
        forced_upper = forced_cloud.upper()
        if forced_upper in ("AWS", "GCP"):
            active_cloud = forced_upper
            override_reason = f"User hard constraint enforced: '{forced_upper} only'."
    elif strategy == "cheapest":
        cheaper = cost_comparison["cheaper_provider"]
        if cheaper != active_cloud:
            active_cloud = cheaper
            override_reason = (
                f"Optimization strategy 'cheapest' overrode ML choice from {ml_result['selected_cloud']} to {cheaper} "
                f"(saves ~${cost_comparison['monthly_difference_usd']}/month, {cost_comparison['percentage_savings']}%)."
            )
    elif strategy == "performance":
        override_reason = "Optimization strategy 'performance' prioritized low-latency containerized execution."

    # Active compute and infra corresponding to the active cloud
    if active_cloud == ml_result["selected_cloud"]:
        final_compute = ml_result["recommended_compute"]
        final_infra = ml_result["primary_infrastructure"]
    else:
        final_compute = ml_result["alternate_compute"]
        final_infra = ml_result["alternate_infrastructure"]

    # 3. Policy & Validation Gates (inspired by Vargas et al. [7] and Zhang et al. [10])
    policy_checks = []

    # Gate 1: Containerization Deployability Gate
    is_containerized = bool(features.get("is_containerized", 0))
    if not is_containerized and ("Fargate" in final_compute or "Cloud Run" in final_compute):
        policy_checks.append({
            "gate": "Deployability & Packaging Gate",
            "status": "WARNING",
            "message": (
                f"Application lacks a Dockerfile, but '{final_compute}' requires container packaging. "
                "Recommendation: Autonomous Dockerfile generation required prior to provisioning."
            )
        })
    else:
        policy_checks.append({
            "gate": "Deployability & Packaging Gate",
            "status": "PASS",
            "message": "Container packaging validated." if is_containerized else "Serverless/VM target is compatible with raw runtime."
        })

    # Gate 2: Database Network Security Gate
    if database != "None":
        policy_checks.append({
            "gate": "Security & Network Isolation Gate",
            "status": "PASS_WITH_POLICY",
            "message": (
                f"Managed {database} database must be provisioned inside private isolated subnets "
                f"with {active_cloud} private network peering / Serverless VPC Access. Public IP disabled."
            )
        })

    # Gate 3: Secret Management Gate
    detected_env_vars = scan_result.get("env_vars", [])
    sensitive_vars = [v for v in detected_env_vars if any(k in v.upper() for k in ["SECRET", "KEY", "PASS", "TOKEN", "AUTH"])]
    if sensitive_vars:
        policy_checks.append({
            "gate": "Secret Management Gate",
            "status": "ACTION_REQUIRED",
            "message": (
                f"Identified sensitive variables: {sensitive_vars}. "
                f"Must inject via {active_cloud} Secret Manager / Systems Manager Parameter Store."
            )
        })
    else:
        policy_checks.append({
            "gate": "Secret Management Gate",
            "status": "PASS",
            "message": "No obvious plaintext secret leaks discovered in source scan."
        })

    # Gate 4: Observability and Health Check Gate
    routes = [r.get("path", "") for r in scan_result.get("routes", [])]
    has_health_route = any(p in ["/health", "/healthz", "/ping", "/status", "/"] for p in routes)
    if not has_health_route and scan_result.get("has_api", False):
        policy_checks.append({
            "gate": "Observability & Liveness Gate",
            "status": "WARNING",
            "message": "No explicit /health endpoint detected. Container orchestrator / Load Balancer requires liveness probe."
        })
    else:
        policy_checks.append({
            "gate": "Observability & Liveness Gate",
            "status": "PASS",
            "message": "Liveness/Health probe route recognized."
        })

    return {
        "final_cloud": active_cloud,
        "final_compute": final_compute,
        "final_infrastructure": final_infra,
        "override_reason": override_reason,
        "optimization_strategy": strategy,
        "cost_comparison": cost_comparison,
        "policy_checks": policy_checks,
    }
