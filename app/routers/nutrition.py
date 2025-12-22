from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.nutrition_client import fetch_nutrition
from ..metrics import num_nutrition_analyses

router = APIRouter(prefix="/nutrition", tags=["nutrition"])

class Ingredient(BaseModel):
    name: str
    amount: float
    unit: str

class NutritionSummaryRequest(BaseModel):
    ingredients: List[Ingredient]

nutrition_data = [
    "fat_total_g",
    "fat_saturated_g",
    "sodium_mg",
    "potassium_mg",
    "cholesterol_mg",
    "carbohydrates_total_g",
    "fiber_g",
    "sugar_g",
]

def convert_to_num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

@router.post("")
async def get_nutrition_summary(data: NutritionSummaryRequest, servings: int):
    status = "success"
    try:
        items = []

        for ingredient in data.ingredients:
            query = f"{ingredient.amount}{(' ' + ingredient.unit) if ingredient.unit else ''} {ingredient.name}"
            res = await fetch_nutrition(query)
            items.extend(res)

        total_weight_g = 0.0
        totals = {field: 0.0 for field in nutrition_data}

        for item in items:
            weight = convert_to_num(item.get("serving_size_g"))
            total_weight_g += weight
            for field in nutrition_data:
                totals[field] += convert_to_num(item.get(field))

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
        status = "error"
        raise HTTPException(status_code=502, detail=str(e))
    
    finally:
        num_nutrition_analyses.labels(source="external_api", status=status).inc()