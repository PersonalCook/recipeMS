from fastapi import FastAPI, Request
from .metrics import (
    num_requests,
    num_errors,
    request_latency,
    requests_in_progress,
)
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .routers import recipes
from . import models
from app.utils.storage import MEDIA_ROOT
import os
from .routers import nutrition
from .schemas import RootResponse, HealthResponse

os.makedirs(MEDIA_ROOT, exist_ok=True)
models.Base.metadata.create_all(bind=engine)

API_PREFIX = "/api/recipe"

app = FastAPI(
    title="Recipe Service",
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prefiksiraj API routerje
app.include_router(recipes.router, prefix=API_PREFIX)
app.include_router(nutrition.router, prefix=API_PREFIX)

# Prefiksiraj tudi media
app.mount(f"{API_PREFIX}/media", StaticFiles(directory=MEDIA_ROOT), name="media")

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path

    requests_in_progress.inc()
    start_time = time.time()

    try:
        response = await call_next(request)
        status_code = response.status_code
        duration = time.time() - start_time

        num_requests.labels(method=method, endpoint=endpoint, status_code=status_code).inc()

        if status_code >= 400:
            num_errors.labels(method=method, endpoint=endpoint, status_code=status_code).inc()

        request_latency.labels(method=method, endpoint=endpoint).observe(duration)

        return response
    finally:
        requests_in_progress.dec()

@app.get(
    f"{API_PREFIX}/metrics",
    summary="Prometheus metrics",
    responses={
        200: {"description": "OK", "content": {"text/plain": {"example": "# HELP ..."}}}
    },
)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get(
    f"{API_PREFIX}/",
    response_model=RootResponse,
    summary="Service info",
    responses={
        200: {
            "description": "OK",
            "content": {"application/json": {"example": {"message": "Recipe Service running!"}}},
        }
    },
)
def root():
    return {"message": "Recipe Service running!"}

@app.get(
    f"{API_PREFIX}/health",
    response_model=HealthResponse,
    summary="Health check",
    responses={
        200: {"description": "OK", "content": {"application/json": {"example": {"status": "ok"}}}}
    },
)
def health():
    return {"status": "ok"}
