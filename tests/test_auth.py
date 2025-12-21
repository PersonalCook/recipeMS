import importlib
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jwt import InvalidTokenError


def load_auth_module(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    auth = importlib.import_module("app.utils.auth")
    return importlib.reload(auth)


def test_decode_jwt_valid(monkeypatch):
    auth = load_auth_module(monkeypatch)
    token = jwt.encode({"user_id": 42}, "test-secret", algorithm="HS256")

    payload = auth.decode_jwt(token)

    assert payload["user_id"] == 42


def test_decode_jwt_expired(monkeypatch):
    auth = load_auth_module(monkeypatch)
    expired = datetime.now(timezone.utc) - timedelta(seconds=10)
    token = jwt.encode({"user_id": 1, "exp": expired}, "test-secret", algorithm="HS256")

    with pytest.raises(InvalidTokenError) as exc:
        auth.decode_jwt(token)

    assert str(exc.value) == "Token expired"


def test_get_current_user_id_valid(monkeypatch):
    auth = load_auth_module(monkeypatch)
    token = jwt.encode({"user_id": 7}, "test-secret", algorithm="HS256")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    user_id = auth.get_current_user_id(credentials)

    assert user_id == 7


def test_get_current_user_id_invalid(monkeypatch):
    auth = load_auth_module(monkeypatch)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad-token")

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user_id(credentials)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"
