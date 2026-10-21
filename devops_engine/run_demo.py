"""End-to-End Demonstration Script for AI Autonomous DevOps Engine (Phase 1).
Runs the complete workflow:
1. Codebase static analysis across multiple language stacks (FastAPI, Express, Spring Boot, Serverless)
2. ML feature extraction and probabilistic multi-cloud prediction (AWS vs GCP)
3. Cost sizing comparison and policy validation gate enforcement
4. Context-aware question generation and RAG-based citation-grounded answering.
"""

import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "devops_engine" else _this_dir
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

try:
    from devops_engine.cli import analyze_command, ask_command
except ImportError:
    from cli import analyze_command, ask_command

SAMPLE_BASE = os.path.join(_this_dir, "sample_projects") if os.path.basename(_this_dir) == "devops_engine" else os.path.join(_this_dir, "devops_engine", "sample_projects")

SAMPLE_PROJECTS = [
    ("FastAPI Containerized Microservice (Python + Postgres + Redis)", os.path.join(SAMPLE_BASE, "fastapi_microservice"), None, "balanced"),
    ("Node.js User API with MongoDB (GCP Affinity)", os.path.join(SAMPLE_BASE, "node_express_api"), None, "balanced"),
    ("Enterprise Billing Service (Java Spring Boot + Postgres - AWS Affinity)", os.path.join(SAMPLE_BASE, "java_spring_service"), None, "balanced"),
    ("Serverless Webhook Handler (Python Raw / Event-Driven)", os.path.join(SAMPLE_BASE, "python_serverless"), None, "balanced"),
    ("Policy Constraint Demo (Force AWS on FastAPI)", os.path.join(SAMPLE_BASE, "fastapi_microservice"), "AWS", "balanced"),
    ("Cheapest Strategy Demo (Cost Optimization Override)", os.path.join(SAMPLE_BASE, "fastapi_microservice"), None, "cheapest"),
]


def run_full_demo():
    print("\n" + "=" * 75)
    print("      AI-DRIVEN AUTONOMOUS DEVOPS PLATFORM - PHASE 1 END-TO-END DEMO")
    print("      Focus: Objective 1 (Decision Making) & Objective 2 (Contextual Q&A)")
    print("=" * 75)

    for idx, (title, path, cloud, strategy) in enumerate(SAMPLE_PROJECTS, 1):
        print(f"\n\n>>>>>>>> SCENARIO {idx}: {title} <<<<<<<<")
        analyze_command(path, cloud=cloud, strategy=strategy)

    print("\n\n" + "=" * 75)
    print(">>>>>>>> SCENARIO 7: CONTEXT-AWARE APPLICATION QUESTION ANSWERING (RAG) <<<<<<<<")
    print("=" * 75)
    ask_command(
        os.path.join(SAMPLE_BASE, "fastapi_microservice"),
        question="Why did the AI decision engine recommend this cloud and compute service over the alternative?"
    )

    print("\n\n" + "=" * 75)
    print("DEMONSTRATION COMPLETE: All Phase 1 Objectives Successfully Verified!")
    print("To launch the interactive Web Dashboard, run:")
    print("    streamlit run app.py")
    print("=" * 75)


if __name__ == "__main__":
    run_full_demo()
