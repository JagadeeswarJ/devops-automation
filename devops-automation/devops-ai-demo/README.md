# AI DevOps Decision Engine

A feasibility prototype for an AI-driven autonomous
DevOps platform.

The prototype demonstrates:

1. Codebase analysis
2. ML-based cloud recommendation
3. ML-based compute-service recommendation
4. Multi-cloud support
5. User cloud constraints
6. Cloud architecture generation

---

## Architecture

Codebase
    |
    v
Code Analyzer
    |
    v
Feature Extraction
    |
    v
Random Forest ML Models
    |
    +---- Cloud Recommendation
    |
    +---- Compute Recommendation
    |
    v
Cloud Architecture
    |
    v
AWS / Azure / GCP


---

## Installation

Create a virtual environment:

python -m venv .venv

Activate on Windows:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt


---

## Train the models

python train.py


This creates:

artifacts/cloud_model.joblib
artifacts/compute_model.joblib


---

## Run the demo

FastAPI:

python demo.py sample_projects/fastapi_app


Node.js:

python demo.py sample_projects/node_express


Spring Boot:

python demo.py sample_projects/java_spring


---

## Force a cloud

AWS only:

python demo.py sample_projects/node_express --cloud AWS


Azure only:

python demo.py sample_projects/node_express --cloud Azure


GCP only:

python demo.py sample_projects/java_spring --cloud GCP


---

## Current ML implementation

The prototype uses Random Forest classifiers.

Model 1:

Application features
    ->
Cloud recommendation


Model 2:

Application features + selected cloud
    ->
Compute-service recommendation


---

## Current features

- Programming language
- Framework
- Database
- Containerization
- API presence


---

## Supported clouds

AWS
Azure
GCP


---

## Important limitation

This is a feasibility prototype.

The training dataset is intentionally small and
synthetic.

For the final research project, the dataset should
be replaced with a significantly larger and
experimentally validated dataset containing:

- Application characteristics
- Cloud services
- Deployment architectures
- Resource requirements
- Cost
- Performance
- Scalability
- Reliability
- Deployment outcomes


---

## Future system

The complete project can extend this prototype with:

- GitHub integration
- AST-based source-code analysis
- Code embeddings
- RAG
- LLM-based application Q&A
- Terraform generation
- AWS deployment
- Azure deployment
- GCP deployment
- CI/CD
- Log analysis
- ML anomaly detection
- Error classification
- Automated rollback
- Auto-scaling
- Deployment reports
