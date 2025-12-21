CI overview

This repo runs two GitHub Actions jobs:
- test: installs requirements and runs `pytest`
- container: builds the Docker image, runs the container, and hits `/` for a smoke test

Tests (files and intent):
- `tests/test_auth.py`: JWT decode and auth helper behavior (valid, expired, invalid tokens).
- `tests/test_recipes_router.py`: recipes CRUD and filters, including validation of bad ingredients.
- `tests/test_storage.py`: image upload storage writes and filename normalization.
- `tests/test_user_client.py`: user-service client responses and error handling via mocked HTTP.
