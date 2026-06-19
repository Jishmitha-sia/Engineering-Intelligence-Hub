"""Unit tests for security utilities."""

import pytest
from datetime import timedelta

from core.security import (
    create_access_token,
    verify_token,
    hash_password,
    verify_password,
    is_valid_password,
)


@pytest.mark.unit
@pytest.mark.auth
class TestSecurity:
    def test_password_hash_and_verify(self):
        password = "SecurePass123!"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("WrongPass123!", hashed)

    def test_password_validation(self):
        valid, errors = is_valid_password("SecurePass123!")
        assert valid
        assert errors == []

        valid, errors = is_valid_password("short")
        assert not valid
        assert len(errors) > 0

    def test_jwt_token_round_trip(self):
        token = create_access_token(subject=42, expires_delta=timedelta(minutes=30))
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["type"] == "access"

    def test_invalid_token_returns_none(self):
        assert verify_token("invalid.token.value") is None
