"""Cost and Resource Sizing Estimation Engine for Multi-Cloud Architectures (AWS vs GCP).
Models compute, database, cache, network egress, and storage costs using published cloud rate baselines.
"""

from typing import Dict, Any


PRICING_TABLE = {
    "AWS": {
        "compute": {
            "AWS Lambda": {
                "base_price": 0.0, # Free tier 1M requests
                "per_million_requests": 0.20,
                "gb_second": 0.0000166667,
            },
            "AWS ECS Fargate": {
                "vcpu_hourly": 0.04048, # per vCPU/hour
                "memory_gb_hourly": 0.004445, # per GB/hour
            },
            "AWS EC2": {
                "t3.small": 15.18, # monthly reserved/on-demand baseline (~$0.0208/hr)
                "t3.medium": 30.36,
            }
        },
        "database": {
            "PostgreSQL": 29.50, # db.t3.micro Multi-AZ / single AZ baseline + 20GB storage
            "MySQL": 28.00,
            "MongoDB": 45.00, # DocumentDB t3.medium instance
            "DynamoDB": 5.00, # On-demand read/write baseline
            "None": 0.0
        },
        "cache": {
            "Redis": 17.50, # cache.t3.micro
            "None": 0.0
        },
        "storage": {
            "s3_per_gb": 0.023,
            "baseline_storage_gb": 10
        },
        "network_egress_per_gb": 0.09
    },
    "GCP": {
        "compute": {
            "GCP Cloud Run": {
                "base_price": 0.0, # Free tier 2M requests
                "per_million_requests": 0.40,
                "vcpu_second": 0.00002400,
                "memory_gb_second": 0.00000250,
            },
            "GCP Cloud Functions": {
                "base_price": 0.0,
                "per_million_requests": 0.40,
                "gb_second": 0.00000250,
            },
            "GCP Compute Engine": {
                "e2-micro": 7.11,
                "e2-small": 14.22,
                "e2-medium": 28.44, # monthly on-demand baseline
            }
        },
        "database": {
            "PostgreSQL": 26.80, # Cloud SQL db-f1-micro / db-custom-1-3840 baseline
            "MySQL": 25.50,
            "MongoDB": 35.00, # Atlas on GCP entry tier
            "DynamoDB": 4.50, # Firestore Datastore mode equivalent
            "Firestore": 4.50,
            "None": 0.0
        },
        "cache": {
            "Redis": 16.00, # Memorystore 1GB basic tier
            "None": 0.0
        },
        "storage": {
            "gcs_per_gb": 0.020,
            "baseline_storage_gb": 10
        },
        "network_egress_per_gb": 0.085
    }
}


def estimate_monthly_cost(
    provider: str,
    compute_service: str,
    database: str,
    has_cache: bool,
    traffic_tier: str = "medium"
) -> Dict[str, Any]:
    """Estimate monthly operational cost for a given infrastructure configuration."""
    pricing = PRICING_TABLE.get(provider, PRICING_TABLE["AWS"])

    # Traffic assumptions
    traffic_profiles = {
        "light": {"requests_per_month": 300_000, "egress_gb": 5, "avg_duration_sec": 0.20},
        "medium": {"requests_per_month": 2_500_000, "egress_gb": 35, "avg_duration_sec": 0.25},
        "heavy": {"requests_per_month": 15_000_000, "egress_gb": 200, "avg_duration_sec": 0.30},
    }
    traffic = traffic_profiles.get(traffic_tier.lower(), traffic_profiles["medium"])
    reqs = traffic["requests_per_month"]
    egress_gb = traffic["egress_gb"]

    # 1. Compute Cost
    compute_cost = 0.0
    if provider == "AWS":
        if compute_service == "AWS Lambda":
            # 512 MB memory avg
            billable_reqs = max(0, reqs - 1_000_000)
            req_cost = (billable_reqs / 1_000_000) * pricing["compute"]["AWS Lambda"]["per_million_requests"]
            duration_cost = (billable_reqs * traffic["avg_duration_sec"] * 0.5) * pricing["compute"]["AWS Lambda"]["gb_second"]
            compute_cost = req_cost + duration_cost
        elif compute_service == "AWS ECS Fargate":
            # 1 task running 24/7 (0.5 vCPU, 1 GB RAM)
            hours = 730
            compute_cost = (0.5 * pricing["compute"]["AWS ECS Fargate"]["vcpu_hourly"] * hours) + \
                           (1.0 * pricing["compute"]["AWS ECS Fargate"]["memory_gb_hourly"] * hours)
        else: # AWS EC2
            compute_cost = pricing["compute"]["AWS EC2"]["t3.small"]
    else: # GCP
        if compute_service == "GCP Cloud Run":
            # Auto-scaled to zero, active during requests
            active_cpu_seconds = reqs * traffic["avg_duration_sec"] * 0.5
            active_mem_seconds = reqs * traffic["avg_duration_sec"] * 1.0
            cpu_cost = active_cpu_seconds * pricing["compute"]["GCP Cloud Run"]["vcpu_second"]
            mem_cost = active_mem_seconds * pricing["compute"]["GCP Cloud Run"]["memory_gb_second"]
            billable_reqs = max(0, reqs - 2_000_000)
            req_cost = (billable_reqs / 1_000_000) * pricing["compute"]["GCP Cloud Run"]["per_million_requests"]
            compute_cost = cpu_cost + mem_cost + req_cost
        elif compute_service == "GCP Cloud Functions":
            billable_reqs = max(0, reqs - 2_000_000)
            compute_cost = (billable_reqs / 1_000_000) * pricing["compute"]["GCP Cloud Functions"]["per_million_requests"]
        else: # GCP Compute Engine
            compute_cost = pricing["compute"]["GCP Compute Engine"]["e2-small"]

    # 2. Database Cost
    db_cost = pricing["database"].get(database, pricing["database"]["None"])

    # 3. Cache Cost
    cache_cost = pricing["cache"]["Redis"] if has_cache else 0.0

    # 4. Storage & Egress Cost
    storage_cost = pricing["storage"]["s3_per_gb" if provider == "AWS" else "gcs_per_gb"] * pricing["storage"]["baseline_storage_gb"]
    egress_cost = egress_gb * pricing["network_egress_per_gb"]

    total = compute_cost + db_cost + cache_cost + storage_cost + egress_cost

    return {
        "provider": provider,
        "traffic_tier": traffic_tier,
        "monthly_requests": reqs,
        "breakdown": {
            "compute": round(compute_cost, 2),
            "database": round(db_cost, 2),
            "cache": round(cache_cost, 2),
            "storage": round(storage_cost, 2),
            "network_egress": round(egress_cost, 2),
        },
        "total_estimated_monthly_usd": round(total, 2)
    }


def compare_costs(
    aws_compute: str,
    gcp_compute: str,
    database: str,
    has_cache: bool,
    traffic_tier: str = "medium"
) -> Dict[str, Any]:
    """Compare estimated monthly costs across AWS and GCP side by side."""
    aws_estimate = estimate_monthly_cost("AWS", aws_compute, database, has_cache, traffic_tier)
    gcp_estimate = estimate_monthly_cost("GCP", gcp_compute, database, has_cache, traffic_tier)

    diff = aws_estimate["total_estimated_monthly_usd"] - gcp_estimate["total_estimated_monthly_usd"]
    cheaper = "GCP" if diff > 0 else "AWS"
    pct_diff = round(abs(diff) / max(aws_estimate["total_estimated_monthly_usd"], 0.01) * 100, 1)

    return {
        "AWS": aws_estimate,
        "GCP": gcp_estimate,
        "cheaper_provider": cheaper,
        "monthly_difference_usd": round(abs(diff), 2),
        "percentage_savings": pct_diff,
    }
