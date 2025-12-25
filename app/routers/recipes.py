import json
from datetime import time
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import ValidationError
from ..database import SessionLocal
from .. import schemas
from .. import crud
from .. import models
from ..elastic import client
from ..utils.auth import get_current_user_id
from ..services.user_client import get_user_id_by_username
from ..utils.storage import save_image
from ..metrics import num_created_recipes

router = APIRouter(prefix="/recipes", tags=["Recipes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#adding and updating recipe to elasticsearch
async def index_recipe(recipe):
    await client.index(
        index="recipes",
        id=recipe["recipe_id"],
        document={
            "recipe_name": recipe["recipe_name"],
            "recipe_id": recipe["recipe_id"],
            "user_id": recipe["user_id"],
            "description": recipe["description"],
            "ingredients": [r["name"] for r in recipe["ingredients"]],
            "cooking_time": recipe["cooking_time"].strftime("%H:%M:%S"),
            "total_time": recipe["total_time"].strftime("%H:%M:%S"),
            "keywords": recipe["keywords"],
            "category": recipe["category"].value,
            "visibility": recipe["visibility"].value,
            "created_at": recipe["created_at"].isoformat(),
        }
    )

async def update_recipe_es(recipe):
    await client.update(
        index="recipes",
        id=recipe["recipe_id"],
        doc={
            "recipe_name": recipe["recipe_name"],
            "recipe_id": recipe["recipe_id"],
            "user_id": recipe["user_id"],
            "description": recipe["description"],
            "ingredients": [r["name"] for r in recipe["ingredients"]],
            "cooking_time": recipe["cooking_time"].strftime("%H:%M:%S"),
            "total_time": recipe["total_time"].strftime("%H:%M:%S"),
            "keywords": recipe["keywords"],
            "category": recipe["category"].value,
            "visibility": recipe["visibility"].value,
            "created_at": recipe["created_at"].isoformat(),
        }
    )
#deleting recipe from elasticsearch
async def delete_recipe_es(recipe_id):
    await client.delete(
        index="recipes",
        id=recipe_id,
        ignore=[404]
    )

@router.get("/", response_model=list[schemas.Recipe])
def read_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    recipes = crud.get_recipes(db, skip=skip, limit=limit)
    return recipes 


@router.get("/{recipe_id}", response_model=schemas.Recipe)
def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = crud.get_recipe(db, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe  



@router.post("/", response_model=schemas.Recipe, status_code=201)
async def create_recipe(
    recipe_name: str = Form(...),
    description: str | None = Form(None),
    cooking_time: time = Form(...),
    total_time: time = Form(...),
    servings: int = Form(...),
    ingredients: str = Form(..., description="JSON array of ingredients"),
    instructions: str = Form(...),
    keywords: str | None = Form(None),
    visibility: schemas.VisibilityEnum = Form(schemas.VisibilityEnum.PUBLIC),
    category: schemas.CategoryEnum = Form(...),
    image: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    try:
        ingredients_payload = json.loads(ingredients)
        ingredient_items = [schemas.IngredientCreate(**ing) for ing in ingredients_payload]
    except (json.JSONDecodeError, TypeError, ValidationError):
        raise HTTPException(status_code=400, detail="Invalid ingredients format")

    if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    image_path = await save_image(image)

    recipe = schemas.RecipeCreate(
        recipe_name=recipe_name,
        description=description,
        cooking_time=cooking_time,
        total_time=total_time,
        servings=servings,
        ingredients=ingredient_items,
        instructions=instructions,
        keywords=keywords,
        img=image_path,
        visibility=visibility,
        category=category,
    )

    num_created_recipes.labels(source="api").inc()
    created_recipe = crud.create_recipe(db=db, recipe=recipe, user_id=user_id)
    await index_recipe(created_recipe)
    return created_recipe


@router.put("/{recipe_id}", response_model=schemas.Recipe)
async def update_recipe(
    recipe_id: int,
    recipe_name: str | None = Form(None),
    description: str | None = Form(None),
    cooking_time: time | None = Form(None),
    total_time: time | None = Form(None),
    servings: int | None = Form(None),
    instructions: str | None = Form(None),
    keywords: str | None = Form(None),
    visibility: schemas.VisibilityEnum | None = Form(None),
    category: schemas.CategoryEnum | None = Form(None),
    image: UploadFile | None = File(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    recipe_raw = db.query(models.Recipe).filter(models.Recipe.recipe_id == recipe_id).first()

    if not recipe_raw:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if recipe_raw.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own recipes")

    update_data = {}
    if recipe_name is not None:
        update_data["recipe_name"] = recipe_name
    if description is not None:
        update_data["description"] = description
    if cooking_time is not None:
        update_data["cooking_time"] = cooking_time
    if total_time is not None:
        update_data["total_time"] = total_time
    if servings is not None:
        update_data["servings"] = servings
    if instructions is not None:
        update_data["instructions"] = instructions
    if keywords is not None:
        update_data["keywords"] = keywords
    if visibility is not None:
        update_data["visibility"] = visibility
    if category is not None:
        update_data["category"] = category

    if image is not None:
        if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise HTTPException(status_code=400, detail="Unsupported image type")
        update_data["img"] = await save_image(image)

    updates = schemas.RecipeUpdate(**update_data)

    updated = crud.update_recipe(db, recipe_id, updates)
    await update_recipe_es(updated)
    return updated


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    recipe = db.query(models.Recipe).filter(models.Recipe.recipe_id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this recipe")

    deleted = crud.delete_recipe(db, recipe_id=recipe_id)
    if deleted:
        await delete_recipe_es(recipe_id)
    return None

@router.get("/user/{user_id}", response_model=list[schemas.Recipe])
def get_recipes_created_by_user(user_id: int, db: Session = Depends(get_db)):
    recipes = crud.get_recipes_by_user(db, user_id=user_id)
    return recipes


@router.get("/by-username/{username}", response_model=list[schemas.Recipe])
async def get_recipes_created_by_username(username: str, db: Session = Depends(get_db)):
    user_id = await get_user_id_by_username(username)
    recipes = crud.get_recipes_by_user(db, user_id=user_id)
    return recipes
