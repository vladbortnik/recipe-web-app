# AGENTS.md — Recipe Hub

## Stack
- Python 3.12 / Flask 3.0 / SQLAlchemy + Flask-Migrate / PostgreSQL 16
- Single-package app (`app/`) — no monorepo, no frontend build step
- Templates are Jinja2 server-rendered; no JS framework, no npm

## Running locally

All development runs through Docker Compose. Direct `python run.py` works only if a local PostgreSQL is running and `.env` has `DB_HOST` pointing to it.

```bash
# Start (builds image, runs migrations, starts gunicorn on :5002)
docker compose up --build -d

# Logs
docker compose logs -f web1

# Stop
docker compose down
```

The app is reachable at `http://localhost:5002` only. Ports 5003/5004 in the README refer to a multi-instance production setup — `compose.yaml` only defines `web1`.

## Environment

- `.env` is required and is **not** committed (it is gitignored).
- Copy `.env-example` to `.env` and fill in all keys before first run.
- `DB_HOST=db` — this hostname only resolves inside Docker. For bare-metal dev, change to `localhost`.
- `GOOGLE_REDIRECT_URI` in `.env` is set to the production URL. Override it for local OAuth testing: `http://localhost:5002/auth/google/callback`.
- `SESSION_COOKIE_SECURE` and `WTF_CSRF_SSL_STRICT` are `True` when `FLASK_DEBUG=False` (the default). CSRF will reject non-HTTPS requests in production mode. Set `FLASK_DEBUG=True` in `.env` for local HTTP development.

## Migrations

`scripts/entrypoint.sh` runs automatically on container start:
1. Waits for Postgres (`nc -z $DB_HOST $DB_PORT`)
2. `flask db init` (only if `migrations/` does not exist)
3. `flask db migrate -m "Auto migration"`
4. `flask db upgrade head`

The `migrations/` directory is **gitignored** — it is regenerated on each fresh container start. Do not commit it.

To run migrations manually inside a running container:
```bash
docker exec -it recipe-web-app-web1-1 /bin/bash
flask db migrate -m "description"
flask db upgrade head
```

## App entrypoint

- `run.py` — module-level code runs under Gunicorn too (calls `create_app()` and `db.create_all()`). Only the `if __name__ == "__main__": app.run(...)` block is skipped by Gunicorn.
- Do **not** change the `host`, `port`, or `debug` values in `run.py` directly — control them via `.env`.
- App factory is `app/__init__.py:create_app()`.

## Key files
| File | Purpose |
|---|---|
| `app/routes.py` | All routes — single file, no blueprints |
| `app/models.py` | `User`, `ImgSet`, `Recipe`, `Favorite` |
| `app/utils.py` | Azure Vision, Spoonacular, email, token helpers |
| `app/config.py` | All config from env vars; security flags derive from `DEBUG` |
| `app/static/whitelist.txt` | 99 grocery item names; Azure Vision results are filtered against this |
| `app/static/upload_dir/` | User-uploaded images; gitignored except `.gitkeep` |

## No test suite

There are no tests. No `pytest`, no CI. Verification is manual via the running app.

## External API dependencies

Features that require live credentials (will silently fail or error without them):
- **Image upload → ingredient recognition**: Azure Computer Vision (`AZURE_COMPUTERVISION_KEY` + `AZURE_COMPUTERVISION_ENDPOINT`)
- **Recipe search**: Spoonacular (`SPOONACULAR_API_KEY`)
- **Google OAuth**: `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`
- **Email (verification, password reset)**: `MAIL_*` vars (Fastmail SMTP by default)
- **reCAPTCHA**: required on login/signup/password-reset forms — use test keys for local dev

## Deployment

Production runs 3 Gunicorn instances behind an external Nginx (not in `compose.yaml`). The `compose.yaml` in repo only defines one instance (`web1`). Multi-instance configs are in `docker-compose-examples/`.
