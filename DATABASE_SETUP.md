# Database Setup (Docker-first)

This project is configured to use Docker for the database and application runtime. There is a single source of truth for environment variables: **`.env`** at the repository root.

## Where env variables come from

- The root `.env` file is referenced by docker-compose for all services (`db`, `backend`, `frontend`).
- The backend uses the `DATABASE_URL` from the environment; the Postgres image uses `POSTGRES_*` variables from the same file.

Example (already provided in `.env`):

```
DATABASE_URL=postgresql+asyncpg://appuser:DB7x9Kp2RqLm4N8sTvW3yZ5@db:5432/schedule_db
POSTGRES_USER=appuser
POSTGRES_PASSWORD=DB7x9Kp2RqLm4N8sTvW3yZ5
POSTGRES_DB=schedule_db
```

## Run

From the repository root:

```powershell
docker-compose up --build -d
```

Services:
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432 (inside Docker network as `db:5432`)

## Notes

- Local, non-Docker database modes and extra env files were removed. Use Docker and edit the root `.env` file when you need to change credentials or other server settings.
- The healthcheck uses the `POSTGRES_*` variables from `.env`.
