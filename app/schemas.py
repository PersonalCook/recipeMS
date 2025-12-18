from pydantic import BaseModel
from typing import Optional, List
from datetime import time, datetime
from enum import Enum

class CategoryEnum(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    DESSERT = "dessert"
    SNACK = "snack"

class VisibilityEnum(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    FOLLOWERS_ONLY = "followers_only"

# -------------------------
# Ingredient Schemas
# -------------------------

class IngredientCreate(BaseModel):
    name: str
    amount: float
    unit: str

class IngredientRead(BaseModel):
    name: str
    amount: float
    unit: str

    class Config:
        orm_mode = True


# -------------------------
# Recipe Schemas
# -------------------------

class RecipeBase(BaseModel):
    recipe_name: str
    description: Optional[str] = None
    cooking_time: time
    total_time: time
    servings: int
    ingredients: List[IngredientCreate]
    instructions: str
    keywords: Optional[str] = None
    img: str
    visibility: VisibilityEnum = VisibilityEnum.PUBLIC
    category: CategoryEnum


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    recipe_name: Optional[str] = None
    description: Optional[str] = None
    cooking_time: Optional[time] = None
    total_time: Optional[time] = None
    servings: Optional[int] = None
    instructions: Optional[str] = None
    keywords: Optional[str] = None
    img: Optional[str] = None
    visibility: Optional[VisibilityEnum] = None
    category: Optional[CategoryEnum] = None
    #manjka še da bi lahko sestavine posodobil, malo bolj komplicirano

class Recipe(BaseModel):
    recipe_id: int
    user_id: int
    created_at: datetime
    recipe_name: str
    description: Optional[str]
    cooking_time: time
    total_time: time
    servings: int
    ingredients: List[IngredientRead]
    instructions: str
    keywords: Optional[str]
    img: str
    visibility: VisibilityEnum
    category: CategoryEnum

    class Config:
        orm_mode = True
