import os
import httpx
from fastapi import HTTPException


USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8000")


async def get_user_id_by_username(username: str) -> int:
    """Resolve a username to user_id via user-service."""
    url = f"{USER_SERVICE_URL}/users/by-username/{username}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"user-service unavailable: {exc}") from exc

    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to resolve user")

    data = resp.json()
    user_id = data.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=502, detail="Malformed response from user-service")
    return user_id
