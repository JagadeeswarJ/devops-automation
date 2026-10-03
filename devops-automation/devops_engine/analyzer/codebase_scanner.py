"""Comprehensive Codebase Scanner.
Performs static analysis across repository files to extract multi-language breakdown,
architectural characteristics, API routes, container configurations, and dependency graphs.
"""

import os
import re
from typing import Dict, List, Set, Any
from .dependency_parser import (
    parse_requirements_txt,
    parse_package_json,
    parse_pom_xml,
    analyze_dependencies,
)

IGNORED_DIRS = {
    ".git", ".svn", ".hg", "node_modules", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", "target", "dist",
    "build", ".idea", ".vscode", "bin", "obj"
}

EXTENSION_LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C",
}

SERVERLESS_PATTERNS = [
    re.compile(r"""def\s+(handler|lambda_handler|handle_[a-zA-Z0-9_]+)\s*\(\s*(?:event|context|req|request)""", re.IGNORECASE),
]

ROUTE_PATTERNS = [
    # FastAPI / Flask
    re.compile(r"""@(app|router|blueprint)\.(get|post|put|delete|patch|options|head)\s*\(\s*["']([^"']+)["']""", re.IGNORECASE),
    re.compile(r"""@app\.route\s*\(\s*["']([^"']+)["'](?:\s*,\s*methods\s*=\s*\[([^\]]+)\])?""", re.IGNORECASE),
    # Express.js
    re.compile(r"""(app|router)\.(get|post|put|delete|patch|all|use)\s*\(\s*["']([^"']+)["']""", re.IGNORECASE),
    # Spring Boot
    re.compile(r"""@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping)\s*\(\s*(?:value\s*=\s*)?["']([^"']+)["']""", re.IGNORECASE),
    # Go Gin / Echo
    re.compile(r"""(r|router|e|app)\.(GET|POST|PUT|DELETE|PATCH)\s*\(\s*["']([^"']+)["']""", re.IGNORECASE),
]

ENV_VAR_PATTERNS = [
    re.compile(r"""os\.(?:environ\.get|getenv)\s*\(\s*["']([A-Z0-9_]+)["']""", re.IGNORECASE),
    re.compile(r"""process\.env\.([A-Z0-9_]+)"""),
    re.compile(r"""@Value\s*\(\s*["']\$\{([A-Z0-9_]+)""", re.IGNORECASE),
    re.compile(r"""System\.(?:getenv)\s*\(\s*["']([A-Z0-9_]+)["']""", re.IGNORECASE),
]


def safe_read(file_path: str, max_chars: int = 200_000) -> str:
    """Safely read text file content up to a character limit."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_chars)
    except Exception:
        return ""


def parse_dockerfile(content: str) -> Dict[str, Any]:
    """Extract key deployment parameters from Dockerfile."""
    result = {
        "has_dockerfile": True,
        "base_image": "unknown",
        "exposed_ports": [],
        "is_multistage": False,
        "has_healthcheck": False,
    }

    from_count = 0
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        upper = line.upper()
        if upper.startswith("FROM "):
            from_count += 1
            parts = line.split()
            if len(parts) >= 2:
                result["base_image"] = parts[1]
        elif upper.startswith("EXPOSE "):
            ports = re.findall(r"\d+", line)
            result["exposed_ports"].extend([int(p) for p in ports])
        elif upper.startswith("HEALTHCHECK "):
            result["has_healthcheck"] = True

    result["is_multistage"] = from_count > 1
    result["exposed_ports"] = sorted(list(set(result["exposed_ports"])))
    return result


def scan_directory(project_path: str) -> Dict[str, Any]:
    """Recursively scan a project directory and extract deep operational metadata."""
    project_path = os.path.abspath(project_path)
    if not os.path.exists(project_path):
        raise FileNotFoundError(f"Project directory '{project_path}' does not exist.")

    languages_loc: Dict[str, int] = {}
    languages_file_count: Dict[str, int] = {}
    discovered_files: List[str] = []
    
    all_packages: List[str] = []
    routes_found: List[Dict[str, str]] = []
    env_vars_found: Set[str] = set()
    dockerfile_info: Dict[str, Any] = {"has_dockerfile": False}
    has_docker_compose = False
    
    # Walk directory
    for root, dirs, files in os.walk(project_path):
        # Exclude blacklisted directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]

        for fname in files:
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, project_path).replace("\\", "/")
            discovered_files.append(rel_path)

            ext = os.path.splitext(fname)[1].lower()
            
            # Check language
            if ext in EXTENSION_LANGUAGE_MAP:
                lang = EXTENSION_LANGUAGE_MAP[ext]
                languages_file_count[lang] = languages_file_count.get(lang, 0) + 1
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = sum(1 for _ in f)
                        languages_loc[lang] = languages_loc.get(lang, 0) + lines
                except Exception:
                    pass

            # Inspect dependency manifests
            if fname.lower() == "requirements.txt":
                content = safe_read(full_path)
                all_packages.extend(parse_requirements_txt(content))
            elif fname.lower() == "package.json":
                content = safe_read(full_path)
                p_info = parse_package_json(content)
                all_packages.extend(p_info["all_packages"])
            elif fname.lower() == "pom.xml":
                content = safe_read(full_path)
                all_packages.extend(parse_pom_xml(content))

            # Inspect Docker files
            if fname.lower() == "dockerfile" or fname.lower().startswith("dockerfile."):
                dockerfile_info = parse_dockerfile(safe_read(full_path))
            if "docker-compose" in fname.lower() and (fname.endswith(".yml") or fname.endswith(".yaml")):
                has_docker_compose = True

            # Route & Environment Variable scanning on code files
            if ext in {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go"}:
                content = safe_read(full_path)
                # Env vars
                for pattern in ENV_VAR_PATTERNS:
                    matches = pattern.findall(content)
                    for m in matches:
                        if isinstance(m, str) and len(m) > 1 and not m.isdigit():
                            env_vars_found.add(m)

                # Serverless handlers
                for pattern in SERVERLESS_PATTERNS:
                    for match in pattern.finditer(content):
                        fn_name = match.group(1)
                        routes_found.append({"method": "EVENT", "path": f"/{fn_name}", "file": rel_path})

                # Routes
                for pattern in ROUTE_PATTERNS:
                    for match in pattern.finditer(content):
                        groups = match.groups()
                        if len(groups) == 3:
                            # prefix, method, path
                            routes_found.append({"method": groups[1].upper(), "path": groups[2], "file": rel_path})
                        elif len(groups) == 2:
                            # method or annotation, path
                            routes_found.append({"method": groups[0].upper(), "path": groups[1], "file": rel_path})

    # Determine primary language
    primary_language = "Unknown"
    if languages_loc:
        primary_language = max(languages_loc, key=languages_loc.get)
    elif languages_file_count:
        primary_language = max(languages_file_count, key=languages_file_count.get)

    # Analyze dependencies
    deps_analysis = analyze_dependencies(all_packages, primary_language)

    # Determine primary framework
    primary_framework = "None"
    if deps_analysis["detected_frameworks"]:
        primary_framework = deps_analysis["detected_frameworks"][0]
    else:
        # Fallback inspection of code content / paths
        if primary_language == "Python":
            if any("fastapi" in f for f in discovered_files) or any("fastapi" in r.get("path", "") for r in routes_found):
                primary_framework = "FastAPI"
            elif any("flask" in f for f in discovered_files):
                primary_framework = "Flask"
        elif primary_language in ("JavaScript", "TypeScript"):
            if any("express" in f for f in discovered_files):
                primary_framework = "Express"

    # Identify primary database
    primary_database = "None"
    if deps_analysis["relational_db"]:
        # Check specific dialect
        if any("postgr" in d for d in deps_analysis["relational_db"]):
            primary_database = "PostgreSQL"
        elif any("mysql" in d for d in deps_analysis["relational_db"]):
            primary_database = "MySQL"
        else:
            primary_database = "PostgreSQL" # standard relational
    elif deps_analysis["nosql_db"]:
        if any("mongo" in d for d in deps_analysis["nosql_db"]):
            primary_database = "MongoDB"
        elif any("dynamo" in d for d in deps_analysis["nosql_db"]):
            primary_database = "DynamoDB"
        elif any("firestore" in d for d in deps_analysis["nosql_db"]):
            primary_database = "Firestore"
        else:
            primary_database = "MongoDB"

    has_cache = len(deps_analysis["cache"]) > 0
    has_queue = len(deps_analysis["message_queue"]) > 0
    route_count = len(routes_found)
    has_api = route_count > 0 or primary_framework in {"FastAPI", "Flask", "Express", "Spring Boot", "NestJS", "Gin"}

    # Ports
    detected_port = 8080
    if dockerfile_info.get("exposed_ports"):
        detected_port = dockerfile_info["exposed_ports"][0]
    elif primary_framework == "FastAPI":
        detected_port = 8000
    elif primary_framework == "Express":
        detected_port = 3000
    elif primary_framework == "Spring Boot":
        detected_port = 8080
    elif primary_framework == "Flask":
        detected_port = 5000

    total_loc = sum(languages_loc.values())
    total_files = len(discovered_files)

    return {
        "project_path": project_path,
        "primary_language": primary_language,
        "primary_framework": primary_framework,
        "primary_database": primary_database,
        "has_cache": has_cache,
        "cache_type": "Redis" if has_cache else "None",
        "has_queue": has_queue,
        "is_containerized": dockerfile_info["has_dockerfile"],
        "dockerfile_info": dockerfile_info,
        "has_docker_compose": has_docker_compose,
        "has_api": has_api,
        "route_count": route_count,
        "routes": routes_found[:25], # sample top routes
        "total_loc": total_loc,
        "total_files": total_files,
        "languages_loc": languages_loc,
        "languages_file_count": languages_file_count,
        "detected_port": detected_port,
        "env_vars": sorted(list(env_vars_found)),
        "dependencies": deps_analysis,
    }
