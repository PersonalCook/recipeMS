from sqlalchemy.orm import Session
from . import models, schemas
from typing import Optional


# -----------------------------------------
# Helper: serialize SQLAlchemy Recipe → Pydantic-friendly dict
# -----------------------------------------

def serialize_recipe(recipe: models.Recipe):
    return {
        "recipe_id": recipe.recipe_id,
        "recipe_name": recipe.recipe_name,
        "description": recipe.description,
        "cooking_time": recipe.cooking_time,
        "total_time": recipe.total_time,
        "servings": recipe.servings,
        "instructions": recipe.instructions,
        "keywords": recipe.keywords,
        "img": recipe.img,
        "visibility": recipe.visibility,
        "category": recipe.category,
        "created_at": recipe.created_at,
        "user_id": recipe.user_id,

        "ingredients": [
            {
                "name": ri.ingredient.name,
                "amount": ri.amount,
                "unit": ri.unit,
            }
            for ri in recipe.ingredients
        ]
    }




def get_recipe(db: Session, recipe_id: int) -> Optional[dict]:
    recipe = db.query(models.Recipe).filter(models.Recipe.recipe_id == recipe_id).first()
    return serialize_recipe(recipe) if recipe else None


def get_recipes(db: Session, skip: int = 0, limit: int = 100):
    recipes = (
        db.query(models.Recipe)
        .order_by(models.Recipe.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [serialize_recipe(r) for r in recipes]


def create_recipe(db: Session, recipe: schemas.RecipeCreate, user_id: int) -> dict:
    db_recipe = models.Recipe(
        recipe_name=recipe.recipe_name,
        description=recipe.description,
        cooking_time=recipe.cooking_time,
        total_time=recipe.total_time,
        servings=recipe.servings,
        instructions=recipe.instructions,
        keywords=recipe.keywords,
        img=recipe.img,
        visibility=recipe.visibility,
        category=recipe.category, 
        user_id=user_id
    )

    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

    for ing in recipe.ingredients:
        db_ing = db.query(models.Ingredient).filter_by(name=ing.name).first()

        if not db_ing:
            db_ing = models.Ingredient(name=ing.name)
            db.add(db_ing)
            db.commit()
            db.refresh(db_ing)

        rec_ing = models.RecipeIngredient(
            recipe_id=db_recipe.recipe_id,
            ingredient_id=db_ing.ingredient_id,
            amount=ing.amount,
            unit=ing.unit
        )
        db.add(rec_ing)

    db.commit()
    db.refresh(db_recipe)

    return serialize_recipe(db_recipe)


def update_recipe(db: Session, recipe_id: int, updates: schemas.RecipeUpdate):
    db_recipe = db.query(models.Recipe).filter(models.Recipe.recipe_id == recipe_id).first()

    if not db_recipe:
        return None

    update_data = updates.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_recipe, field, value)

    db.commit()
    db.refresh(db_recipe)
    return serialize_recipe(db_recipe)


def delete_recipe(db: Session, recipe_id: int):
    db_recipe = db.query(models.Recipe).filter(models.Recipe.recipe_id == recipe_id).first()

    if not db_recipe:
        return None

    db.delete(db_recipe)
    db.commit()
    return True

def get_recipes_by_user(db: Session, user_id: int):
    recipes = (
        db.query(models.Recipe)
        .filter(models.Recipe.user_id == user_id)
        .order_by(models.Recipe.created_at.desc())
        .all()
    )
    return [serialize_recipe(r) for r in recipes]