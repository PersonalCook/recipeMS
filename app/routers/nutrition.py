from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.nutrition_client import fetch_nutrition

router = APIRouter(prefix="/nutrition", tags=["nutrition"])

class Ingredient(BaseModel):
    name: str
    amount: float
    unit: str

class NutritionSummaryRequest(BaseModel):
    ingredients: List[Ingredient]

NUTRITION_FIELDS = [
    "fat_total_g",
    "fat_saturated_g",
    "sodium_mg",
    "potassium_mg",
    "cholesterol_mg",
    "carbohydrates_total_g",
    "fiber_g",
    "sugar_g",
]

def _to_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

@router.post("")
async def get_nutrition_summary(data: NutritionSummaryRequest, servings: int):
    try:
        items = []

        for ing in data.ingredients:
            single_query = f"{ing.amount}{(' ' + ing.unit) if ing.unit else ''} {ing.name}"
            res = await fetch_nutrition(single_query)
            # api-ninjas vrne listo – jo dodamo v skupni seznam
            items.extend(res)

        total_weight_g = 0.0
        totals = {field: 0.0 for field in NUTRITION_FIELDS}

        for item in items:
            weight = _to_number(item.get("serving_size_g"))
            total_weight_g += weight
            for field in NUTRITION_FIELDS:
                totals[field] += _to_number(item.get(field))

        per_100g = {}
        if total_weight_g > 0:
            factor = 100.0 / total_weight_g
            for field, value in totals.items():
                per_100g[field] = value * factor
        
        per_serving = {}
        if total_weight_g > 0 and servings > 0:
            factor = 1.0 / servings
            for field, value in totals.items():
                per_serving[field] = value * factor

        return {
            "total_weight_g": total_weight_g,
            "totals": totals,
            "per_100g": per_100g,
            "per_serving": per_serving,
            "items": items,
        }

    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))