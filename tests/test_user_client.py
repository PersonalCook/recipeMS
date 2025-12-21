import importlib

import httpx
import pytest
import respx
from fastapi import HTTPException


def load_user_client(monkeypatch):
    monkeypatch.setenv("USER_SERVICE_URL", "http://user_service:8000")
    user_client = importlib.import_module("app.services.user_client")
    return importlib.reload(user_client)


@respx.mock
@pytest.mark.asyncio
async def test_get_user_id_by_username_success(monkeypatch):
    user_client = load_user_client(monkeypatch)
    respx.get("http://user_service:8000/users/by-username/alice").mock(
        return_value=httpx.Response(200, json={"user_id": 5})
    )

    user_id = await user_client.get_user_id_by_username("alice")

    assert user_id == 5


@respx.mock
@pytest.mark.asyncio
async def test_get_user_id_by_username_not_found(monkeypatch):
    user_client = load_user_client(monkeypatch)
    respx.get("http://user_service:8000/users/by-username/missing").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(HTTPException) as exc:
        await user_client.get_user_id_by_username("missing")

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"


@respx.mock
@pytest.mark.asyncio
async def test_get_user_id_by_username_bad_response(monkeypatch):
    user_client = load_user_client(monkeypatch)
    respx.get("http://user_service:8000/users/by-username/broken").mock(
        return_value=httpx.Response(500)
    )

    with pytest.raises(HTTPException) as exc:
        await user_client.get_user_id_by_username("broken")

    assert exc.value.status_code == 502
    assert exc.value.detail == "Failed to resolve user"


@respx.mock
@pytest.mark.asyncio
async def test_get_user_id_by_username_unavailable(monkeypatch):
    user_client = load_user_client(monkeypatch)
    respx.get("http://user_service:8000/users/by-username/down").mock(
        side_effect=httpx.ConnectError("down")
    )

    with pytest.raises(HTTPException) as exc:
        await user_client.get_user_id_by_username("down")

    assert exc.value.status_code == 502
    assert "user-service unavailable" in exc.value.detail
