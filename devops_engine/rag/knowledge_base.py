"""Curated Cloud Architecture and DevOps Knowledge Base for AWS and GCP.
Provides factual, verified architectural patterns, service capabilities, cost profiles, and security standards.
"""

from typing import List, Dict, Any


CLOUD_KNOWLEDGE_DOCS = [
    {
        "id": "aws-ecs-fargate",
        "title": "AWS ECS Fargate Container Architecture",
        "category": "AWS Compute",
        "content": (
            "AWS Elastic Container Service (ECS) with AWS Fargate is a serverless container compute engine. "
            "It runs containers without requiring EC2 instance provisioning, patching, or OS management. "
            "Key characteristics: Fargate scales horizontally based on CPU or memory target-tracking policies. "
            "Networking: Tasks execute inside an AWS VPC and can be attached to private subnets with an Application "
            "Load Balancer (ALB) handling HTTPS ingress, health checks, and path-based routing. "
            "Use cases: Production microservices, REST APIs with steady traffic, background workers, and containerized "
            "applications built with Docker. Cost: Billed per vCPU-hour and memory-GB-hour with zero idle instance cost."
        )
    },
    {
        "id": "aws-lambda",
        "title": "AWS Lambda Serverless Compute Architecture",
        "category": "AWS Compute",
        "content": (
            "AWS Lambda is an event-driven, serverless computing service that executes code in response to HTTP requests "
            "(via API Gateway) or cloud events (S3, SQS, DynamoDB Streams). "
            "Key characteristics: Instant auto-scaling from 0 to thousands of concurrent requests. Scales to zero when idle. "
            "Execution duration limit is 15 minutes. "
            "Cold start: Handled via Provisioned Concurrency or lightweight runtimes (Node.js, Python, Go). "
            "Use cases: Webhooks, lightweight REST microfunctions, asynchronous event consumers, and intermittent traffic. "
            "Cost: 1 million free requests per month, followed by $0.20 per million requests + $0.0000166667 per GB-second."
        )
    },
    {
        "id": "gcp-cloud-run",
        "title": "Google Cloud Run Serverless Container Architecture",
        "category": "GCP Compute",
        "content": (
            "Google Cloud Run is a fully managed serverless platform that automatically runs and scales containerized applications. "
            "Key characteristics: Directly deploys any container image listening on an HTTP port. Supports up to 1,000 concurrent "
            "requests per container instance (unlike AWS Lambda's 1-request-per-instance model), yielding significant cost savings. "
            "Fast scaling: Scales from 0 to dozens of instances in under 2 seconds. Min-instances setting eliminates cold starts. "
            "Networking: Built-in TLS certificates, integrated custom domains, and Serverless VPC Access for private database connectivity. "
            "Use cases: Modern containerized web APIs (FastAPI, Express, Spring Boot, Gin), web apps, and microservices. "
            "Cost: Free tier of 2 million requests/month, 360,000 vCPU-seconds, and 180,000 GiB-seconds."
        )
    },
    {
        "id": "gcp-cloud-functions",
        "title": "Google Cloud Functions (2nd Gen)",
        "category": "GCP Compute",
        "content": (
            "Google Cloud Functions (2nd gen) is built on top of Cloud Run and Google Eventarc. "
            "It provides event-driven serverless execution with support for 90+ event sources. "
            "Key characteristics: Concurrency support (up to 1,000 concurrent requests per function instance), "
            "up to 60-minute execution timeouts for HTTP functions, and native integration with Cloud Storage and Pub/Sub. "
            "Use cases: Serverless webhooks, lightweight APIs, event transformers, and file processing."
        )
    },
    {
        "id": "aws-rds-postgresql",
        "title": "Amazon RDS for PostgreSQL Architecture and Best Practices",
        "category": "AWS Database",
        "content": (
            "Amazon Relational Database Service (RDS) for PostgreSQL provides managed relational database hosting. "
            "Features: Automated backups with point-in-time recovery, Multi-AZ replication for high availability, "
            "read replicas for read-heavy workloads, and automated minor version patching. "
            "Security: Databases should be deployed strictly within private DB subnets across at least 2 Availability Zones. "
            "Public IP should be disabled. Connections should require SSL/TLS and authenticate using AWS Secrets Manager credentials."
        )
    },
    {
        "id": "gcp-cloud-sql",
        "title": "Google Cloud SQL for PostgreSQL Architecture",
        "category": "GCP Database",
        "content": (
            "Google Cloud SQL provides fully managed relational database services for PostgreSQL, MySQL, and SQL Server. "
            "Features: Automated storage increase, automatic daily backups, regional High Availability with automatic failover, "
            "and built-in IAM database authentication. "
            "Connectivity: Applications connect via Cloud SQL Auth Proxy or Private Service Access (internal RFC 1918 VPC IP) "
            "ensuring the database is never exposed to the public internet."
        )
    },
    {
        "id": "aws-vs-gcp-tradeoffs",
        "title": "Architectural and Cost Trade-offs: AWS vs GCP",
        "category": "Cloud Comparison",
        "content": (
            "Comparison of AWS and GCP for application deployment: "
            "1. Serverless Containers: GCP Cloud Run supports request concurrency (multiple requests handled by one container instance), "
            "whereas AWS Lambda bills per invocation. AWS ECS Fargate requires a persistent task or auto-scaling step, making "
            "Cloud Run more cost-effective for variable HTTP traffic. "
            "2. Enterprise Ecosystem: AWS offers more mature enterprise compliance, broader region availability, and deeper integration "
            "with legacy Spring Boot and enterprise IAM topologies. "
            "3. Networking & Egress: GCP offers simpler global VPC networking without region-bound VPC peering, and generally lower egress costs. "
            "4. Operational Simplicity: GCP Cloud Run requires significantly less Terraform and IAM boilerplate than AWS ECS + ALB + Target Groups."
        )
    },
    {
        "id": "devsecops-container-security",
        "title": "DevSecOps and Container Hardening Standards",
        "category": "Security Standards",
        "content": (
            "Standard security requirements for cloud container deployments (referencing Vargas et al. and Trivy/Checkov guidelines): "
            "1. Multi-stage builds to avoid leaking compilers, test code, or build secrets into the final image. "
            "2. Non-root user execution: specify USER appuser rather than running as root (UID 0). "
            "3. Liveness and Readiness Probes: Applications must declare HTTP endpoints (e.g., /health) so load balancers can detect failures. "
            "4. Secret injection: Database passwords, JWT secret keys, and API tokens must never be hardcoded or baked into Dockerfiles. "
            "They must be injected at runtime via AWS Secrets Manager or GCP Secret Manager environment variables."
        )
    }
]


def get_all_knowledge_docs() -> List[Dict[str, Any]]:
    """Return all curated cloud knowledge base documents."""
    return CLOUD_KNOWLEDGE_DOCS
