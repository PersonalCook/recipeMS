import os
import httpx
from fastapi import HTTPException


API_URL = "https://api.api-ninjas.com/v1/nutrition"
API_KEY = os.getenv("NINJAS_NUTRITION_API_KEY")

async def fetch_nutrition(query: str):
    if not API_KEY:
        raise RuntimeError("NINJAS_NUTRITION_API_KEY not configured")
    headers = {"X-Api-Key": API_KEY}
    params = {"query": query}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(API_URL, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()