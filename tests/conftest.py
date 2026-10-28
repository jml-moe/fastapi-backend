import os
import tempfile
from pathlib import Path

# Harus diset sebelum app diimpor (engine dan settings dibuat saat impor).
os.environ["SECRET_KEY"] = "test-secret-key-0123456789abcdef0123456789abcdef"
os.environ["DB_URL"] = f"sqlite:///{Path(tempfile.mkdtemp()) / 'test.db'}"
os.environ["ADMIN_EMAIL"] = "admin@test.local"
os.environ["ADMIN_PASSWORD"] = "admin-test-123"

DATASET = Path(os.environ.get("DATASET_PATH", "data/survey_results_public_2025.xlsx"))
