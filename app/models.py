from sqlalchemy import Column, Integer, String, Text, Time, TIMESTAMP, Enum as SQLEnum, Float, ForeignKey
from .database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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

class Recipe(Base):
    __tablename__ = "recipes"

    recipe_id = Column(Integer, primary_key=True, index=True)
    recipe_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, nullable=False)
    cooking_time = Column(Time, nullable=False)
    total_time = Column(Time, nullable=False)
    servings = Column(Integer, nullable=False)
    instructions = Column(Text, nullable=False)
    keywords = Column(String, nullable=True)
    img = Column(String, nullable=False)
    visibility = Column(SQLEnum(VisibilityEnum), default=VisibilityEnum.PUBLIC, nullable=False)
    category = Column(SQLEnum(CategoryEnum), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")

class Ingredient(Base):
    __tablename__ = "ingredients"

    ingredient_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    uses = relationship("RecipeIngredient", back_populates="ingredient")

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.recipe_id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.ingredient_id"), nullable=False)
    amount = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="uses")
