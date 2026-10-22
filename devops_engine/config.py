"""Configuration module for DevOps Engine.
Loads environment variables from .env file and provides platform-wide settings.
"""

import os
# Enforce 100% offline local embeddings (no unauthenticated HF hub calls)
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
from pathlib import Path


def load_env(env_path: str = None) -> bool:
    """Zero-dependency .env loader that populates os.environ without requiring external packages.
    
    Searches in:
    1. Explicit env_path (if provided)
    2. Current working directory (.env)
    3. devops_engine directory (.env)
    4. Project root directory (../.env)
    """
    search_paths = []
    if env_path:
        search_paths.append(Path(env_path))
    else:
        cwd = Path.cwd()
        here = Path(__file__).resolve().parent
        search_paths.extend([
            cwd / ".env",
            here / ".env",
            here.parent / ".env",
        ])

    loaded = False
    for p in search_paths:
        if p.is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, val = line.split("=", 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            if key and key not in os.environ:
                                os.environ[key] = val
                                loaded = True
                if loaded:
                    break
            except Exception:
                pass
    return loaded


# Automatically load environment variables on import
load_env()

# Google Cloud & Gemini Configuration
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "mcp-test-sreenivas")
GOOGLE_CLOUD_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
GEMINI_MODEL = "gemini-2.5-flash"

# AWS Configuration
AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
