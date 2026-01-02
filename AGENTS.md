# Repository Guidelines

## Project Structure & Module Organization
- `main.py` is the FastAPI application entrypoint and middleware wiring.
- `api/v1/` contains versioned route modules (admin, agent, jobs, logs, etc.).
- `schemas/` defines Pydantic request/response models and shared enums/utilities.
- `repositories/` holds data-access logic for MongoDB/Redis.
- `services/` contains business logic; `security/` contains auth, hashing, and token helpers.
- `core/` hosts infrastructure pieces like database and scheduler setup.
- `celery_worker.py` defines the Celery app and tasks.
- `email_templates/` stores outbound email templates.
- `docker-compose.yml` and `Dockerfile` describe the containerized stack.

## Build, Test, and Development Commands
- `python -m uvicorn main:app --reload` runs the API locally with auto-reload.
- `docker compose up -d --build` starts the full stack (API, worker, Mongo, Redis, Flower).
- `docker compose logs -f web` tails API logs during local debugging.
- `celery -A celery_worker worker -l info --pool=custom --concurrency=5` runs a worker when not using Docker.

## Coding Style & Naming Conventions
- Use 4-space indentation and follow the existing PEP8-style patterns.
- Module and function names are `snake_case`; classes are `PascalCase`; constants use `UPPER_SNAKE_CASE`.
- Pydantic schemas in `schemas/` follow the `*Base`, `*Create`, `*Update`, `*Out` pattern (e.g., `UserBase`, `UserCreate`).
- Keep route modules under `api/v1/` and group endpoints by domain.

## Testing Guidelines
- No automated test suite is present; `test.py` is empty.
- If you add tests, place them under `tests/` and use a `test_*.py` naming convention; document how to run them here.

## Commit & Pull Request Guidelines
- Recent commits use short messages like `automated commit`. If you adopt a different format, align with maintainers first.
- PRs should include a concise summary, linked issue (if any), and a note on any API or schema changes.

## Security & Configuration Notes
- Configure services via env vars used in `docker-compose.yml` (e.g., `MONGO_URL`, `DB_NAME`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`).
- Store secrets in a local `.env` and do not commit credentials to the repo.
