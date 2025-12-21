import importlib
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile


def load_storage_module(monkeypatch, media_root: Path):
    monkeypatch.setenv("MEDIA_ROOT", str(media_root))
    storage = importlib.import_module("app.utils.storage")
    return importlib.reload(storage)


@pytest.mark.asyncio
async def test_save_image_creates_file(monkeypatch, tmp_path):
    storage = load_storage_module(monkeypatch, tmp_path)
    upload = UploadFile(filename="photo.PNG", file=BytesIO(b"image-bytes"))

    result = await storage.save_image(upload)

    assert result.startswith("/media/")
    filename = result.replace("/media/", "")
    saved_path = tmp_path / filename
    assert saved_path.exists()
    assert saved_path.suffix == ".png"
