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
