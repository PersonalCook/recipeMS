# recipeMS

Recipe service for PersonalCook.

This microservice manages recipes for PersonalCook.
It exposes a REST API for creating, updating, searching and retrieving recipes. It also provides nutritional infomation via API Ninjas (https://api-ninjas.com).

## Local dev

1. docker network create personalcook-net
2. copy .env.example .env
3. docker compose up --build

## Dependencies

- user service at USER_SERVICE_URL (default http://user_service:8000)
- Elasticsearch at ELASTICSEARCH_HOST (default http://elasticsearch:9200)

## Ports

- API: 8001
- Postgres: 5433
