## 1. File structure

```text
devops-ai-demo/
│
├── train.py
├── analyzer.py
├── recommender.py
├── demo.py
├── requirements.txt
├── README.md
│
├── artifacts/
│   └── .gitkeep
│
└── sample_projects/
    │
    ├── fastapi_app/
    │   ├── main.py
    │   └── requirements.txt
    │
    ├── node_express/
    │   ├── package.json
    │   ├── server.js
    │   └── Dockerfile
    │
    └── java_spring/
        ├── pom.xml
        ├── Dockerfile
        └── src/
            └── main/
                └── java/
                    └── Application.java
```

The `artifacts/` directory will contain the trained `.joblib` models after running `train.py`.

---

# 2. File contents

## `requirements.txt`

```txt
pandas
scikit-learn
joblib
```

---

## `train.py`

This creates the small demonstration dataset and trains the ML models.

```python
import os
import joblib
import pandas as pd

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier


ARTIFACT_DIR = "artifacts"

os.makedirs(ARTIFACT_DIR, exist_ok=True)


# ---------------------------------------------------------
# Training dataset
# ---------------------------------------------------------

data = [
    # language, framework, database, containerized, api, cloud, compute
    ["Python", "FastAPI", "PostgreSQL", 0, 1, "AWS", "Lambda"],
    ["Python", "Flask", "None", 0, 1, "AWS", "Lambda"],
    ["Python", "Django", "PostgreSQL", 1, 1, "AWS", "ECS"],
    ["Python", "FastAPI", "PostgreSQL", 1, 1, "AWS", "ECS"],

    ["JavaScript", "Express", "None", 0, 1, "AWS", "Lambda"],
    ["JavaScript", "Express", "MongoDB", 1, 1, "AWS", "ECS"],
    ["JavaScript", "Express", "PostgreSQL", 1, 1, "AWS", "ECS"],

    ["Java", "Spring Boot", "PostgreSQL", 1, 1, "AWS", "ECS"],
    ["Java", "Spring Boot", "PostgreSQL", 1, 1, "GCP", "Cloud Run"],
    ["Java", "Spring Boot", "None", 1, 1, "GCP", "Cloud Run"],

    ["Python", "FastAPI", "PostgreSQL", 0, 1, "Azure", "Functions"],
    ["Python", "Flask", "None", 0, 1, "Azure", "Functions"],
    ["Python", "Django", "PostgreSQL", 1, 1, "Azure", "Container Apps"],

    ["JavaScript", "Express", "MongoDB", 1, 1, "GCP", "Cloud Run"],
    ["JavaScript", "Express", "None", 0, 1, "GCP", "Cloud Run"],
]


columns = [
    "language",
    "framework",
    "database",
    "containerized",
    "api",
    "cloud",
    "compute",
]


df = pd.DataFrame(data, columns=columns)


features = [
    "language",
    "framework",
    "database",
    "containerized",
    "api",
]


X = df[features]


# ---------------------------------------------------------
# Model 1: Cloud recommendation
# ---------------------------------------------------------

cloud_y = df["cloud"]


categorical_features = [
    "language",
    "framework",
    "database",
]


numeric_features = [
    "containerized",
    "api",
]


preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features,
        ),
        (
            "numeric",
            "passthrough",
            numeric_features,
        ),
    ]
)


cloud_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=100,
                random_state=42,
            ),
        ),
    ]
)


cloud_model.fit(X, cloud_y)


joblib.dump(
    cloud_model,
    f"{ARTIFACT_DIR}/cloud_model.joblib",
)


# ---------------------------------------------------------
# Model 2: Compute recommendation
# ---------------------------------------------------------

# Compute recommendation depends on both:
# application features + selected cloud.

X_compute = X.copy()

X_compute["cloud"] = df["cloud"]


compute_features = features + ["cloud"]


compute_categorical = [
    "language",
    "framework",
    "database",
    "cloud",
]


compute_numeric = [
    "containerized",
    "api",
]


compute_preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            compute_categorical,
        ),
        (
            "numeric",
            "passthrough",
            compute_numeric,
        ),
    ]
)


compute_model = Pipeline(
    steps=[
        ("preprocessor", compute_preprocessor),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=100,
                random_state=42,
            ),
        ),
    ]
)


compute_model.fit(
    X_compute[compute_features],
    df["compute"],
)


joblib.dump(
    compute_model,
    f"{ARTIFACT_DIR}/compute_model.joblib",
)


print("Training completed.")
print("Models saved to:", ARTIFACT_DIR)
```

---

# `analyzer.py`

This is the codebase analysis component.

For the one-hour demo, we use simple file/dependency detection rather than a full AST/code intelligence system.

```python
import json
import os


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception:
        return ""


def analyze_codebase(project_path):

    project_path = os.path.abspath(project_path)

    files = set()

    for root, _, filenames in os.walk(project_path):
        for filename in filenames:
            relative_path = os.path.relpath(
                os.path.join(root, filename),
                project_path,
            )

            files.add(relative_path.replace("\\", "/"))


    # -----------------------------------------------------
    # Detect language
    # -----------------------------------------------------

    language = "Unknown"

    if any(
        file.endswith(".py")
        for file in files
    ):
        language = "Python"

    elif any(
        file.endswith(".js")
        for file in files
    ):
        language = "JavaScript"

    elif any(
        file.endswith(".java")
        for file in files
    ):
        language = "Java"


    # -----------------------------------------------------
    # Detect framework
    # -----------------------------------------------------

    framework = "Unknown"


    package_json_path = os.path.join(
        project_path,
        "package.json",
    )

    package_content = read_file(package_json_path)

    if "express" in package_content.lower():
        framework = "Express"


    requirements_path = os.path.join(
        project_path,
        "requirements.txt",
    )

    requirements_content = read_file(
        requirements_path
    ).lower()


    if "fastapi" in requirements_content:
        framework = "FastAPI"

    elif "flask" in requirements_content:
        framework = "Flask"

    elif "django" in requirements_content:
        framework = "Django"


    pom_path = os.path.join(
        project_path,
        "pom.xml",
    )

    pom_content = read_file(pom_path).lower()

    if "spring-boot" in pom_content:
        framework = "Spring Boot"


    # -----------------------------------------------------
    # Detect database
    # -----------------------------------------------------

    database = "None"

    combined_content = (
        package_content
        + requirements_content
        + pom_content
    ).lower()


    if "mongodb" in combined_content:
        database = "MongoDB"

    elif (
        "postgresql" in combined_content
        or "postgres" in combined_content
    ):
        database = "PostgreSQL"

    elif "mysql" in combined_content:
        database = "MySQL"


    # -----------------------------------------------------
    # Detect containerization
    # -----------------------------------------------------

    containerized = (
        "Dockerfile" in files
    )


    # -----------------------------------------------------
    # Detect API
    # -----------------------------------------------------

    api = False

    api_keywords = [
        "express",
        "fastapi",
        "flask",
        "spring",
        "rest",
        "@app.get",
        "@app.post",
        "router",
    ]


    for keyword in api_keywords:

        if keyword.lower() in combined_content:

            api = True
            break


    return {
        "language": language,
        "framework": framework,
        "database": database,
        "containerized": int(containerized),
        "api": int(api),
    }
```

---

# `recommender.py`

This loads the trained models and makes the actual ML prediction.

```python
import os
import joblib
import pandas as pd


ARTIFACT_DIR = "artifacts"


cloud_model = joblib.load(
    f"{ARTIFACT_DIR}/cloud_model.joblib"
)


compute_model = joblib.load(
    f"{ARTIFACT_DIR}/compute_model.joblib"
)


# ---------------------------------------------------------
# Cloud service mapping
# ---------------------------------------------------------

CLOUD_SERVICES = {

    "AWS": {
        "Lambda": {
            "database": {
                "PostgreSQL": "Amazon RDS",
                "MongoDB": "Amazon DocumentDB",
                "None": "None",
            },
            "storage": "Amazon S3",
        },

        "ECS": {
            "database": {
                "PostgreSQL": "Amazon RDS",
                "MongoDB": "Amazon DocumentDB",
                "None": "None",
            },
            "storage": "Amazon S3",
        },
    },


    "Azure": {
        "Functions": {
            "database": {
                "PostgreSQL": "Azure Database for PostgreSQL",
                "MongoDB": "Azure Cosmos DB",
                "None": "None",
            },
            "storage": "Azure Blob Storage",
        },

        "Container Apps": {
            "database": {
                "PostgreSQL": "Azure Database for PostgreSQL",
                "MongoDB": "Azure Cosmos DB",
                "None": "None",
            },
            "storage": "Azure Blob Storage",
        },
    },


    "GCP": {
        "Cloud Run": {
            "database": {
                "PostgreSQL": "Cloud SQL",
                "MongoDB": "MongoDB Atlas",
                "None": "None",
            },
            "storage": "Google Cloud Storage",
        },
    },
}


def predict_cloud(features, forced_cloud=None):

    df = pd.DataFrame([features])


    probabilities = cloud_model.predict_proba(df)[0]

    classes = cloud_model.classes_


    scores = {
        cloud: float(probability)
        for cloud, probability
        in zip(classes, probabilities)
    }


    if forced_cloud:

        if forced_cloud not in scores:

            raise ValueError(
                f"Unsupported cloud: {forced_cloud}"
            )

        selected_cloud = forced_cloud

    else:

        selected_cloud = max(
            scores,
            key=scores.get,
        )


    return selected_cloud, scores


def predict_compute(
    features,
    cloud,
):

    df = pd.DataFrame([{
        **features,
        "cloud": cloud,
    }])


    compute = compute_model.predict(df)[0]


    probabilities = compute_model.predict_proba(df)[0]

    classes = compute_model.classes_


    scores = {
        service: float(probability)
        for service, probability
        in zip(classes, probabilities)
    }


    return compute, scores


def get_resources(
    cloud,
    compute,
    database,
):

    cloud_data = CLOUD_SERVICES[cloud]

    compute_data = cloud_data[compute]


    database_service = compute_data[
        "database"
    ].get(
        database,
        "Managed Database",
    )


    return {
        "compute": f"{cloud} {compute}",
        "database": database_service,
        "storage": compute_data["storage"],
    }


def recommend(
    features,
    forced_cloud=None,
):

    cloud, cloud_scores = predict_cloud(
        features,
        forced_cloud,
    )


    compute, compute_scores = predict_compute(
        features,
        cloud,
    )


    resources = get_resources(
        cloud,
        compute,
        features["database"],
    )


    return {
        "cloud": cloud,
        "cloud_scores": cloud_scores,
        "compute": compute,
        "compute_scores": compute_scores,
        "resources": resources,
    }
```

---

# `demo.py`

This is the file you actually run during your demonstration.

```python
import argparse

from analyzer import analyze_codebase
from recommender import recommend


def percentage(value):

    return f"{value * 100:.1f}%"


def print_separator():

    print(
        "\n"
        + "=" * 60
    )


def main():

    parser = argparse.ArgumentParser(
        description="AI DevOps Feasibility Demo"
    )


    parser.add_argument(
        "project",
        help="Path to application codebase",
    )


    parser.add_argument(
        "--cloud",
        choices=[
            "AWS",
            "Azure",
            "GCP",
        ],
        help="Force deployment to a specific cloud",
    )


    args = parser.parse_args()


    # -----------------------------------------------------
    # Analyze codebase
    # -----------------------------------------------------

    print_separator()

    print(
        "        AI DEVOPS DECISION ENGINE"
    )

    print_separator()


    print(
        "\nAnalyzing codebase..."
    )


    features = analyze_codebase(
        args.project
    )


    print("\nDetected Application:")

    print(
        f"Language       : "
        f"{features['language']}"
    )

    print(
        f"Framework      : "
        f"{features['framework']}"
    )

    print(
        f"Database       : "
        f"{features['database']}"
    )

    print(
        f"Containerized  : "
        f"{bool(features['containerized'])}"
    )

    print(
        f"API            : "
        f"{bool(features['api'])}"
    )


    # -----------------------------------------------------
    # ML recommendation
    # -----------------------------------------------------

    result = recommend(
        features,
        args.cloud,
    )


    print_separator()

    print(
        "              ML RECOMMENDATION"
    )

    print_separator()


    print(
        f"\nSelected Cloud : "
        f"{result['cloud']}"
    )


    print("\nCloud Probabilities:")

    for cloud, score in sorted(
        result["cloud_scores"].items(),
        key=lambda item: item[1],
        reverse=True,
    ):

        print(
            f"  {cloud:<10} "
            f"{percentage(score)}"
        )


    print(
        "\nRecommended Compute:"
    )

    print(
        f"  {result['compute']}"
    )


    print("\nCompute Probabilities:")

    for service, score in sorted(
        result["compute_scores"].items(),
        key=lambda item: item[1],
        reverse=True,
    ):

        print(
            f"  {service:<20} "
            f"{percentage(score)}"
        )


    # -----------------------------------------------------
    # Resources
    # -----------------------------------------------------

    print_separator()

    print(
        "           CLOUD ARCHITECTURE"
    )

    print_separator()


    resources = result["resources"]


    print(
        f"\nCompute  : "
        f"{resources['compute']}"
    )

    print(
        f"Database : "
        f"{resources['database']}"
    )

    print(
        f"Storage  : "
        f"{resources['storage']}"
    )


    # -----------------------------------------------------
    # Explanation
    # -----------------------------------------------------

    print_separator()

    print(
        "                EXPLANATION"
    )

    print_separator()


    print(
        f"\n- {features['language']} "
        f"application detected."
    )

    print(
        f"- {features['framework']} "
        f"framework detected."
    )


    if features["containerized"]:

        print(
            "- Docker containerization detected; "
            "container-oriented compute is suitable."
        )

    else:

        print(
            "- No Dockerfile detected; "
            "serverless compute is considered."
        )


    if features["database"] != "None":

        print(
            f"- {features['database']} database detected; "
            "managed database service recommended."
        )

    else:

        print(
            "- No persistent database detected."
        )


    if args.cloud:

        print(
            f"- User constraint enforced: "
            f"{args.cloud} only."
        )


    print_separator()

    print(
        "Deployment architecture generated."
    )

    print(
        "Actual cloud provisioning is the "
        "next engineering stage."
    )

    print_separator()


if __name__ == "__main__":
    main()
```

---

# Sample project 1 — FastAPI

## `sample_projects/fastapi_app/main.py`

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():

    return {
        "message": "FastAPI application"
    }


@app.get("/users")
def users():

    return {
        "users": []
    }
```

---

## `sample_projects/fastapi_app/requirements.txt`

```txt
fastapi
uvicorn
psycopg2-binary
```

---

# Sample project 2 — Node.js

## `sample_projects/node_express/package.json`

```json
{
  "name": "node-express-demo",
  "version": "1.0.0",
  "description": "Sample Node.js Express application",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "mongodb": "^6.0.0"
  }
}
```

---

## `sample_projects/node_express/server.js`

```javascript
const express = require("express");

const app = express();

app.get("/", (req, res) => {

    res.json({
        message: "Node Express application"
    });

});

app.get("/users", (req, res) => {

    res.json({
        users: []
    });

});

app.listen(3000, () => {

    console.log(
        "Server running on port 3000"
    );

});
```

---

## `sample_projects/node_express/Dockerfile`

```dockerfile
FROM node:20

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

---

# Sample project 3 — Spring Boot

## `sample_projects/java_spring/pom.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>

<project
    xmlns="http://maven.apache.org/POM/4.0.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="
        http://maven.apache.org/POM/4.0.0
        https://maven.apache.org/xsd/maven-4.0.0.xsd"
>

    <modelVersion>4.0.0</modelVersion>

    <groupId>com.demo</groupId>

    <artifactId>spring-demo</artifactId>

    <version>1.0.0</version>

    <parent>

        <groupId>
            org.springframework.boot
        </groupId>

        <artifactId>
            spring-boot-starter-parent
        </artifactId>

        <version>
            3.3.0
        </version>

    </parent>


    <dependencies>

        <dependency>

            <groupId>
                org.springframework.boot
            </groupId>

            <artifactId>
                spring-boot-starter-web
            </artifactId>

        </dependency>


        <dependency>

            <groupId>
                org.postgresql
            </groupId>

            <artifactId>
                postgresql
            </artifactId>

        </dependency>

    </dependencies>

</project>
```

---

## `sample_projects/java_spring/Dockerfile`

```dockerfile
FROM eclipse-temurin:21

WORKDIR /app

COPY target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT [
    "java",
    "-jar",
    "app.jar"
]
```

---

## `sample_projects/java_spring/src/main/java/Application.java`

```java
package com.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;


@SpringBootApplication
@RestController
public class Application {

    public static void main(String[] args) {

        SpringApplication.run(
            Application.class,
            args
        );
    }


    @GetMapping("/")
    public String home() {

        return "Spring Boot application";
    }
}
```

---

# `README.md`

```markdown
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
```

### Run sequence

After creating these files:

```bash
pip install -r requirements.txt
python train.py
python demo.py sample_projects/fastapi_app
```

Then demonstrate the user constraint:

```bash
python demo.py sample_projects/fastapi_app --cloud AWS
```

and:

```bash
python demo.py sample_projects/java_spring --cloud GCP
```

This gives you a concrete **ML-based proof of feasibility** rather than a mock UI. The important next step for the actual major project is replacing the tiny synthetic dataset in `train.py` with a real dataset and designing the **cloud-service recommendation problem** properly.
