"""Dependency and Manifest Parser for Multi-Language Repositories.
Parses requirements.txt, package.json, pom.xml, and go.mod to extract libraries and categorize services.
"""

import os
import re
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Set, Any


# Known service category signatures
DB_RELATIONAL_PACKAGES = {
    # Python
    "psycopg2", "psycopg2-binary", "asyncpg", "mysqlclient", "mysql-connector-python",
    "sqlalchemy", "tortoise-orm", "peewee", "aiomysql", "databases", "dj-database-url",
    # Node.js
    "pg", "pg-hstore", "mysql", "mysql2", "sequelize", "typeorm", "prisma", "@prisma/client", "knex",
    # Java
    "postgresql", "mysql-connector-java", "spring-boot-starter-data-jpa", "hibernate-core", "h2"
}

DB_NOSQL_PACKAGES = {
    # Python
    "pymongo", "motor", "mongoengine", "cassandra-driver", "dynamodb", "google-cloud-firestore",
    # Node.js
    "mongodb", "mongoose", "dynamoose", "@aws-sdk/client-dynamodb", "@google-cloud/firestore",
    # Java
    "spring-boot-starter-data-mongodb", "mongodb-driver-sync", "aws-java-sdk-dynamodb"
}

CACHE_PACKAGES = {
    # Python
    "redis", "aioredis", "walrus", "pymemcache", "python-memcached",
    # Node.js
    "redis", "ioredis", "memcached",
    # Java
    "spring-boot-starter-data-redis", "jedis", "lettuce-core"
}

QUEUE_PACKAGES = {
    # Python
    "celery", "pika", "rq", "kafka-python", "confluent-kafka", "aio-pika",
    # Node.js
    "amqplib", "bull", "kafkajs", "rsmq",
    # Java
    "spring-kafka", "spring-rabbit", "amqp-client", "kafka-clients"
}

FRAMEWORK_SIGNATURES = {
    "python": {
        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django",
        "tornado": "Tornado",
        "sanic": "Sanic",
        "streamlit": "Streamlit",
        "celery": "Celery Worker"
    },
    "javascript": {
        "express": "Express",
        "nestjs": "NestJS",
        "@nestjs/core": "NestJS",
        "next": "Next.js",
        "koa": "Koa",
        "fastify": "Fastify",
        "socket.io": "Socket.io Server"
    },
    "java": {
        "spring-boot": "Spring Boot",
        "spring-web": "Spring MVC",
        "quarkus": "Quarkus",
        "micronaut": "Micronaut"
    }
}


def parse_requirements_txt(content: str) -> List[str]:
    """Parse Python requirements.txt file."""
    packages = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-r") or line.startswith("-i"):
            continue
        # Strip version specifiers like ==, >=, <=, ~=, <, >
        pkg = re.split(r"[><=~;]", line)[0].strip().lower()
        if pkg:
            packages.append(pkg)
    return packages


def parse_package_json(content: str) -> Dict[str, Any]:
    """Parse Node.js package.json file."""
    try:
        data = json.loads(content)
        deps = list(data.get("dependencies", {}).keys())
        dev_deps = list(data.get("devDependencies", {}).keys())
        scripts = data.get("scripts", {})
        main_file = data.get("main", "")
        return {
            "dependencies": deps,
            "devDependencies": dev_deps,
            "scripts": scripts,
            "main": main_file,
            "all_packages": [d.lower() for d in deps + dev_deps]
        }
    except Exception:
        return {"dependencies": [], "devDependencies": [], "scripts": {}, "main": "", "all_packages": []}


def parse_pom_xml(content: str) -> List[str]:
    """Parse Java Maven pom.xml file."""
    packages = []
    try:
        root = ET.fromstring(content)
        # Handle XML namespace
        ns = {"m": "http://maven.apache.org/POM/4.0.0"}
        deps = root.findall(".//m:dependency", ns) or root.findall(".//dependency")
        for dep in deps:
            artifact_id = dep.find("m:artifactId", ns) if ns else None
            if artifact_id is None:
                artifact_id = dep.find("artifactId")
            if artifact_id is not None and artifact_id.text:
                packages.append(artifact_id.text.strip().lower())
    except Exception:
        # Fallback regex parsing
        artifacts = re.findall(r"<artifactId>([^<]+)</artifactId>", content, re.IGNORECASE)
        packages = [a.strip().lower() for a in artifacts if a.strip().lower() != "pom"]
    return packages


def analyze_dependencies(package_list: List[str], lang_hint: str = "") -> Dict[str, Any]:
    """Categorize a list of discovered package names."""
    detected = {
        "relational_db": [],
        "nosql_db": [],
        "cache": [],
        "message_queue": [],
        "detected_frameworks": [],
        "all_dependencies": package_list
    }

    pkg_set = set(p.lower() for p in package_list)

    for pkg in pkg_set:
        for r_pkg in DB_RELATIONAL_PACKAGES:
            if r_pkg in pkg:
                detected["relational_db"].append(pkg)
                break
        for n_pkg in DB_NOSQL_PACKAGES:
            if n_pkg in pkg:
                detected["nosql_db"].append(pkg)
                break
        for c_pkg in CACHE_PACKAGES:
            if c_pkg in pkg:
                detected["cache"].append(pkg)
                break
        for q_pkg in QUEUE_PACKAGES:
            if q_pkg in pkg:
                detected["message_queue"].append(pkg)
                break

    # Framework identification
    lang_key = lang_hint.lower() if lang_hint else ""
    framework_dicts = FRAMEWORK_SIGNATURES.get(lang_key, {})
    if not framework_dicts:
        # Search all
        for l_dict in FRAMEWORK_SIGNATURES.values():
            for key, name in l_dict.items():
                if any(key in p for p in pkg_set):
                    detected["detected_frameworks"].append(name)
    else:
        for key, name in framework_dicts.items():
            if any(key in p for p in pkg_set):
                detected["detected_frameworks"].append(name)

    # Deduplicate
    detected["relational_db"] = sorted(list(set(detected["relational_db"])))
    detected["nosql_db"] = sorted(list(set(detected["nosql_db"])))
    detected["cache"] = sorted(list(set(detected["cache"])))
    detected["message_queue"] = sorted(list(set(detected["message_queue"])))
    detected["detected_frameworks"] = sorted(list(set(detected["detected_frameworks"])))

    return detected
