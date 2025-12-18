import os
import uuid
import shutil
from fastapi import UploadFile

MEDIA_ROOT = os.getenv("MEDIA_ROOT", "media")


async def save_image(upload: UploadFile) -> str:
    """
    Persist an uploaded image to MEDIA_ROOT and return the public path.
    """
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    _, ext = os.path.splitext(upload.filename)
    filename = f"{uuid.uuid4().hex}{ext.lower()}"
    destination = os.path.join(MEDIA_ROOT, filename)

    with open(destination, "wb") as out_file:
        shutil.copyfileobj(upload.file, out_file)

    return f"/media/{filename}"
