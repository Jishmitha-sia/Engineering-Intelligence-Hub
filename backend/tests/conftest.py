"""Shared pytest fixtures."""

import pytest


@pytest.fixture
def sample_user() -> dict:
    return {
        "email": "testuser@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
    }
