# recipeMS

Recipe service for PersonalCook.

This microservice manages recipes for PersonalCook.
It exposes a REST API for creating, updating, searching and retrieving recipes. It also provides nutritional infomation via API Ninjas (https://api-ninjas.com).

## Overview
RecipeMS manages recipe CRUD, media uploads, and nutrition analysis. It stores recipe data in PostgreSQL, indexes recipes in Elasticsearch for search, and uses API Ninjas for nutrition summaries.

## Architecture
- FastAPI service with PostgreSQL persistence.
- Elasticsearch index for recipe search.
- External nutrition API integration.
- File-based media storage for recipe images.

## Local dev

1. docker network create personalcook-net
2. copy .env.example .env
3. docker compose up --build

## Configuration
Environment variables (see `.env.example`):
- `DATABASE_URL`: Postgres connection string.
- `JWT_SECRET`, `JWT_ALGORITHM`: JWT validation for protected endpoints.
- `USER_SERVICE_URL`: user service base URL.
- `ELASTICSEARCH_HOST`: Elasticsearch base URL.
- `NINJAS_NUTRITION_API_KEY`: API Ninjas key for nutrition endpoint.

## Dependencies

- user service at USER_SERVICE_URL (default http://user_service:8000)
- Elasticsearch at ELASTICSEARCH_HOST (default http://elasticsearch:9200)

## Ports

- API: 8001
- Postgres: 5433

## API Docs
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI JSON: http://localhost:8001/openapi.json

## Testing
Run tests locally:
```
pytest
```

## CI
This repo runs two GitHub Actions jobs:
- `test`: installs requirements and runs `pytest`
- `container`: builds the Docker image, runs the container, and hits `/` for a smoke test

Tests (files and intent):
- `tests/test_auth.py`: JWT decode and auth helper behavior (valid, expired, invalid tokens).
- `tests/test_recipes_router.py`: recipes CRUD and filters, including validation of bad ingredients.
- `tests/test_storage.py`: image upload storage writes and filename normalization.
- `tests/test_user_client.py`: user-service client responses and error handling via mocked HTTP.

## Deployment
- Docker image and Helm chart are provided for deployment.
- Health check: `GET /health`.
- Metrics: `GET /metrics` (Prometheus format).
- Media files are served from `/media`.

## Troubleshooting
- `NINJAS_NUTRITION_API_KEY` missing: `/nutrition` requests will fail.
- Elasticsearch connection errors: verify `ELASTICSEARCH_HOST` and ES container status.
- JWT errors: verify `JWT_SECRET` and `JWT_ALGORITHM`.
