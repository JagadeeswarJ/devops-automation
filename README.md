# AI-Driven Autonomous DevOps Platform (Phase 1)

Intelligent multi-cloud decision engine (AWS vs. GCP) and context-aware RAG question-answering framework.

---

## 1. Prerequisites & Environment Setup

> **Note on Python Version:** This project requires **Python 3.12** (PyTorch and Sentence-Transformers do not have pre-built wheels for Python 3.15 yet).

### Step 1: Install Python 3.12 (if not already installed)
```powershell
winget install Python.Python.3.12
```
*(Or download the installer from [python.org](https://www.python.org/downloads/release/python-31210/)).*

### Step 2: Create & Activate Virtual Environment
Open PowerShell and run:
```powershell
# Navigate to project root
cd "e:\079_data\VNR\SEM_7\Major Project"

# Create virtual environment bound to Python 3.12
py -3.12 -m venv .venv

# If script execution is disabled, allow it for this terminal session:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate the virtual environment:
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 2. How to Run the Application & Demo

> **Important:** Always change directory into `devops_engine` before executing commands:
> ```powershell
> cd "e:\079_data\VNR\SEM_7\Major Project\devops_engine"
> ```

### A. Interactive Web Dashboard (Recommended for Demo & Examiner Review)
Launches the full browser UI for real-time codebase scanning, side-by-side AWS vs. GCP cost comparisons, ML probability charts, and interactive RAG Q&A:
```powershell
streamlit run app.py
```
*Access in browser at:* `http://localhost:8501`

---

### B. Automated Console Demo (All 5 Scenarios in 15 Seconds)
Executes a complete automated test across all sample stacks (FastAPI, Express, Spring Boot, Serverless Python, Policy Overrides, and RAG Q&A):
```powershell
python run_demo.py
```

---

### C. Command-Line Interface (CLI)

#### Analyze a Target Codebase:
```powershell
# Auto-select optimal cloud (ML decides)
python cli.py analyze sample_projects/fastapi_microservice

# Enforce a specific cloud constraint (e.g. AWS only)
python cli.py analyze sample_projects/fastapi_microservice --cloud AWS

# Enforce cheapest monthly cost optimization
python cli.py analyze sample_projects/fastapi_microservice --strategy cheapest
```

#### Context-Aware RAG Q&A:
```powershell
# View auto-generated diagnostic questions and answers
python cli.py ask sample_projects/fastapi_microservice

# Ask a custom question with exact file and line citations
python cli.py ask sample_projects/fastapi_microservice -q "Why was GCP chosen over AWS?"
```

---

### D. Automated Verification & Machine Learning Metrics

#### Run Automated Unit Test Suite (7/7 Passing):
```powershell
pytest tests -v
```

#### View ML Model Accuracy & Evaluation Benchmark:
```powershell
python evaluate_models.py
```

#### Retrain ML Models (Optional):
```powershell
python train.py
```

---

## 3. Project Structure

All application code, models, datasets, sample microservices, and unit tests reside in `devops_engine/`:

```
devops_engine/
|-- analyzer/           # Static scanner, AST route parser, 10-D feature extractor
|-- ml/                 # Random Forest models, dataset generator, predictor
|   |-- models/         # Serialized .joblib model files & evaluation metrics
|-- decision_rules/     # AWS vs. GCP cost sizing engine & DevSecOps policy gates
|-- rag/                # Dense vector store (MiniLM-L6-v2), chunker, QA engine
|-- sample_projects/    # 4 target test apps (FastAPI, Express, Spring Boot, Serverless)
|-- tests/              # 7 automated unit tests (test_analyzer, test_ml, test_rag)
|-- app.py              # Interactive Streamlit Web Dashboard
|-- cli.py              # Command-Line Interface (analyze & ask)
|-- run_demo.py         # Automated 15-second console demo script
|-- evaluate_models.py  # Model evaluation benchmark & accuracy reporter
|-- train.py            # ML pipeline retrainer
```

---

## 4. Documentation References

* **Complete Technical Workflow & Architecture:** [`project-workflow.md`](project-workflow.md)
  - Detailed problem formulation, literature gaps (19 research papers), internal algorithms, mathematical models, and scenario walkthroughs.
* **Architecture Diagrams Preview:** Open [`docs/DIAGRAMS_PREVIEW.html`](docs/DIAGRAMS_PREVIEW.html) in any browser to snip Mermaid diagrams (`Win + Shift + S`) for presentations.
