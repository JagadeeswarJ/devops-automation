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
