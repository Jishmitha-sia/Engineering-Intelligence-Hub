"""Unit test path setup."""

import os
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2] / "app"
sys.path.insert(0, str(APP_ROOT))

os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-secret-key-for-testing-only-not-production-safe",
)
