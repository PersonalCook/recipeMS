from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .routers import recipes
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recipe Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(recipes.router)
app.mount("/media", StaticFiles(directory="media"), name="media")

@app.get("/")
def root():
    return {"message": "Recipe Service running in Docker!"}

#uvicorn app.main:app --reload
#http://localhost:8080/docs
