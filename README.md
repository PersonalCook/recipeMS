# recipeMS

Recipe service for PersonalCook.

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
