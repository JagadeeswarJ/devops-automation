# AI-Driven Autonomous DevOps Platform — Phase 1

An intelligent multi-cloud decision engine and context-aware RAG question-answering framework for automated cloud infrastructure provisioning and application deployment.

Targeted Cloud Providers: **Amazon Web Services (AWS)** & **Google Cloud Platform (GCP)**.

---

## Phase 1 Implemented Objectives

1. **Objective 1: Codebase-Based Decision Making**
   - Deep multi-language static analysis (Python, JavaScript/TypeScript, Java, Go).
   - Automated dependency and manifest parsing (`requirements.txt`, `package.json`, `pom.xml`).
   - Architectural pattern and route discovery (`@app.get`, `router.use`, `@GetMapping`).
   - Supervised ML models (Random Forest ensembles) trained on 1,600 repository profiles.
   - Probabilistic recommendation of cloud provider (AWS vs. GCP) and compute service (Lambda, ECS Fargate, EC2 vs. Cloud Run, Cloud Functions, Compute Engine).
   - Multi-cloud monthly cost and sizing estimation under variable traffic loads.
   - Policy arbitration layer for user constraints (`--cloud AWS/GCP`, `--strategy cheapest/performance`) and DevSecOps validation gates.

2. **Objective 2: Context-Aware Application Question Answering**
   - Retrieval-Augmented Generation (RAG) using dense semantic embeddings (`sentence-transformers/all-MiniLM-L6-v2`, 384-dimensional).
   - In-memory vector store indexing chunked codebase files, architectural decision summaries, and curated AWS/GCP knowledge bases.
   - Dynamic contextual diagnostic question generator (5–7 questions per project).
   - Citation-grounded answering with file names, line numbers, and architectural trade-offs.

---

## Quick Start & Verification

### 1. Run the End-to-End Automated Demonstration
Runs through 5 realistic scenarios across FastAPI, Node.js Express, Java Spring Boot, policy constraints, and RAG Q&A:
```bash
python run_demo.py
```

### 2. Launch the Interactive Web Dashboard
Launches the Streamlit browser dashboard for live examiner presentations:
```bash
streamlit run devops_engine/app.py
```

### 3. Run the Automated Unit Test Suite
Runs all 7 unit and integration tests:
```bash
python -m unittest discover -s tests
```

### 4. View Machine Learning Model Metrics & Feature Importances
Displays test accuracy, F1 scores, 5-fold cross-validation results, and top predictive features:
```bash
python evaluate_models.py
```

### 5. Retrain the ML Models (Optional)
Regenerates the 1,600-sample dataset and retrains the scikit-learn pipelines:
```bash
python train.py
```

---

## CLI Usage

### Analyze a Codebase
```bash
# Basic analysis (ML auto-selects optimal cloud)
python -m devops_engine.cli analyze devops_engine/sample_projects/fastapi_microservice

# Enforce a specific cloud constraint
python -m devops_engine.cli analyze devops_engine/sample_projects/fastapi_microservice --cloud AWS

# Enforce cost-optimized selection
python -m devops_engine.cli analyze devops_engine/sample_projects/fastapi_microservice --strategy cheapest
```

### Context-Aware Application Q&A
```bash
# View suggested questions and answer the primary question
python -m devops_engine.cli ask devops_engine/sample_projects/fastapi_microservice

# Ask a specific question
python -m devops_engine.cli ask devops_engine/sample_projects/fastapi_microservice -q "What database and caching services are needed, and what will they cost?"
```

---

## Presentation & Report Materials
For presentation slides and report documentation matching review requirements, see:
* [CHAPTER_3_APPROACH_DESIGN_METHODOLOGY.md](CHAPTER_3_APPROACH_DESIGN_METHODOLOGY.md)
  - Overview of Phase—I Work and Outcomes
  - Refinement of Problem and Objectives based on Feedback
  - Selection of Approach / Methodology
  - Technical Approach and Key Elements
  - Supporting Analysis / Design Considerations (AWS vs. GCP Trade-offs)
  - Tools / Techniques Used
  - Justification of Selected Approach
