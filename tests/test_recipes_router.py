import importlib
import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


class DummyESClient:
    async def index(self, **kwargs):
        return None

    async def update(self, **kwargs):
        return None

    async def delete(self, **kwargs):
        return None


@pytest.fixture()
def test_client(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "test.db"
    media_root = tmp_path / "media"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("MEDIA_ROOT", str(media_root))

    database = importlib.reload(importlib.import_module("app.database"))
    models = importlib.reload(importlib.import_module("app.models"))
    importlib.reload(importlib.import_module("app.crud"))
    recipes = importlib.reload(importlib.import_module("app.routers.recipes"))

    models.Base.metadata.create_all(bind=database.engine)

    recipes.client = DummyESClient()

    async def fake_get_user_id_by_username(username: str) -> int:
        return 1

    recipes.get_user_id_by_username = fake_get_user_id_by_username

    def override_get_db():
        db = database.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(recipes.router)
    app.dependency_overrides[recipes.get_db] = override_get_db
    app.dependency_overrides[recipes.get_current_user_id] = lambda: 1

    return TestClient(app), recipes


def _create_recipe_payload(name: str = "Test Recipe"):
    ingredients = [{"name": "flour", "amount": 1.5, "unit": "cup"}]
    data = {
        "recipe_name": name,
        "description": "desc",
        "cooking_time": "00:10:00",
        "total_time": "00:20:00",
        "servings": "2",
        "ingredients": json.dumps(ingredients),
        "instructions": "mix",
        "keywords": "quick",
        "visibility": "public",
        "category": "breakfast",
    }
    files = {"image": ("photo.png", b"image-bytes", "image/png")}
    return data, files


def test_create_and_get_recipe(test_client):
    client, _ = test_client
    data, files = _create_recipe_payload()

    created = client.post("/recipes/", data=data, files=files)
    assert created.status_code == 201
    recipe = created.json()

    fetched = client.get(f"/recipes/{recipe['recipe_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["recipe_name"] == "Test Recipe"


def test_list_and_filter_recipes(test_client):
    client, _ = test_client
    data, files = _create_recipe_payload(name="First")
    client.post("/recipes/", data=data, files=files)
    data, files = _create_recipe_payload(name="Second")
    client.post("/recipes/", data=data, files=files)

    listed = client.get("/recipes/")
    assert listed.status_code == 200
    assert len(listed.json()) >= 2

    by_user = client.get("/recipes/user/1")
    assert by_user.status_code == 200
    assert len(by_user.json()) >= 2

    by_username = client.get("/recipes/by-username/alice")
    assert by_username.status_code == 200
    assert len(by_username.json()) >= 2


def test_update_recipe(test_client):
    client, _ = test_client
    data, files = _create_recipe_payload()
    created = client.post("/recipes/", data=data, files=files).json()

    updated = client.put(
        f"/recipes/{created['recipe_id']}",
        data={"recipe_name": "Updated", "servings": "4"},
    )
    assert updated.status_code == 200
    assert updated.json()["recipe_name"] == "Updated"
    assert updated.json()["servings"] == 4


def test_update_forbidden_for_other_user(test_client):
    client, recipes = test_client
    data, files = _create_recipe_payload()
    created = client.post("/recipes/", data=data, files=files).json()

    client.app.dependency_overrides[recipes.get_current_user_id] = lambda: 999
    forbidden = client.put(
        f"/recipes/{created['recipe_id']}",
        data={"recipe_name": "Nope"},
    )
    assert forbidden.status_code == 403


def test_delete_recipe(test_client):
    client, _ = test_client
    data, files = _create_recipe_payload()
    created = client.post("/recipes/", data=data, files=files).json()

    deleted = client.delete(f"/recipes/{created['recipe_id']}")
    assert deleted.status_code == 204

    missing = client.get(f"/recipes/{created['recipe_id']}")
    assert missing.status_code == 404


def test_create_recipe_invalid_ingredients(test_client):
    client, _ = test_client
    data, files = _create_recipe_payload()
    data["ingredients"] = "not-json"

    response = client.post("/recipes/", data=data, files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid ingredients format"
