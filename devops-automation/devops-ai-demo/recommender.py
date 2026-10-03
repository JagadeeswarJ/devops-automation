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
