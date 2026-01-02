# recipeMS

Recipe service for PersonalCook.

This microservice manages recipes for PersonalCook.
It exposes a REST API for creating, updating, searching and retrieving recipes. It also provides nutritional infomation via API Ninjas (https://api-ninjas.com).

---

## Overview

RecipeMS manages recipe CRUD, media uploads, and nutrition analysis. It stores recipe data in PostgreSQL, indexes recipes in Elasticsearch for search, and uses API Ninjas for nutrition summaries.

---

## Architecture

- **FastAPI** application
- **PostgreSQL** for persistence
- **Elasticsearch** for indexing and search
- **API Ninjas** for nutrition analysis
- **Persistent volume** for recipe media storage
- **Prometheus / Grafana** for metrics and monitoring
- **EFK stack (Fluent Bit, Elasticsearch, Kibana)** for centralized logging

---

## Configuration

The application configuration is fully separated from the implementation and is provided via multiple sources:

1. **Kubernetes ConfigMap**
   - Non-sensitive configuration injected as environment variables and as a mounted configuration file.
2. **Kubernetes Secrets**
   - Sensitive values such as database credentials, JWT secrets, and API keys.
3. **Configuration file**
   - `config.yaml` mounted into the container at:
     ```
     /app/config/config.yaml
     ```

All configuration values are parametrized via Helm `values.yaml` files.

---

## Environment Variables

| Variable                 | Description                    | Required |
| ------------------------ | ------------------------------ | -------- |
| DATABASE_URL             | PostgreSQL connection string   | yes      |
| JWT_SECRET               | JWT signing secret             | yes      |
| JWT_ALGORITHM            | JWT algorithm (default: HS256) | no       |
| ELASTICSEARCH_HOST       | Elasticsearch endpoint         | yes      |
| ELASTICSEARCH_USER       | Elasticsearch user             | no       |
| ELASTICSEARCH_PASSWORD   | Elasticsearch password         | yes      |
| USER_SERVICE_URL         | User service base URL          | yes      |
| NINJAS_NUTRITION_API_KEY | API Ninjas nutrition key       | optional |

---

## Local development

- Configuration via `.env` file (see `.env.example`)
- API available at: `http://localhost:8001`
- PostgreSQL exposed on: `localhost:5433`

1. docker network create personalcook-net
2. copy .env.example .env
3. docker compose up --build

---

## Kubernetes

- Configuration via Helm values, ConfigMaps, and Secrets
- API exposed through reverse proxy: http://134.112.128.83/api/recipe/
- Media stored on a PersistentVolumeClaim

Separate Helm values files are used:

- `values-dev.yaml`
- `values-prod.yaml`

Example deployments:
helm upgrade --install recipe-service-prod . -n personalcook -f values-prod.yaml

---

## Observability & Logging

The Recipe Service is integrates with a centralized logging and monitoring stack.

### Logging (EFK stack)

Application logs are written to stdout and collected at the Kubernetes level using:

- **Fluent Bit** – log collection and forwarding
- **Elasticsearch** – centralized log storage and indexing
- **Kibana** – log visualization and analysis

### Metrics & Monitoring

The service exposes Prometheus-compatible metrics at: /metrics

Metrics are scraped using:

- **Prometheus Operator** via a `ServiceMonitor`
- Visualized in **Grafana**

#### Exposed metrics

- **`http_requests_total`** _(Counter)_  
  Total number of HTTP requests.  
  **Labels:** `method`, `endpoint`, `status_code`

- **`http_request_errors_total`** _(Counter)_  
  Total number of failed HTTP requests (error responses).  
  **Labels:** `method`, `endpoint`, `status_code`

- **`http_request_latency_seconds`** _(Histogram)_  
  HTTP request latency distribution (seconds).  
  **Labels:** `method`, `endpoint`

- **`http_requests_in_progress`** _(Gauge)_  
  Number of HTTP requests currently being processed.

- **`created_recipes_total`** _(Counter)_  
  Total number of created recipes.  
  **Labels:** `source` (e.g., `api`, `import`)

- **`nutrition_analyses_total`** _(Counter)_  
  Total number of nutrition analyses.  
  **Labels:** `source`, `status` (e.g., `success`, `error`)

---

## Dependencies

- user service at USER_SERVICE_URL (default http://user_service:8000)
- Elasticsearch at ELASTICSEARCH_HOST (default http://elasticsearch:9200)

---

## API Docs

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI JSON: http://localhost:8001/openapi.json

---

## Testing

Run tests locally:

```
pytest
```

---

## CI

This repo runs two GitHub Actions jobs:

- `test`: installs requirements and runs `pytest`
- `container`: builds the Docker image, runs the container, and hits `/` for a smoke test

Tests (files and intent):

- `tests/test_auth.py`: JWT decode and auth helper behavior (valid, expired, invalid tokens).
- `tests/test_recipes_router.py`: recipes CRUD and filters, including validation of bad ingredients.
- `tests/test_storage.py`: image upload storage writes and filename normalization.
- `tests/test_user_client.py`: user-service client responses and error handling via mocked HTTP.

---

## Troubleshooting

- `NINJAS_NUTRITION_API_KEY` missing: `/nutrition` requests will fail.
- Elasticsearch connection errors: verify `ELASTICSEARCH_HOST` and ES container status.
- JWT errors: verify `JWT_SECRET` and `JWT_ALGORITHM`.
