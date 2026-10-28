import os
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-secret-key-0123456789abcdef0123456789abcdef")
os.environ.setdefault("DB_URL", "sqlite://")

DATASET = Path(os.environ.get("DATASET_PATH", "data/survey_results_public_2025.xlsx"))
