"""Command Line Interface for the AI Autonomous DevOps Engine.
Provides commands for repository scanning, ML cloud recommendation, cost comparison,
and context-aware question answering.
"""

import sys
import os
import argparse
from typing import Optional

from devops_engine.analyzer.codebase_scanner import scan_directory
from devops_engine.analyzer.feature_extractor import extract_ml_features
from devops_engine.ml.predictor import DevOpsPredictor
from devops_engine.decision_rules.policy_engine import apply_decision_rules
from devops_engine.rag.qa_engine import DevOpsQAEngine
from devops_engine.ml.trainer import train_and_evaluate_all


def print_banner():
    banner = """
========================================================================
   AI-DRIVEN AUTONOMOUS DEVOPS DECISION & Q&A PLATFORM (PHASE 1)
   Intelligent Multi-Cloud Provisioning (AWS & GCP) & Contextual RAG
========================================================================
"""
    print(banner)


def analyze_command(project_path: str, cloud: Optional[str] = None, strategy: str = "balanced"):
    """Run complete static analysis, ML prediction, and policy arbitration on a project."""
    print(f"\n[*] Scanning codebase at: {project_path}")
    scan = scan_directory(project_path)

    print("\n" + "=" * 55)
    print(" 1. STATIC CODEBASE ANALYSIS")
    print("=" * 55)
    print(f"  - Primary Language : {scan['primary_language']}")
    print(f"  - Primary Framework: {scan['primary_framework']}")
    print(f"  - Primary Database : {scan['primary_database']}")
    print(f"  - In-Memory Cache  : {'Redis' if scan['has_cache'] else 'None'}")
    print(f"  - Containerized    : {'Yes (Dockerfile)' if scan['is_containerized'] else 'No (Bare runtime)'}")
    print(f"  - API Endpoints    : {scan['route_count']} routes discovered")
    print(f"  - Total Code LOC   : {scan['total_loc']} lines across {scan['total_files']} files")
    if scan.get("env_vars"):
        print(f"  - Discovered Envs  : {', '.join(scan['env_vars'][:6])}")

    # Feature extraction
    features = extract_ml_features(scan)

    # ML Inference
    predictor = DevOpsPredictor()
    ml_res = predictor.predict_full_pipeline(features, forced_cloud=cloud)

    print("\n" + "=" * 55)
    print(" 2. ML CLOUD & COMPUTE INFERENCE")
    print("=" * 55)
    print(f"  - Architectural Archetype: {ml_res['archetype']}")
    print(f"  - Archetype Probabilities: {ml_res['archetype_probabilities']}")
    print(f"\n  - Recommended Provider   : {ml_res['selected_cloud']}")
    print(f"    * AWS Confidence       : {ml_res['cloud_probabilities'].get('AWS', 0.0) * 100:.1f}%")
    print(f"    * GCP Confidence       : {ml_res['cloud_probabilities'].get('GCP', 0.0) * 100:.1f}%")
    print(f"\n  - Recommended Compute    : {ml_res['recommended_compute']}")
    for s_name, s_prob in sorted(ml_res['compute_probabilities'].items(), key=lambda x: x[1], reverse=True):
        print(f"    * {s_name:<24}: {s_prob * 100:.1f}%")

    # Policy & Cost arbitration
    decision = apply_decision_rules(scan, ml_res, forced_cloud=cloud, optimization_strategy=strategy)

    print("\n" + "=" * 55)
    print(" 3. COMPARATIVE SIZING & ESTIMATED MONTHLY BILL")
    print("=" * 55)
    costs = decision["cost_comparison"]
    aws_c = costs["AWS"]
    gcp_c = costs["GCP"]
    print(f"  - AWS Total Projected Cost : ${aws_c['total_estimated_monthly_usd']:.2f} / month")
    print(f"    (Compute: ${aws_c['breakdown']['compute']}, DB: ${aws_c['breakdown']['database']}, Cache: ${aws_c['breakdown']['cache']}, Egress: ${aws_c['breakdown']['network_egress']})")
    print(f"  - GCP Total Projected Cost : ${gcp_c['total_estimated_monthly_usd']:.2f} / month")
    print(f"    (Compute: ${gcp_c['breakdown']['compute']}, DB: ${gcp_c['breakdown']['database']}, Cache: ${gcp_c['breakdown']['cache']}, Egress: ${gcp_c['breakdown']['network_egress']})")
    print(f"  - Cost-Optimized Winner    : {costs['cheaper_provider']} (Saves ${costs['monthly_difference_usd']:.2f}/mo, {costs['percentage_savings']}%)")

    if decision["override_reason"]:
        print(f"\n  [!] Rule Arbitration Notice: {decision['override_reason']}")

    print("\n" + "=" * 55)
    print(f" 4. FINAL CLOUD ARCHITECTURE STACK ({decision['final_cloud']})")
    print("=" * 55)
    infra = decision["final_infrastructure"]
    print(f"  - Compute Engine  : {decision['final_compute']}")
    print(f"  - Database Tier   : {infra['database_service']}")
    print(f"  - Cache Tier      : {infra['cache_service']}")
    print(f"  - Object Storage  : {infra['storage_service']}")
    print(f"  - Observability   : {infra['monitoring_service']}")
    print(f"  - IAM / Security  : {infra['security_iam']}")
    print(f"  - Networking      : {infra['networking']}")

    print("\n" + "=" * 55)
    print(" 5. DEVSECOPS POLICY & VALIDATION GATES")
    print("=" * 55)
    for p in decision["policy_checks"]:
        print(f"  [{p['status']:<15}] {p['gate']}: {p['message']}")

    return scan, ml_res, decision


def ask_command(project_path: str, question: Optional[str] = None, cloud: Optional[str] = None):
    """Run Q&A and suggest context-aware questions."""
    scan, ml_res, decision = analyze_command(project_path, cloud=cloud)

    print("\n" + "=" * 55)
    print(" 6. CONTEXT-AWARE APPLICATION Q&A (RAG ENGINE)")
    print("=" * 55)
    qa = DevOpsQAEngine()
    print("[*] Indexing codebase chunks, architecture decisions, and cloud knowledge docs...")
    qa.set_context(project_path, scan, decision)

    if not question:
        print("\nSuggested Context-Specific Questions for this Application:")
        questions = qa.generate_contextual_questions()
        for idx, q in enumerate(questions, 1):
            print(f"  {idx}. {q}")
        print("\nPrompting answer for Question #1:")
        question = questions[0]

    print(f"\nUser Query: {question}")
    result = qa.answer_question(question)
    print(f"\nMode: {result['source_mode']}")
    print("-" * 55)
    print(result["answer"])
    print("-" * 55)


def main():
    parser = argparse.ArgumentParser(description="AI DevOps Autonomous Decision Engine")
    subparsers = parser.add_subparsers(dest="command")

    # Analyze subparser
    analyze_p = subparsers.add_parser("analyze", help="Analyze repository and generate ML recommendations")
    analyze_p.add_argument("project", help="Path to project codebase")
    analyze_p.add_argument("--cloud", choices=["AWS", "GCP"], help="Force specific cloud provider")
    analyze_p.add_argument("--strategy", choices=["balanced", "cheapest", "performance"], default="balanced", help="Optimization strategy")

    # Ask subparser
    ask_p = subparsers.add_parser("ask", help="Ask context-aware question about codebase and deployment")
    ask_p.add_argument("project", help="Path to project codebase")
    ask_p.add_argument("--query", "-q", help="Custom question (optional)")
    ask_p.add_argument("--cloud", choices=["AWS", "GCP"], help="Target cloud constraint")

    # Train subparser
    subparsers.add_parser("train", help="Retrain ML models and generate evaluation metrics")

    args = parser.parse_args()
    print_banner()

    if args.command == "analyze":
        analyze_command(args.project, cloud=args.cloud, strategy=args.strategy)
    elif args.command == "ask":
        ask_command(args.project, question=args.query, cloud=args.cloud)
    elif args.command == "train":
        train_and_evaluate_all()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
